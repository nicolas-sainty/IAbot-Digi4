// Import des fonctions nécessaires
import { getMessages } from "@/lib/queries";    // Fonction pour récupérer les messages depuis la base de données
import { NextResponse } from "next/server";      // Utilitaire Next.js pour gérer les réponses API
 
// Définition d'une route API qui répond aux requêtes POST
// Cette fonction est appelée quand quelqu'un fait une requête POST à /api/messages
export async function POST(req: Request) {
    // Extrait l'ID du chat depuis le corps de la requête
    // req.json() transforme le corps de la requête JSON en objet JavaScript
    const { id } = await req.json();
    
    // Utilise la fonction getMessages pour récupérer tous les messages
    // associés à l'ID du chat fourni
    const messages = await getMessages(id);
    
    // Affiche les messages dans la console (utile pour le débogage)
    console.log(messages);
    
    // Renvoie les messages au format JSON
    // NextResponse.json crée une réponse HTTP appropriée
    return NextResponse.json(messages);
}