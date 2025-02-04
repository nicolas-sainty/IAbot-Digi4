"use client";

import { Menu, Plus, Trash2, ChartNoAxesCombined, Flag, Aperture } from "lucide-react";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [chats, setChats] = useState([]);
  const [hoveredChat, setHoveredChat] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchChats = fetch("/api/chat/getAll")
      .then((response) => response.json())
      .then((data) => setChats(data))
      .catch((error) => console.error("Error fetching chats:", error));
  }, []);

  return (
    <div className="flex h-screen ">
      {/* Bouton de menu fixe */}
      {!isSidebarOpen && (
        <button 
          onClick={() => setIsSidebarOpen(true)}
          className="fixed top-9 left-6 p-2 bg-[#DC2625] text-white rounded-lg shadow-lg hover:bg-gray-700 transition-colors z-50"
        >
          <Menu className="w-6 h-6" />
        </button>
      )}
      {/* Sidebar Container */}
      <div className={`${isSidebarOpen ? "w-72" : "w-0"} transition-all duration-300 overflow-hidden h-full left-6`}> 
        <div className="w-72 bg-[#1A1A24] text-white flex flex-col h-full shadow-lg p-4">
          {/* Logo & Toggle Sidebar Button */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2">
              <Image src="/logo_blanc.png" alt="F1-GPT Logo" width={24} height={24} className="w-5 h-5" />
              <span className="text-lg font-bold">F1-BOT</span>
            </div>
            <button 
              onClick={() => setIsSidebarOpen(false)}
              className="p-1.5 hover:bg-gray-700 rounded-lg transition-colors"
            >
              <Menu className="w-6 h-6 text-white" />
            </button>
          </div>

          {/* New Chat Button */}
          <button className="w-[90%] mx-auto flex items-center justify-center gap-2 rounded-lg p-3 bg-[#DC2625] text-white hover:bg-red-700 transition-colors text-md font-medium mb-3">
            <Plus className="w-4 h-5" />
            <span className="text-center">Nouvelle conversation</span>
          </button>

          {/* Conversations List */}
          <div className="flex-1 overflow-y-auto mt-4 space-y-2">
            {chats.map((chat: any) => (
              <div 
                key={chat.id}
                className="relative flex items-center w-full text-left px-4 py-3 rounded-lg hover:bg-gray-800 transition-colors text-sm cursor-pointer"
                onMouseEnter={() => setHoveredChat(chat.id)}
                onMouseLeave={() => setHoveredChat(null)}
              >
                <span className="flex-1 truncate">{chat.title}</span>
                {hoveredChat === chat.id && (
                  <button className="ml-2 text-gray-400 hover:text-white transition-colors">
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            ))}
          </div>

          {/* Categories en bas */}
          <div className="mt-auto border-t border-gray-700 pt-4 space-y-1">
            <button 
              className="w-full flex items-center gap-3 rounded-lg p-2 text-md hover:bg-gray-800 transition-colors"
              onClick={() => router.push("/chat/general")}
            >
              <Aperture className="w-5 h-5 text-white"/> Général
            </button>
            <button 
              className="w-full flex items-center gap-2 rounded-lg p-3 text-md hover:bg-gray-800 transition-colors"
              onClick={() => router.push("/chat/courses")}
            >
              <Flag className="w-5 h-5 text-white" /> Dernières courses
            </button>
            <button 
              className="w-full flex items-center gap-2 rounded-lg p-3 text-md hover:bg-gray-800 transition-colors"
              onClick={() => router.push("/chat/statistiques")}
            >
              <ChartNoAxesCombined className="w-5 h-5 text-white"/> Statistiques
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1">
        <div className="ml-[40px]">{children}</div>
      </div>
    </div>
  );
}
