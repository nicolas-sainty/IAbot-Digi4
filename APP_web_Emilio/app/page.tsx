"use client"

import Link from 'next/link'
import { ArrowUp } from 'lucide-react'
import Image from 'next/image'
import { useState } from 'react'
import { useChat } from 'ai/react'
import { mutate } from 'swr'
import { useRouter } from 'next/navigation'
import Chat from '@/app/components/chat'

interface ChatMessage {
  id: string;
  content: string;
  role: string;
}

export default function Home() {
  return (
    <main className="flex min-h-screen w-full flex-col items-center justify-end bg-[#FFF] relative">
      <Chat />
    </main>
  )
}