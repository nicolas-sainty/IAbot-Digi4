'use client';

import { useEffect, useState } from "react";
import Image from "next/image";
import { ArrowUp } from "lucide-react";

interface Message {
  id: string;
  content: string;
  created_at: string;
  role: 'user' | 'assistant';
}

interface ChatProps {
  chatId: string;
}

const ChatPage = ({ chatId }: ChatProps) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const getMessages = async () => {
      const fetchedMessages = await fetchMessages(chatId);
      setMessages(fetchedMessages);
      setIsLoading(false);
    };

    getMessages();
  }, [chatId]);

  if (isLoading) {
    return <div className="w-full text-center p-8">Chargement de l'historique...</div>;
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
        <form className="relative">
          <textarea
            className="w-full py-4 px-6 pr-16 min-h-[110px] max-h-[75vh] overflow-y-hidden border-0 rounded-[24px] focus:outline-none focus:ring-0 bg-[#F1F1F1] resize-none"
            placeholder="Posez votre question ici..."
            style={{ scrollbarWidth: 'auto', scrollbarColor: 'auto' }}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                // handleSubmit function should be defined elsewhere
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
