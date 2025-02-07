// Indique que ce composant s'exécute côté client et non côté serveur
"use client"
 
// Import des composants et fonctionnalités nécessaires
import Link from 'next/link'                // Pour créer des liens de navigation
import { ArrowUp } from 'lucide-react'      // Icône de flèche vers le haut
import Image from 'next/image'              // Composant optimisé pour les images
import { useState } from 'react'            // Hook React pour gérer l'état
import { useChat } from 'ai/react'          // Hook pour gérer le chat AI
import { mutate } from 'swr'                // Utilitaire pour mettre à jour les données
import { useRouter } from 'next/navigation'  // Hook pour la navigation
import Chat from '@/app/components/chat'     // Notre composant Chat personnalisé
 
// Définition d'une interface TypeScript pour la structure d'un message
interface ChatMessage {
  id: string;      // Identifiant unique du message
  content: string; // Contenu du message
  role: string;    // Rôle de l'expéditeur (user ou assistant)
}
 
// Composant principal de la page d'accueil
export default function Home() {
  return (
    // Conteneur principal avec des classes Tailwind CSS pour le style
    <main className="flex min-h-screen w-full flex-col items-center justify-end bg-[#FFF] relative">
      {/* Affiche le composant Chat */}
      <Chat />
    </main>
  )
}