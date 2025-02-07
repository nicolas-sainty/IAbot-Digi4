// Indique que ce composant doit être exécuté côté client (navigateur) et non côté serveur
"use client"
 
// Import des icônes et des fonctionnalités nécessaires
import { Menu, Plus, Aperture, Flag, ChartNoAxesCombined } from 'lucide-react'      // Menu = icône hamburger, Plus = icône +
import { useEffect, useState } from 'react'     // Hooks React pour gérer l'état et les effets
import { useRouter } from 'next/navigation'     // Pour la navigation entre les pages
 
// Définition du composant principal
// Il reçoit children comme prop (ce qui sera affiché à l'intérieur du layout)
export default function ClientLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // Création des états (variables qui peuvent changer et mettre à jour l'interface)
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);  // État pour la barre latérale (ouverte/fermée)
  const [chats, setChats] = useState([]);                    // État pour stocker la liste des chats
  const router = useRouter();                                // Pour gérer la navigation
 
  // useEffect s'exécute quand le composant est monté (au chargement)
  useEffect(() => {
    // Récupère tous les chats depuis l'API
    const fetchChats = fetch('/api/chat/getAll')
      .then(response => response.json())           // Convertit la réponse en JSON
      .then(data => setChats(data))               // Met à jour l'état avec les données
      .catch(error => console.error('Error fetching chats:', error));  // Gère les erreurs
  }, []);  // [] signifie que ça ne s'exécute qu'une fois au chargement
 
  return (
    // Conteneur principal avec espacement (padding) et écart (gap)
    <div className="flex p-4 gap-4">
      {/* Barre latérale */}
      <div className={`${isSidebarOpen ? 'w-64' : 'w-0'} transition-all duration-300 overflow-hidden`}>
        {/* Contenu de la barre latérale avec fond sombre */}
        <div className="w-64 bg-[#1A1A24] text-white flex flex-col h-[96vh] rounded-2xl shadow-sm">
          {/* Bouton pour ouvrir/fermer la barre latérale */}
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className={`absolute top-6 left-6 p-1.5 rounded-lg transition-colors ${
              isSidebarOpen
                ? 'hover:bg-gray-700 text-white'
                : 'text-[rgb(26,26,36)] hover:bg-gray-100'
            }`}
          >
            <Menu className="w-6 h-6" />
          </button>
 
          {/* Bouton "Nouveau Chat" avec fond rouge */}
          <div className="pt-[80px] px-4">
            <button
              className="w-full flex items-center justify-center gap-[4px] rounded-xl bg-[#DC2625] p-3 hover:bg-red-700 transition-colors text-white"
              onClick={() => router.push('/')}
            >
              <Plus className="w-4 h-4" />
              <span className="text-[14px] font-medium">Nouvelle conversation</span>
            </button>
          </div>
 
          {/* Liste des conversations */}
          <div className="flex-1 overflow-y-auto mt-4 mx-3.5 space-y-1">
  {[...chats].reverse().map((chat: any) => (
    <div key={chat.id}>
      <button
        onClick={() => router.push(`/chat/${chat.id}`)}
        className="w-full flex items-center rounded-lg p-2 text-[13px] hover:bg-gray-800 transition-colors"
        style={{
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
        }}
      >
        <span>{chat.title}</span>
      </button>
    </div>
  ))}
</div>
 
          {/* Categories en bas */}
          <div className="mt-auto border-t border-gray-700 pt-4 pb-[18px] space-y-1 mx-3.5">
            <button
              className="w-full flex items-center gap-2 rounded-lg p-3 text-[14px] hover:bg-gray-800 transition-colors"
              onClick={() => router.push("/chat/general")}
            >
              <Aperture className="w-5 h-5 text-white"/> Général
            </button>
            <button
              className="w-full flex items-center gap-2 rounded-lg p-3 text-[14px] hover:bg-gray-800 transition-colors"
              onClick={() => router.push("/chat/courses")}
            >
              <Flag className="w-5 h-5 text-white"/> Dernières courses
            </button>
            <button
              className="w-full flex items-center gap-2 rounded-lg p-3 text-[14px] hover:bg-gray-800 transition-colors"
              onClick={() => router.push("/chat/statistiques")}
            >
              <ChartNoAxesCombined className="w-5 h-5 text-white"/> Statistiques
            </button>
          </div>
 
        </div>
      </div>
 
      {/* Zone principale de contenu */}
      <div className="flex-1">
        <div className="ml-[40px]">
          {children}  {/* Affiche le contenu passé au composant */}
        </div>
      </div>
    </div>
  );
}
