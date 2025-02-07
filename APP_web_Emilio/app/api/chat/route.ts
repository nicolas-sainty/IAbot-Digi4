import { streamText, createDataStreamResponse } from "ai";
import { getStoredResponse, createMessages } from "@/lib/queries";
import { Message } from "ai";
import { NextResponse } from "next/server";

// 📌 **Gestion de la route API POST**
export async function POST(req: Request) {
  try {
    const { messages, id: chatId } = await req.json();

    if (!chatId) {
      throw new Error("❌ Erreur: chatId est undefined !");
    }
    if (!messages) {
      throw new Error("❌ Erreur: messages est undefined !");
    }

    // 🔹 **Récupération du dernier message utilisateur**
    const lastUserMessage = [...messages].reverse().find((m: Message) => m.role === "user");

    if (!lastUserMessage) {
      throw new Error("❌ Erreur: Aucun message utilisateur trouvé !");
    }

    return createDataStreamResponse({
      async execute(dataStream) {
        dataStream.writeData({ chatId });
        console.log("✅ Chat ID envoyé au client:", { chatId });

        // 🔹 **Sauvegarde immédiate du message utilisateur**
        await createMessages(chatId, lastUserMessage.content as unknown as JSON, "user");

        // 🔹 **Récupération de la réponse stockée en base**
        const storedResponse = await getStoredResponse(chatId, lastUserMessage.content);

        if (storedResponse) {
          console.log("✅ Réponse trouvée en base:", storedResponse);

          // **Stream de la réponse stockée immédiatement**
          await streamText({
            text: storedResponse,
            onToken: (token) => dataStream.writeData({ token }),
            onFinish: async () => {
              // **Sauvegarde de la réponse en base**
              await createMessages(chatId, storedResponse, "assistant");
              console.log("✅ Réponse enregistrée dans Supabase.");
            },
          });
        } else {
          console.log("❌ Aucune réponse stockée. Message temporaire envoyé.");

          // **Stream d'un message temporaire**
          await streamText({
            text: "⏳ Je recherche une réponse...",
            onToken: (token) => dataStream.writeData({ token }),
          });
        }
      },

      // ✅ Gestion des erreurs
      onError: (error) => (error instanceof Error ? error.message : String(error)),
    });
  } catch (error) {
    console.error("❌ Erreur dans chat.route.ts :", error);
    return NextResponse.json({ error: error.message || "Erreur inconnue" }, { status: 500 });
  }
}
