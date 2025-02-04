import os
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.schema import AIMessage, HumanMessage
from dotenv import load_dotenv
from supabase import create_client
from typing import List

# Charger les variables d'environnement
load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Vérification des clés essentielles
if not SUPABASE_URL or not SUPABASE_KEY or not OPENAI_API_KEY:
    raise ValueError("Vérifiez que SUPABASE_URL, SUPABASE_KEY et OPENAI_API_KEY sont définis dans votre fichier .env")

# Initialiser Supabase et Embeddings
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# 📌 Fonction pour récupérer l'historique du chat
def get_chat_history(chat_id: str) -> List:
    """
    Récupère l'historique des messages pour un chat_id donné.
    """
    response = supabase.table("message").select("*").eq("chat_id", chat_id).order("id").execute()

    # ✅ Vérifier si Supabase a retourné une erreur correctement
    if "error" in response and response["error"]:
        raise Exception(f"Erreur Supabase : {response['error']}")

    # ✅ Vérifier si des données ont été retournées
    if not response.data or len(response.data) == 0:
        print("⚠️ Aucun message trouvé pour ce chat_id.")
        return []

    # ✅ Transformer les messages en format LangChain
    messages = response.data
    history = []
    for message in messages:
        if message["role"] == "user":
            history.append(HumanMessage(content=message["content"]))
        elif message["role"] == "assistant":
                history.append(AIMessage(content=message["content"]))
        
        return history


# 📌 Fonction pour récupérer le dernier message utilisateur
def get_last_user_message() -> dict:
    """
    Récupère le dernier message utilisateur dans la base de données.
    """
    response = supabase.table("message").select("*").eq("role", "user").order("id", desc=True).limit(1).execute()

    print("🔍 Debug - Données récupérées depuis Supabase:", response.data)  # ➜ Ajout pour voir le contenu

    # Vérifier si Supabase a retourné une erreur
    if hasattr(response, "error") and response.error:
        raise Exception(f"Erreur Supabase : {response.error}")

    # Vérifier si des données ont été retournées
    if not response.data or len(response.data) == 0:
        print("⚠️ Aucun message utilisateur trouvé.")
        return None

    return response.data[0]

# 📌 Fonction pour sauvegarder une réponse d'assistant
def save_assistant_message(chat_id: str, content: str):
    """
    Sauvegarde une réponse de l'assistant dans la base de données.
    """
    response = supabase.table("message").insert({
        "chat_id": chat_id,
        "role": "assistant",
        "content": content
    }).execute()

    # ✅ Vérifier si Supabase a retourné une erreur
    if isinstance(response, dict) and "error" in response:
        raise Exception(f"Erreur Supabase : {response['error']}")

    # ✅ Vérifier si l'insertion a bien fonctionné
    if not response.data:
        raise Exception("⚠️ L'insertion dans la table 'message' a échoué.")
    
    print("✅ Réponse de l'assistant sauvegardée avec succès.")


# 📌 Fonction pour créer le chatbot
def create_chatbot():
    """
    Crée un chatbot LangChain basé sur un index vectoriel.
    """
    print("🔄 Chargement de l'index vectoriel...")
    vector_store = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

    print("✅ Chatbot prêt à l'emploi.")
    return ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY),
        retriever=vector_store.as_retriever()
    )

# 📌 Fonction principale
def process_last_user_message():
    """
    Traite le dernier message utilisateur et génère une réponse.
    """
    # Récupérer le dernier message utilisateur
    last_message = get_last_user_message()
    if not last_message:
        print("Aucun message utilisateur trouvé.")
        return

    chat_id = last_message["chat_id"]
    user_message = last_message["content"]

    # Charger l'historique du chat
    history = get_chat_history(chat_id)

    # Créer le chatbot
    chatbot = create_chatbot()

    # Générer une réponse
    response = chatbot({"question": user_message, "chat_history": history})
    bot_response = response["answer"]
    print(f"Réponse générée : {bot_response}")

    # Sauvegarder la réponse dans la base de données
    save_assistant_message(chat_id, bot_response)
    print("✅ Réponse de l'assistant sauvegardée.")

# 📌 Exécuter le script
if __name__ == "__main__":
    process_last_user_message()
