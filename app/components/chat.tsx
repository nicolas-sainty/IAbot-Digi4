'use client';

import { useEffect, useState } from "react";
import Image from "next/image";
import { ArrowUp } from "lucide-react";
import { Message, useChat } from 'ai/react';
import { useRouter } from 'next/navigation';
import { useChatContext } from '@/app/context/ChatContext';

interface ChatProps {
  chatIdFromProps?: string | null;
  url?: string;
  initialMessages?: Message[];
}

const ChatPage = ({ chatIdFromProps = null, url = '/api/chat', initialMessages = [] }: ChatProps) => {
  const router = useRouter();
  const [chatId, setChatId] = useState<string | null>(chatIdFromProps);
  const [isLoading, setIsLoading] = useState(true);
  const { pendingMessage, setPendingMessage } = useChatContext();
  
  console.log("chatId dans Chat.tsx", chatId)
  console.log("initialMessages dans Chat.tsx", initialMessages)

  useEffect(() => {
    if (chatIdFromProps) {
      setChatId(chatIdFromProps);
    }
  }, [chatIdFromProps]);

  const { messages, input, handleInputChange, handleSubmit: handleChatSubmit } = useChat({
    api: url,
    id: chatId || undefined,
    initialMessages: initialMessages,
  });

  useEffect(() => {
    if (initialMessages.length > 0 || messages.length > 0 || chatId) {
      setIsLoading(false);
    }
    if (pendingMessage) {
      handleChatSubmit({ preventDefault: () => {} });
      setPendingMessage('');
    }
  }, [messages, chatId, pendingMessage, initialMessages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!chatId && input.trim()) {
      try {
        // Extraire les premiers mots (maximum 5) pour le titre
        const title = input.trim().split(/\s+/).slice(0, 5).join(' ');
        
        const newChat = await fetch('/api/chat/create', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ title }),
        });
        
        if (!newChat.ok) {
          throw new Error(`HTTP error! status: ${newChat.status}`);
        }
        const newChatData = await newChat.json();
        console.log("newChatData dans Chat.tsx", newChatData);
        const currentInput = input;
        setPendingMessage(currentInput);
        window.history.replaceState({}, '', `/chat/${newChatData.id}`);
        setChatId(newChatData.id);
      } catch (error) {
        console.error("Erreur lors de la création du chat:", error);
        return;
      }
    } else {
      handleChatSubmit(e);
    }
  };

  if (isLoading && chatId) {
    return (
      <div className="w-full h-screen flex items-center justify-center">
        <div className="text-center p-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#FF1E02] mx-auto mb-4"></div>
          <div>Chargement de l'historique...</div>
        </div>
      </div>
    );
  }

  return (
    <main className="flex min-h-screen w-full flex-col items-center justify-end bg-[#FFF] relative">
      <div className="absolute left-0 right-0 top-[45%] -translate-y-1/2 flex items-center justify-center pointer-events-none transition-all duration-300">
        <Image
          src="/Images/F1.svg.png"
          alt="F1 Logo"
          width={400}
          height={400}
          className="opacity-30 transition-transform duration-300"
          priority
        />
      </div>

      <div className="w-[665px]">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex w-full mb-4 ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-[80%] p-4 rounded-2xl ${
                message.role === 'user'
                  ? 'bg-[#FF1E02] text-white rounded-tr-sm'
                  : 'bg-[#F1F1F1] rounded-tl-sm'
              }`}
            >
              <div className="whitespace-pre-wrap">{message.content}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="w-[665px] mb-[4vh]">
        <form onSubmit={handleSubmit} className="relative">
          <textarea
            className="w-full py-4 px-6 pr-16 min-h-[110px] max-h-[75vh] overflow-y-hidden border-0 rounded-[24px] focus:outline-none focus:ring-0 bg-[#F1F1F1] resize-none"
            placeholder="Posez votre question ici..."
            style={{ scrollbarWidth: 'auto', scrollbarColor: 'auto' }}
            value={input}
            onChange={handleInputChange}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
          />
          <button
            className="absolute bottom-4 right-4 w-10 h-10 rounded-full flex items-center justify-center bg-[#FF1E02] hover:bg-[#FF1E02]/90 transition-colors"
            type="submit"
          >
            <ArrowUp className="w-6 h-6 text-white" />
          </button>
        </form>
      </div>
    </main>
  );
};

export default ChatPage;
