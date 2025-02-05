import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
const supabaseServiceKey = process.env.SERVICE_ROLE_KEY
export const supabase = createClient(supabaseUrl, supabaseServiceKey)

// Fonction de test de connexion
export async function testConnection() {
  try {
    const { data, error } = await supabase.from('chat').select('*').limit(1)
    
    if (error) {
      console.error('Erreur de connexion:', error.message)
      return false
    }
    
    console.log('Connexion réussie!')
    return true
  } catch (error) {
    console.error('Erreur:', error.message)
    return false
  }
} 