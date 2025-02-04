import { openai } from "@ai-sdk/openai";
import { streamText, createDataStreamResponse } from "ai";
import { createChat, createMessages } from "@/lib/queries";
import { Message } from "ai";
import { NextResponse } from "next/server";

// Gestion de la route API POST pour les conversations avec l'IA
export async function POST(req: Request) {
  const { messages, id: chatId } = await req.json();
  
  return createDataStreamResponse({
    async execute(dataStream) {
      if (!chatId) {
        throw new Error("❌ Erreur: chatId est undefined !");
      }

      // On récupère uniquement le dernier message de l'utilisateur
      const lastUserMessage = [...messages].reverse().find((m: Message) => m.role === 'user');
      
      if (!lastUserMessage) {
        throw new Error("❌ Erreur: Aucun message utilisateur trouvé !");
      }

      dataStream.writeData({ chatId, chats: { id: chatId } });
      console.log("✅ Chat ID et métadonnées envoyés au client:", { chatId, chats: { id: chatId } });

      // Génération de la réponse IA
      const result = await streamText({
        model: openai("gpt-4o-mini"),
        messages,
        system: "Tu es un assistant pour la F1.",
        onFinish: async (result) => {
          // Sauvegarde des messages une fois le stream terminé
          await createMessages(chatId, lastUserMessage.content as unknown as JSON, 'user');
          await createMessages(chatId, result.text as unknown as JSON, 'assistant');
        }
      });

      await result.mergeIntoDataStream(dataStream);
    },

    // Gestion des erreurs pendant le streaming
    onError: (error) => error instanceof Error ? error.message : String(error),
  });
}
