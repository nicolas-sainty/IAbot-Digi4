import { getChats } from "@/lib/queries";
import { NextResponse } from "next/server";

export async function GET(req: Request) { 
    const chats = await getChats();
    console.log("chats dans getAll route", chats);
    return NextResponse.json(chats);
}