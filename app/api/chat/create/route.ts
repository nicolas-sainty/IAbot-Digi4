import { createChat } from "@/lib/queries";
import { NextResponse } from "next/server";

export async function POST(req: Request) {
    const { title } = await req.json();
    const chats = await createChat(title || "Nouvelle conversation");
    console.log(chats);
    return NextResponse.json(chats);
}