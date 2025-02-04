"use client";

import { useParams } from 'next/navigation';
import Chat from '@/components/chat';
import { useEffect, useState } from 'react';

export default function ChatPage() {
  const { id } = useParams();
  const [isLoading, setIsLoading] = useState(true);
  
  if (!id) return null;
  
  return <Chat id={Array.isArray(id) ? id[0] : id} />;
}