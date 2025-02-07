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

# 🔹 Variable globale pour stocker les embeddings et éviter le double chargement
vector_store = None


import chromadb

def clear_chromadb():
    """ Supprime toutes les anciennes données de ChromaDB. """
    chromadb_client = chromadb.PersistentClient(path="./chromadb_f1")
    
    for collection_name in ["results", "drivers"]:
        collection = chromadb_client.get_or_create_collection(name=collection_name)
        collection.delete(where={})  # Supprime tout le contenu

    print("✅ ChromaDB vidé des anciennes données.")


def regenerate_chromadb_embeddings():
    """ Génère les embeddings pour results et drivers, puis les stocke dans ChromaDB. """
    print("🔄 Régénération des embeddings pour results et drivers...")

    chromadb_client = chromadb.PersistentClient(path="./chromadb_f1")

    # ✅ Embeddings pour `drivers`
    drivers = supabase.table("drivers").select("driver_ref", "first_name", "last_name", "dob", "nationality", "url").execute().data
    collection_drivers = chromadb_client.get_or_create_collection(name="drivers")

    for driver in drivers:
        embedding = embeddings_model.embed_query(
            f"Pilote {driver['first_name']} {driver['last_name']} ({driver['nationality']}). "
            f"Né le {driver['dob']}. Plus d'informations : {driver['url']}."
        )
        collection_drivers.add(
            ids=[driver["driver_ref"]],
            embeddings=[embedding],
            metadatas=[driver]
        )

    print(f"✅ {len(drivers)} pilotes mis à jour dans ChromaDB.")

    # ✅ Embeddings pour `results`
    results = supabase.table("results").select("season", "circuit_id", "driver_id", "constructor_id", "grid", "position", "points", "status").execute().data
    collection_results = chromadb_client.get_or_create_collection(name="results")

    for result in results:
        embedding = embeddings_model.embed_query(
            f"Résultat {result['season']} - Circuit {result['circuit_id']}: "
            f"Pilote {result['driver_id']}, Écurie {result['constructor_id']}, "
            f"Position {result['position']}, Points {result['points']}, Statut {result['status']}."
        )
        collection_results.add(
            ids=[f"{result['season']}_{result['circuit_id']}_{result['driver_id']}"],
            embeddings=[embedding],
            metadatas=[result]
        )

    print(f"✅ {len(results)} résultats mis à jour dans ChromaDB.")

    print("✅ Régénération des embeddings terminée !")


# ✅ Fonction pour récupérer les embeddings de Supabase avec pagination
def get_all_embeddings():
    all_embeddings = []
    all_texts = []
    all_metadata = []
    batch_size = 500  # Limite de requête pour éviter le timeout

    tables = {
        "races": ("id", "name", "embedding"),
        "drivers": ("driver_ref", "first_name", "last_name", "embedding"),
        "results": ("id", "driver_id", "race_id", "position", "points", "embedding")
    }

    for table, columns in tables.items():
        offset = 0  # Pagination

        while True:
            print(f"🔄 Chargement des données depuis {table} (offset {offset})...")

            response = supabase.table(table).select(*columns).range(offset, offset + batch_size - 1).execute()
            if "error" in response and response["error"]:
                raise Exception(f"❌ Erreur Supabase ({table}) : {response['error']}")

            data = response.data
            if not data:
                print(f"✅ Fin de la récupération pour {table}. {len(all_embeddings)} embeddings chargés.")
                break  # Plus de données, on arrête

            for row in data:
                try:
                    embedding_vector = json.loads(row["embedding"]) if isinstance(row["embedding"], str) else row["embedding"]
                    all_embeddings.append(np.array(embedding_vector, dtype=np.float32))

                    text_value = row["name"] if table == "races" else f"{row['first_name']} {row['last_name']}" if table == "drivers" else f"Résultat: {row['driver_id']} - Position: {row['position']} - Points: {row['points']}"

                    all_texts.append(text_value)
                    all_metadata.append({"table": table, "id": row[columns[0]]})
                except Exception as e:
                    print(f"⚠️ Problème avec une entrée de {table}: {e}")

            offset += batch_size

    print(f"✅ {len(all_embeddings)} embeddings récupérés depuis Supabase.")
    return all_embeddings, all_texts, all_metadata

# ✅ Debug : Vérifier les résultats en course
def debug_results_search():
    print("🔍 Recherche des résultats de course dans ChromaDB...")
    results = vector_store.similarity_search("Résultats de la saison 2019 en Formule 1", k=5)

    if not results:
        print("❌ Aucune donnée trouvée pour 'Résultats de F1 2019'.")
    else:
        for i, res in enumerate(results):
            print(f"📜 Résultat {i+1}: {res.page_content} - Metadata: {res.metadata}")


def create_chatbot():
    print("✅ Chatbot prêt à répondre !")
    chromadb_client = chromadb.PersistentClient(path="./chromadb_f1")
    vector_store = Chroma(persist_directory="./chromadb_f1", embedding_function=embeddings_model)
    return ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY),
        retriever=vector_store.as_retriever()
    )

def get_race_results(season, driver_id=None):
    """ Récupère les résultats pour une saison donnée et un pilote (optionnel). """
    query = supabase.table("results").select("*").eq("season", season)
    
    if driver_id:
        query = query.eq("driver_id", driver_id)
    
    response = query.execute()
    return response.data

# ✅ Récupérer le dernier message utilisateur
def get_last_user_message():
    response = supabase.table("message").select("*").eq("role", "user").order("created_at", desc=True).limit(1).execute()
    return response.data[0] if response.data else None

# ✅ Fonction principale du chatbot
def process_chat():
    print("💬 Chatbot en attente de messages... (tape 'exit' pour quitter)")
    chatbot = create_chatbot()
    last_processed_message_id = None

    while True:
        last_message = get_last_user_message()
        if not last_message:
            time.sleep(2)
            continue

        chat_id = last_message["chat_id"]
        user_message = last_message["content"]
        message_id = last_message["id"]

        if last_processed_message_id == message_id:
            time.sleep(2)
            continue
        
        last_processed_message_id = message_id

        if user_message.lower() in ["exit", "quit", "bye"]:
            print("👋 Chatbot arrêté.")
            break

        print(f"📝 Message utilisateur reçu : {user_message}")

        response = chatbot.invoke({
            "question": f"{user_message}. Cherche uniquement dans les résultats de courses de Formule 1.",
            "chat_history": []
        })
        bot_response = response["answer"]

        print(f"🤖 Réponse générée : {bot_response}")
        supabase.table("message").insert({"chat_id": chat_id, "role": "assistant", "content": bot_response}).execute()

        time.sleep(2)


# ✅ Exécuter le chatbot
if __name__ == "__main__":
    process_chat()
