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
      try {
        const response = await fetch(`/api/messages`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ id }),
        });
        const data = await response.json();
        console.log("data dans ChatPage.tsx", data);
        
        // Vérification que data est un tableau avant de faire le mapping
        if (Array.isArray(data)) {
          setInitialMessages(data.map((msg: any) => ({
            id: msg.chat_id || msg.id, // Fallback au cas où chat_id n'existe pas
            content: msg.content,
            role: msg.role
          })));
        } else if (data.messages && Array.isArray(data.messages)) {
          setInitialMessages(data.messages.map((msg: any) => ({
            id: msg.chat_id || msg.id,
            content: msg.content,
            role: msg.role
          })));
        }
        setIsLoading(false);
      } catch (error) {
        console.error("Erreur lors de la récupération des messages:", error);
        setIsLoading(false);
      }
    };
    
    if (id) {
      fetchMessages();
    }
  }, [id]);

  return <Chat chatIdFromProps={id as string} initialMessages={initialMessages} />;
}