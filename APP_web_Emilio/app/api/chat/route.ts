import { openai } from "@ai-sdk/openai";
import { streamText, createDataStreamResponse } from "ai";
import { createChat, createMessages } from "@/lib/queries";
import { Message } from "ai";
import { NextResponse } from "next/server";

// Gestion de la route API POST pour les conversations avec l'IA
export async function POST(req: Request) {
  const { messages, id: chatId } = await req.json();

  if (!chatId) {
    throw new Error("❌ Erreur: chatId est undefined !");
  }
  if (!messages) {
    throw new Error("❌ Erreur: messages est undefined !");
  }

  // On récupère uniquement le dernier message utilisateur
  const lastUserMessage = [...messages].reverse().find((m: Message) => m.role === "user");

  if (!lastUserMessage) {
    throw new Error("❌ Erreur: Aucun message utilisateur trouvé !");
  }

  console.log("✅ Chat ID et métadonnées envoyés au client:", { chatId });

  try {
    // 🔹 **Sauvegarde le message utilisateur dans Supabase** 
    await createMessages(chatId, lastUserMessage.content as unknown as JSON, "user");

    // **Ne génère plus de réponse ici** → L'API Python ou Supabase gère cela.
    return NextResponse.json({ chatId, status: "Message utilisateur enregistré" });
  } catch (error) {
    console.error("❌ Erreur lors de l'enregistrement du message utilisateur:", error);
    return NextResponse.json({ error: error.message || "Erreur inconnue" }, { status: 500 });
  }
}

