"use client"

import { Menu, Plus } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

export default function ClientLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [chats, setChats] = useState([]);
  const router = useRouter();

  useEffect(() => {
    const fetchChats = fetch('/api/chat/getAll')
      .then(response => response.json())
      .then(data => setChats(data))
      .catch(error => console.error('Error fetching chats:', error));
  }, []);

  return (
    <div className="flex p-4 gap-4">
      {/* Sidebar Container */}
      <div className={`${isSidebarOpen ? 'w-64' : 'w-0'} transition-all duration-300 overflow-hidden`}>
        {/* Sidebar Content - Largeur fixe */}
        <div className="w-64 bg-[#F9F9F9] text-black flex flex-col h-[96vh] rounded-2xl shadow-sm">
          {/* Toggle Sidebar Button - Moved here */}
          <button 
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="absolute top-6 left-6 p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Menu className="w-5 h-5" />
          </button>

          {/* New Chat Button */}
          <div className="pt-[80px] px-4">
            <button className="w-full flex items-center gap-2 rounded-xl border border-gray-200 p-3 hover:bg-gray-100 transition-colors " onClick={() => router.push('/')}>
              <Plus className="w-4 h-4" />
              <span className="text-sm font-medium">Nouveau Chat</span>
            </button>
          </div>

          {/* Conversations List */}
          <div className="flex-1 overflow-y-auto mt-4">
            {[...chats].reverse().map((chat: any) => (
              <div key={chat.id}>
                <button 
                  onClick={() => router.push(`/chat/${chat.id}`)}
                  className="w-full text-left px-3 py-2 rounded-xl hover:bg-gray-100 transition-colors text-sm"
                >
                  {chat.title} 
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1">
        <div className="ml-[40px]">
          {children}
        </div>
      </div>
    </div>
  );
} 