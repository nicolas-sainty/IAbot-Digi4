"use client"

import Link from 'next/link'
import { ArrowUp } from 'lucide-react'
import Image from 'next/image'
import { useState } from 'react'
import { useChat } from 'ai/react'
import { mutate } from 'swr'

export default function Home() {
  const { messages, input, handleInputChange, handleSubmit } = useChat({
    api: '/api/chat',
    onFinish: (message) => {
      console.log(message);
      mutate('/api/chat/getAll');
    }
  });

  const [hasSentMessage, setHasSentMessage] = useState(false);

  const handleSendMessage = (e: React.FormEvent) => {
    setHasSentMessage(true);
    handleSubmit(e);
  };

  return (
    <main className={`flex min-h-screen w-full flex-col items-center relative px-4 sm:px-6 md:px-8 ${hasSentMessage ? 'justify-end' : 'justify-center'}`}>
      {/* Afficher le titre uniquement si aucun message n'a été envoyé */}
      {!hasSentMessage && (
        <h1 className={`text-xl font-semibold text-center mb-6 text-black`}>
          Bonjour, je suis Emilio !<br />
          En quoi pourrais-je vous aider sur la Formule 1 ?
        </h1>
      )}
    
      {/* Conteneur de la conversation */}
      <div className="w-full max-w-[665px] flex flex-col items-center">
        {messages.map((message) => (
          <div 
            key={message.id} 
            className={`flex w-full mb-4 ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div className={`max-w-[80%] p-4 rounded-2xl ${
              message.role === 'user' 
                ? 'bg-[#DC2625] text-white rounded-tr-sm' 
                : 'bg-[#F1F1F1] rounded-tl-sm'
            }`}>
              <div className="whitespace-pre-wrap">
                {message.content}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="w-full max-w-[665px] mb-[4vh]">
        <form onSubmit={handleSendMessage} className="relative">
          <textarea 
            className="w-full py-4 px-6 pr-16 min-h-[110px] max-h-[75vh] overflow-y-hidden border-0 rounded-[24px] focus:outline-none focus:ring-0 bg-[#F1F1F1] resize-none"
            placeholder="Posez votre question ici..."
            style={{ scrollbarWidth: 'auto', scrollbarColor: 'auto' }}
            value={input}
            onChange={handleInputChange}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage(e);
              }
            }}
          />
          <button 
            className="absolute bottom-4 right-4 w-10 h-10 rounded-full flex items-center justify-center bg-[#DC2625] hover:bg-[#DC2625]/90 transition-colors"
            type="submit"
          >
            <ArrowUp className="w-6 h-6 text-white" />
          </button>
        </form>
      </div>
    </main>
  );
}
