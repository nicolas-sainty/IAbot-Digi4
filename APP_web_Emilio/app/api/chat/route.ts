import { openai } from "@ai-sdk/openai";
import { streamText, createDataStreamResponse } from "ai";
import { getStoredResponse, createMessages } from "@/lib/queries";
import { Message } from "ai";
import { NextResponse } from "next/server";

// 📌 **Gestion de la route API POST**
export async function POST(req: Request) {
  const { messages, id: chatId } = await req.json();

  return createDataStreamResponse({
    async execute(dataStream) {
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

      dataStream.writeData({ chatId, chats: { id: chatId } });
      console.log("✅ Chat ID et métadonnées envoyés au client:", { chatId, chats: { id: chatId } });

      // 🔹 **Cherche une réponse stockée en base**
      const storedResponse = await getStoredResponse(chatId, lastUserMessage.content);

      // ✅ **Si une réponse stockée existe → Ajoute-la au contexte !**
      let finalMessages = [...messages];
      if (storedResponse) {
        console.log("✅ Réponse stockée trouvée ! Ajoutée au contexte IA.");
        finalMessages.push({
          role: "assistant",
          content: storedResponse,
        });
      } else {
        console.log("❌ Aucune réponse stockée trouvée, GPT va générer une réponse.");
      }

      // 🔹 **Génération de la réponse IA**
      const result = await streamText({
        model: openai("gpt-4o-mini"),
        messages: finalMessages,
        system: "Tu es un assistant pour la F1. Ne réponds qu'aux questions sur la F1. Et finis tes phrases par : Vroum Vroum ! 🏎️",
        onFinish: async (result) => {
          // ✅ **Sauvegarde des messages après génération**
          await createMessages(chatId, lastUserMessage.content as unknown as JSON, "user");
          await createMessages(chatId, result.text as unknown as JSON, "assistant");
          console.log("✅ Résultat stocké dans Supabase:", result.text);
        },
      });

      console.log("✅ Réponse finale envoyée au client:", result);
      await result.mergeIntoDataStream(dataStream);
    },

    // ✅ **Gestion des erreurs**
    onError: (error) => (error instanceof Error ? error.message : String(error)),
  });
}
