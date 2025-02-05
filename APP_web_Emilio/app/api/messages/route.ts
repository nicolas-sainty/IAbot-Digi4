import { getMessages } from "@/lib/queries";
import { NextResponse } from "next/server";

export async function POST(req: Request) { 
    const { id } = await req.json();
    const messages = await getMessages(id);
    console.log(messages);
    return NextResponse.json(messages);
}