// Garde le contexte quand tu change de page
'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';

// Définir le type pour le contexte
interface ChatContextType {
  pendingMessage: string;
  setPendingMessage: (message: string) => void;
}

// Créer le contexte
const ChatContext = createContext<ChatContextType | undefined>(undefined);

// Créer le fournisseur de contexte
export const ChatProvider = ({ children }: { children: ReactNode }) => {
  const [pendingMessage, setPendingMessage] = useState<string>('');

  return (
    <ChatContext.Provider value={{ pendingMessage, setPendingMessage }}>
      {children}
    </ChatContext.Provider>
  );
};

// Hook personnalisé pour utiliser le contexte
export const useChatContext = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChatContext must be used within a ChatProvider');
  }
  return context;
}; 