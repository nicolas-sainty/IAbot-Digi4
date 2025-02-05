import { useRouter } from 'next/navigation';

export function ChatList({ chats }: { chats: any[] }) {
  const router = useRouter();

  const handleChatClick = (chatId: string) => {
    console.log("Clicking chat with ID:", chatId);
    router.push(`/chat/${chatId}`);
  };

  console.log("Chat IDs:", chats.map((chat) => chat.id));
  console.log(chats.map((chat) => chat.title));
  console.log(chats.map((chat) => chat.messages));
  console.log(chats.map((chat) => chat.messages.map((messages: any) => messages.content)));
  return (
    <div>
      {chats.map((chat) => (
        <div 
          key={chat.id}
          onClick={() => handleChatClick(chat.id)}
          className="cursor-pointer hover:bg-gray-100 p-4"
        >
          {chat.title}
        </div>
      ))}
    </div>
  );
} 