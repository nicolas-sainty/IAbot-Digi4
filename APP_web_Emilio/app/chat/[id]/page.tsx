// Indique que ce composant s'exécute côté client (dans le navigateur)
'use client';
 
// Import des fonctionnalités nécessaires
import { useParams } from "next/navigation";    // Pour récupérer les paramètres de l'URL
import { useEffect, useState } from "react";    // Hooks React pour gérer l'état et les effets
import Chat from "@/app/components/chat";       // Notre composant Chat personnalisé
 
// Définition d'un type Message pour TypeScript
// Cela décrit la structure que doit avoir un message
interface Message {
  id: string;                        // Identifiant unique du message
  content: string;                   // Contenu du message
  role: 'user' | 'assistant';        // Qui envoie le message (utilisateur ou assistant)
}
 
// Composant principal de la page de chat
export default function ChatPage() {
  // Récupère l'ID du chat depuis l'URL
  const { id } = useParams();
 
  // Création des états (variables qui peuvent changer)
  const [initialMessages, setInitialMessages] = useState<Message[]>([]);  // Liste des messages
  const [isLoading, setIsLoading] = useState(true);                      // État de chargement
 
  // useEffect s'exécute quand le composant est monté ou quand 'id' change
  useEffect(() => {
    // Fonction pour récupérer les messages
    const fetchMessages = async () => {
      try {
        // Appel à l'API pour récupérer les messages
        const response = await fetch(`/api/messages`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ id }),  // Envoie l'ID du chat
        });
        
        // Convertit la réponse en JSON
        const data = await response.json();
        console.log("data dans ChatPage.tsx", data);
        
        // Vérifie si data est un tableau
        if (Array.isArray(data)) {
          // Transforme les données en format Message
          setInitialMessages(data.map((msg: any) => ({
            id: msg.chat_id || msg.id,    // Utilise chat_id ou id comme identifiant
            content: msg.content,          // Contenu du message
            role: msg.role                 // Rôle (user ou assistant)
          })));
        }
        // Si data contient un objet messages qui est un tableau
        else if (data.messages && Array.isArray(data.messages)) {
          setInitialMessages(data.messages.map((msg: any) => ({
            id: msg.chat_id || msg.id,
            content: msg.content,
            role: msg.role
          })));
        }
        
        // Désactive l'état de chargement
        setIsLoading(false);
      } catch (error) {
        // En cas d'erreur, affiche l'erreur dans la console
        console.error("Erreur lors de la récupération des messages:", error);
        setIsLoading(false);
      }
    };
    
    // Si on a un ID, on récupère les messages
    if (id) {
      fetchMessages();
    }
  }, [id]);  // Se déclenche quand 'id' change
 
  // Rendu du composant Chat avec les props nécessaires
  return <Chat
    chatIdFromProps={id as string}     // ID du chat
    initialMessages={initialMessages}   // Messages initiaux
  />;
}
 