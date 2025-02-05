import os
import json
import numpy as np
from typing import List
import time


from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.schema import AIMessage, HumanMessage
from dotenv import load_dotenv
from supabase import create_client

# 📌 Charger les variables d'environnement
load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Vérification des clés essentielles
if not SUPABASE_URL or not SUPABASE_KEY or not OPENAI_API_KEY:
    raise ValueError("Vérifiez que SUPABASE_URL, SUPABASE_KEY et OPENAI_API_KEY sont définis dans votre fichier .env")

# 📌 Initialiser Supabase et Embeddings
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
embeddings_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# ✅ Fonction pour récupérer les embeddings de Supabase
def get_all_embeddings():
    """
    Récupère les embeddings stockés dans les tables races, drivers et results.
    """
    all_embeddings = []
    all_texts = []
    all_metadata = []

    # Définir les colonnes spécifiques à chaque table
    tables = {
        "races": ("id", "name"),  # "name" est le nom de la course
        "drivers": ("driver_ref", "first_name", "last_name"),  # Concaténer first_name + last_name
        "results": ("id", "driver_id")  # Utiliser driver_id pour identifier les résultats
    }

    for table, columns in tables.items():
        response = supabase.table(table).select(*columns, "embedding").execute()

        if "error" in response and response["error"]:
            raise Exception(f"Erreur Supabase ({table}) : {response['error']}")

        if not response.data or len(response.data) == 0:
            print(f"⚠️ Aucun embedding trouvé dans la table {table}.")
            continue

        for row in response.data:
            try:
                embedding_vector = json.loads(row["embedding"]) if isinstance(row["embedding"], str) else row["embedding"]
                all_embeddings.append(np.array(embedding_vector, dtype=np.float32))  # Convertir en array NumPy
                
                # Générer le texte associé à l'embedding
                if table == "drivers":
                    text_value = f"{row['first_name']} {row['last_name']}"  # Concatène prénom + nom
                elif table == "results":
                    text_value = f"Résultat pour le pilote {row['driver_id']}"  # Associe à un pilote
                else:
                    text_value = row[columns[1]]  # Prend la colonne "name" pour races

                all_texts.append(text_value)
                all_metadata.append({"table": table, "id": row[columns[0]]})
            except Exception as e:
                print(f"⚠️ Problème avec une entrée de {table}: {e}")

    print(f"✅ {len(all_embeddings)} embeddings récupérés depuis Supabase.")
    return all_embeddings, all_texts, all_metadata

# ✅ Charger les embeddings dans Chroma
def load_embeddings_into_chroma():
    """
    Charge les embeddings récupérés dans une base vectorielle Chroma.
    """
    embeddings, texts, metadata = get_all_embeddings()

    if not embeddings:
        print("❌ Aucun embedding trouvé, arrêt du chargement.")
        return None

    # Initialiser Chroma
    vector_store = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings_model
    )

    # Ajouter les embeddings dans Chroma
    vector_store.add_texts(
        texts=texts,
        metadatas=metadata,
        embeddings=embeddings
    )

    print("✅ Embeddings chargés dans Chroma avec succès !")
    return vector_store

# ✅ Créer le chatbot
def create_chatbot():
    """
    Crée un chatbot LangChain basé sur les embeddings stockés dans Supabase et chargés dans Chroma.
    """
    print("🔄 Chargement des embeddings depuis Supabase...")
    vector_store = load_embeddings_into_chroma()

    if not vector_store:
        raise Exception("❌ Impossible de charger les embeddings dans Chroma.")

    print("✅ Chatbot prêt à l'emploi avec les embeddings récupérés !")
    return ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY),
        retriever=vector_store.as_retriever()
    )

