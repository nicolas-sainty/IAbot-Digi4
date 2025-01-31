"use client"

import { useChat } from 'ai/react'
import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { ArrowUp, ArrowLeft } from 'lucide-react'

export default function ChatPage() {
  const params = useParams()
  const chatId = params.id

  const { messages, input, handleInputChange, handleSubmit } = useChat({
    api: '/api/chat',
    id: chatId as string,
  })

  return (
    <main className="flex min-h-screen w-full flex-col items-center justify-end bg-[#FFF] relative">
      <Link 
        href="/"
        className="absolute top-4 left-4 flex items-center gap-2 text-gray-600 hover:text-gray-900"
      >
        <ArrowLeft className="w-5 h-5" />
        Retour
      </Link>

      {messages.map((message) => (
        <div 
          key={message.id} 
          className={`w-full max-w-[665px] p-4 mb-4 rounded-lg ${
            message.role === 'user' 
              ? 'bg-[#F1F1F1] ml-auto' 
              : 'bg-[#FF1E02]/10'
          }`}
        >
          <div className="font-bold mb-2">
            {message.role === 'user' ? 'Vous' : 'IA F1'}
          </div>
          <div className="whitespace-pre-wrap">
            {message.content}
          </div>
        </div>
      ))}

      <div className="w-full flex flex-col items-center justify-center p-8 mb-[4vh]">
        <div className="w-[665px] relative">
          <form onSubmit={handleSubmit}>
            <textarea 
              className="w-full py-4 px-6 min-h-[110px] max-h-[75vh] overflow-y-hidden border-0 rounded-[24px] focus:outline-none focus:ring-0 bg-[#F1F1F1] resize-none"
              placeholder="Posez votre question ici..."
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
              className="absolute top-4 right-4 w-10 h-10 rounded-full flex items-center justify-center"
              style={{ backgroundColor: 'rgba(255, 30, 2, 0.5)' }}
              type="submit"
            >
              <ArrowUp className="w-6 h-6 text-white" />
            </button>
          </form>
        </div>
      </div>
    </main>
  )
} 