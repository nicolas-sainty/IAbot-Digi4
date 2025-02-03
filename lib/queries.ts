// Créer un supebase client
import { UUID } from 'crypto'
import { supabase } from './supabase'

// Créer une fonction pour récupérer les messages

export async function getChats() {
  const { data, error } = await supabase.from('chat').select('*')
  if (error) throw error
  return data
}

export async function createChat(title: string) {
  const { data, error } = await supabase
    .from('chat')
    .insert({ title: title, created_at: new Date().toISOString() })
    .select()
    .single()
  if (error) throw error
  console.log('Nouveau chat créé:', data)
  return data
}

export async function getMessages(chatId: string) {
  const { data, error } = await supabase.from('message').select('*').eq('chat_id', chatId)
  if (error) throw error
  return data
}

export async function createMessages(chatId: UUID, content: JSON, role: string) {
  const { data, error } = await supabase.from('message').insert({ chat_id: chatId, content: content, role: role, created_at: new Date().toISOString() })
  if (error) throw error
  return data
}
