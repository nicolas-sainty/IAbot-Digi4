// Créer un supebase client
import { supabase } from './supabase'

// Créer une fonction pour récupérer les messages

export async function getChats() {
  const { data, error } = await supabase.from('chat').select('*')
  if (error) throw error
  return data
}

export async function createChat( title: string ) {
  const { data, error } = await supabase.from('chat').insert({ title: title, created_at: new Date().toISOString()  })
  if (error) throw error
  return data
}

export async function getMessages(chatId: string) {
  const { data, error } = await supabase.from('message').select('*').eq('chat_id', chatId)
  if (error) throw error
  return data
}
