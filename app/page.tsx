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
  })

  return (
    <main className="flex min-h-screen w-full flex-col items-center justify-end bg-[#FFF] relative">ù
      {/* Logo F1 en arrière-plan */}
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

      {/* Conteneur de la conversation */}
      <div className="w-[665px]">
        {messages.map((message) => (
          <div 
            key={message.id} 
            className={`flex w-full mb-4 ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div className={`max-w-[80%] p-4 rounded-2xl ${
              message.role === 'user' 
                ? 'bg-[#FF1E02] text-white rounded-tr-sm' 
                : 'bg-[#F1F1F1] rounded-tl-sm'
            }`}>
              <div className="whitespace-pre-wrap">
                {message.content}
              </div>
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
  )
}
