'use client';
 
import { useEffect, useState } from "react";
import Image from "next/image";
import { ArrowUp } from "lucide-react";
import { Message, useChat } from 'ai/react';
import { useRouter } from 'next/navigation';
import { useChatContext } from '@/app/context/ChatContext';
import ReactMarkdown from 'react-markdown';
 
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
 
  const suggestedQuestions = [
    "Quels sont les règlements clés de la F1 pour 2024 ?",
    "Qui est le plus grand pilote de F1 de tous les temps ?",
    "Comment fonctionne le DRS en F1 ?",
    "Expliquez-moi les qualifications en F1"
  ];
 
  const handleSuggestedQuestion = (question: string) => {
    if (!chatId) {
      handleInputChange({
        target: { value: question }
      } as React.ChangeEvent<HTMLTextAreaElement>);
    }
  };
 
  return (
    <main className="flex min-h-screen w-full flex-col items-center justify-end bg-[#FFF] relative">
      <div className="absolute left-0 right-0 top-[45%] -translate-y-1/2 flex items-center justify-center pointer-events-none transition-all duration-300 z-0">
        <Image
          src="/Images/EmilioF1.svg"
          alt="F1 Logo"
          width={400}
          height={400}
          className="opacity-30 transition-transform duration-300"
          priority
        />
      </div>
 
      <div className="w-[665px] flex-1 overflow-y-auto max-h-[calc(100vh-180px)] mt-4 relative z-10">
  <div className="flex flex-col space-y-4">
    {messages.map((message) => (
      <div
        key={message.id}
        className={`flex w-full ${
          message.role === 'user' ? 'justify-end' : 'justify-start'
        }`}
      >
        <div
          className={`max-w-[80%] p-4 rounded-2xl ${
            message.role === 'user'
              ? 'bg-[#FF1E02] text-white rounded-tr-none'
              : 'bg-[#F1F1F1] rounded-tl-none'
          } shadow-sm`}
        >
          <div className="whitespace-pre-wrap text-[15px] leading-relaxed">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        </div>
      </div>
    ))}
  </div>
</div>
 
      {!chatId && (
  <div className="absolute top-[35%] -translate-y-1/2 w-[665px] flex flex-col gap-3 z-10">
    <h2 className="text-center text-lg font-medium mb-4 text-[#333]">Questions suggérées 🏎️</h2>
    <div className="grid grid-cols-2 gap-4 mb-12">
      {suggestedQuestions.map((question, index) => (
        <button
          key={index}
          onClick={() => handleSuggestedQuestion(question)}
          className="p-4 text-sm text-left rounded-xl bg-[#FFFF] border border-solid border-[#CCCCCC] hover:bg-[#FF1E00] hover:border-[#FF1E00] hover:text-white transition-all duration-300 ease-in-out transform hover:-translate-y-1"
        >
          {question}
        </button>
      ))}
    </div>
  </div>
)}
 
      <div className={`w-[665px] transition-all duration-500 z-10 ${
        chatId ? 'mb-[4vh]' : 'absolute top-[55%] -translate-y-1/2'
      }`}>
        <form onSubmit={handleSubmit} className="relative">
          <textarea
            className={`w-full py-4 px-6 pr-16 overflow-y-hidden border-0 rounded-[24px] focus:outline-none focus:ring-0 bg-[#F1F1F1] resize-none z-20 ${
              chatId ? 'min-h-[110px]' : 'min-h-[160px]'
            }`}
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