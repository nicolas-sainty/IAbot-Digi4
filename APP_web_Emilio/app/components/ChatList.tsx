// Import du hook useRouter de Next.js qui permet de gérer la navigation entre les pages
import { useRouter } from 'next/navigation';
 
// Définition du composant ChatList qui reçoit une prop 'chats' de type tableau
// Le {chats}: {chats: any[]} est une façon de dire que ce composant attend une liste de chats
export function ChatList({ chats }: { chats: any[] }) {
  // Initialisation du router pour pouvoir naviguer entre les pages
  const router = useRouter();
 
  // Fonction qui sera appelée quand on clique sur un chat
  // Elle prend un paramètre chatId qui est l'identifiant unique du chat
  const handleChatClick = (chatId: string) => {
    // Affiche dans la console l'ID du chat sur lequel on a cliqué (utile pour le débogage)
    console.log("Clicking chat with ID:", chatId);
    // Redirige l'utilisateur vers la page du chat sélectionné
    router.push(`/chat/${chatId}`);
  };
 
  // Ces console.log sont utilisés pour le débogage
  // Ils affichent différentes informations sur les chats dans la console
  console.log("Chat IDs:", chats.map((chat) => chat.id));
  console.log(chats.map((chat) => chat.title));
  console.log(chats.map((chat) => chat.messages));
  console.log(chats.map((chat) => chat.messages.map((messages: any) => messages.content)));
 
  // Le rendu du composant
  return (
    // Div conteneur principal
    <div>
      {/* On utilise .map pour créer un élément div pour chaque chat dans la liste */}
      {chats.map((chat) => (
        <div
          // key est nécessaire pour React quand on fait une liste d'éléments
          key={chat.id}
          // Quand on clique sur un chat, on appelle handleChatClick avec l'ID du chat
          onClick={() => handleChatClick(chat.id)}
          // Classes CSS pour le style :
          // cursor-pointer : change le curseur en pointeur quand on survole
          // hover:bg-gray-100 : change la couleur de fond en gris clair au survol
          // p-4 : ajoute un padding de 4 unités
          className="cursor-pointer hover:bg-gray-100 p-4"
        >
          {/* Affiche le titre du chat */}
          {chat.title}
        </div>
      ))}
    </div>
  );
}
