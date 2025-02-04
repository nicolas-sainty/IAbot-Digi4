'use client';

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import  Chat from "@/app/components/chat";

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
}

export default function ChatPage() {
  const { id } = useParams();
  const [initialMessages, setInitialMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchMessages = async () => {
      const response = await fetch(`/api/messages/${id}`);
      const data = await response.json();
      setInitialMessages(data.messages.map((msg: any) => ({
        id: msg.id,
        content: msg.content,
        role: msg.role
      })));
      setIsLoading(false);
    };
    fetchMessages();
  }, [id]);

  return <Chat id={id as string} initialMessages={initialMessages} />;
}