# ✅ Récupérer l'historique du chat depuis Supabase
def get_chat_history(chat_id: str) -> List:
    response = supabase.table("message").select("*").eq("chat_id", chat_id).order("id").execute()

    if "error" in response and response["error"]:
        raise Exception(f"Erreur Supabase : {response['error']}")

    if not response.data or len(response.data) == 0:
        print("Aucun message trouvé pour ce chat_id.")
        return []

    messages = response.data
    history = []
    for message in messages:
        if message["role"] == "user":
            history.append(HumanMessage(content=message["content"]))
        elif message["role"] == "assistant":
            history.append(AIMessage(content=message["content"]))

    return history

# ✅ Récupérer le dernier message utilisateur
def get_last_user_message() -> dict:
    response = supabase.table("message").select("*").eq("role", "user").order("id", desc=True).limit(1).execute()

    if hasattr(response, "error") and response.error:
        raise Exception(f"Erreur Supabase : {response.error}")

    if not response.data or len(response.data) == 0:
        print("⚠️ Aucun message utilisateur trouvé.")
        return None

    return response.data[0]

# ✅ Sauvegarder la réponse du chatbot
def save_assistant_message(chat_id: str, content: str):
    """
    Sauvegarde une réponse de l'assistant dans la base de données.
    """
    response = supabase.table("message").insert({
        "chat_id": chat_id,
        "role": "assistant",
        "content": content
    }).execute()

    if isinstance(response, dict) and "error" in response:
        raise Exception(f"Erreur Supabase : {response['error']}")

    if not response.data:
        raise Exception("⚠️ L'insertion dans la table 'message' a échoué.")

    print("✅ Réponse de l'assistant sauvegardée avec succès.")

# ✅ Fonction principale
import time

def process_chat():
    """
    Boucle continue pour écouter et répondre aux messages des utilisateurs
    uniquement lorsque le dernier message provient d'un utilisateur.
    """
    print("💬 Chatbot en attente de messages... (tape 'exit' pour quitter)\n")

    # Charger les embeddings UNE SEULE FOIS
    print("🔄 Initialisation des embeddings...")
    vector_store = load_embeddings_into_chroma()
    if not vector_store:
        print("❌ Impossible de charger les embeddings. Arrêt du chatbot.")
        return

    print("✅ Chatbot prêt à répondre !")

    chatbot = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY),
        retriever=vector_store.as_retriever()
    )

    last_processed_message_id = None  # Stocke l'ID du dernier message traité

    while True:
        # Récupérer le dernier message utilisateur
        last_message = get_last_user_message()

        # Vérifier si un message a été trouvé
        if not last_message:
            print("⚠️ Aucun nouveau message utilisateur trouvé. En attente...")
            time.sleep(2)  # Attendre 2 secondes avant de revérifier
            continue

        chat_id = last_message["chat_id"]
        user_message = last_message["content"]
        message_id = last_message["id"]  # ID unique du message

        # Vérifier si c'est un nouveau message (éviter de traiter deux fois le même)
        if last_processed_message_id == message_id:
            time.sleep(2)  # Attendre avant de vérifier à nouveau
            continue

        # Vérifier si c'est bien un message utilisateur
        if last_message["role"] != "user":
            time.sleep(2)  # Attendre avant de vérifier à nouveau
            continue

        # Mettre à jour le dernier message traité
        last_processed_message_id = message_id

        # Vérifier si l'utilisateur veut quitter
        if user_message.lower() in ["exit", "quit", "bye"]:
            print("👋 Chatbot arrêté.")
            break

        # Charger l'historique du chat
        history = get_chat_history(chat_id)

        # Générer une réponse SANS RECHARGER LES EMBEDDINGS
        response = chatbot({"question": user_message, "chat_history": history})
        bot_response = response["answer"]
        print(f"🤖 {bot_response}")

        # Sauvegarder la réponse dans Supabase
        save_assistant_message(chat_id, bot_response)

        # Pause pour éviter une boucle trop rapide
        time.sleep(2)




# ✅ Exécuter le script
if __name__ == "__main__":
    process_chat()
