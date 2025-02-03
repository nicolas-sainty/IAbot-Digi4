// Ancienne version  
// import { openai } from "@ai-sdk/openai";
// import { streamText } from "ai";
// import { createChat, getChats } from "@/lib/queries";

// export async function POST(req: Request) { 
//     const { messages } = await req.json();
//     const result = await streamText({
//         model: openai("gpt-4o-mini"),
//         messages,
//         system: "You are a helpful assistant.",
//         onChunk: (chunk) => {
//             console.log("chunk", chunk);
//         }
//     });
//     for await (const textPart of result.textStream) {
//         console.log(textPart);
//       }

//     const chats = await createChat("Chat 1");
//     console.log(chats);
//     console.log(result);
//     console.log(result.toDataStreamResponse());
//     return result.toDataStreamResponse();
// }

// // Générer un titre avec les premiers mots du message de l'utilisateur

import { openai } from "@ai-sdk/openai";
import { streamText, createDataStreamResponse } from "ai";
import { createChat, createMessages } from "@/lib/queries";
import { Message } from "ai";
import { NextResponse } from "next/server";

// Gestion de la route API POST pour les conversations avec l'IA
export async function POST(req: Request) {
  const { messages } = await req.json();

  return createDataStreamResponse({
    async execute(dataStream) {
      const userMessage = messages.find((m: Message) => m.role === 'user')?.content;
      const title = userMessage?.split(' ').slice(0, 5).join(' ') || 'Nouveau chat';

      // Création du chat et stockage en base
      const chats = await createChat(title);
      const chatId = chats.id;
      
      console.log("✅ Chat ID envoyé au client:", chatId);

      // Enregistrement des messages
      for (const message of messages) {
        await createMessages(chats.id, message.content, message.role);
      }

      if (chatId) {
        dataStream.writeData({ chatId, chats });
        console.log("✅ Chat ID et métadonnées envoyés au client:", { chatId, chats });
      } else {
        console.error("❌ Erreur: chatId est undefined !");
      }

      // Génération de la réponse IA
      const result = await streamText({
        model: openai("gpt-4o-mini"),
        messages,
        system: "Tu es un assistant pour la F1.",
      });

      result.mergeIntoDataStream(dataStream);
    },

    // Gestion des erreurs pendant le streaming
    onError: (error) => error instanceof Error ? error.message : String(error),
  });
}
