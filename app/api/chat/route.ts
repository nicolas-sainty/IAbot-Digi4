import { openai } from "@ai-sdk/openai";
import { streamText } from "ai";
import { createChat, getChats } from "@/lib/queries";

export async function POST(req: Request) { 
    const { messages } = await req.json();
    const result = await streamText({
        model: openai("gpt-4o-mini"),
        messages,
        system: "You are a helpful assistant.",
        onChunk: (chunk) => {
            console.log("chunk", chunk);
        }
    });
    for await (const textPart of result.textStream) {
        console.log(textPart);
      }

    const chats = await createChat("Chat 1");
    console.log(chats);
    console.log(result);
    console.log(result.toDataStreamResponse());
    return result.toDataStreamResponse();
}

// Générer un titre avec les premiers mots du message de l'utilisateur