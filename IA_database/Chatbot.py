import os
import json
import numpy as np
import time
import argparse
import chromadb

from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from dotenv import load_dotenv
from supabase import create_client

# 📌 Charger les variables d'environnement
load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Vérification des clés essentielles
if not SUPABASE_URL or not SUPABASE_KEY or not OPENAI_API_KEY:
    raise ValueError("❌ Vérifiez que SUPABASE_URL, SUPABASE_KEY et OPENAI_API_KEY sont bien définis dans votre fichier .env")

# 📌 Initialiser Supabase et Embeddings
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
embeddings_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# 📌 Initialiser ChromaDB
CHROMA_DB_PATH = "./chromadb_f1"
chromadb_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

# 📌 Gestion des arguments CLI
parser = argparse.ArgumentParser(description="Chatbot F1 basé sur ChromaDB et Supabase")
parser.add_argument("-reload", action="store_true", help="Recharger ChromaDB et régénérer les embeddings")
args = parser.parse_args()


# 🔄 **Supprimer et recréer les collections dans ChromaDB**
def clear_chromadb():
    """ Supprime et recrée les collections `results` et `drivers` dans ChromaDB. """
    print("⚠️ Suppression des anciennes données ChromaDB...")

    for collection_name in ["results", "drivers"]:
        try:
            # Supprime directement la collection si elle existe
            chromadb_client.delete_collection(name=collection_name)
            print(f"✅ Collection `{collection_name}` supprimée.")

            # Recrée une collection vide
            chromadb_client.get_or_create_collection(name=collection_name)
            print(f"✅ Collection `{collection_name}` recréée.")

        except Exception as e:
            print(f"❌ Erreur lors de la suppression de `{collection_name}` : {e}")


def fetch_all_supabase_data(table_name, batch_size=1000):
    """ Récupère toutes les données d'une table Supabase avec pagination. """
    all_data = []
    offset = 0

    while True:
        print(f"🔄 Chargement des données depuis `{table_name}` (offset {offset})...")
        response = supabase.table(table_name).select("*").range(offset, offset + batch_size - 1).execute()
        
        if not response.data:
            print(f"✅ Fin de la récupération pour `{table_name}`. {len(all_data)} entrées chargées.")
            break  # Plus de données à récupérer

        all_data.extend(response.data)
        offset += batch_size  # Passer au batch suivant

    return all_data


# 🔄 **Générer les nouveaux embeddings et les stocker dans ChromaDB**
def regenerate_chromadb_embeddings():
    """ Génère les embeddings pour `results` et `drivers`, puis les stocke dans ChromaDB. """
    print("🔄 Régénération des embeddings pour `results` et `drivers`...")

    # ✅ **Embeddings pour `drivers`**
    drivers = fetch_all_supabase_data("drivers")
    collection_drivers = chromadb_client.get_or_create_collection(name="drivers")

    for driver in drivers:
        driver = {k: (v if v is not None else "") for k, v in driver.items()}  # ⚠️ Remplace les `None`
        
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

    # ✅ **Embeddings pour `results`**
    results = fetch_all_supabase_data("results")
    collection_results = chromadb_client.get_or_create_collection(name="results")

    for result in results:
        result = {k: (v if v is not None else "") for k, v in result.items()}  # ⚠️ Remplace les `None`
        
        driver_info = supabase.table("drivers").select("first_name", "last_name").eq("driver_ref", result["driver_id"]).execute().data
        driver_name = f"{driver_info[0]['first_name']} {driver_info[0]['last_name']}" if driver_info else result["driver_id"]

        embedding = embeddings_model.embed_query(
            f"Saison {result['season']} - Circuit {result['circuit_id']}: "
            f"Pilote {driver_name}, Écurie {result['constructor_id']}, "
            f"Position sur la grille: {result['grid']}, Position finale: {result['position']}, "
            f"Points marqués: {result['points']}, Statut: {result['status']}."
        )
        collection_results.add(
            ids=[f"{result['season']}_{result['circuit_id']}_{result['driver_id']}"],
            embeddings=[embedding],
            metadatas=[result]
        )

    print(f"✅ {len(results)} résultats mis à jour dans ChromaDB.")
    print("✅ Régénération des embeddings terminée !")


# ✅ **Créer le chatbot LangChain**
def create_chatbot():
    """ Initialise le chatbot après rechargement des embeddings. """
    print("✅ Chatbot prêt à répondre !")
    vector_store = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embeddings_model)
    return ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(temperature=0, model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY),
        retriever=vector_store.as_retriever()
    )


# ✅ **Récupérer le dernier message utilisateur**
def get_last_user_message():
    response = supabase.table("message").select("*").eq("role", "user").order("created_at", desc=True).limit(1).execute()
    return response.data[0] if response.data else None


# ✅ **Fonction principale du chatbot**
def process_chat():
    """ Boucle principale du chatbot pour répondre aux messages en continu. """
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
        test_chromadb_retrieval("Lewis Hamilton")
        print(f"📝 Message utilisateur reçu : {user_message}")

        # 🔍 **Récupération des résultats pertinents via ChromaDB**
        retriever = chatbot.retriever
        retrieved_docs = retriever.get_relevant_documents(user_message)

        # 📌 **Ajout du contexte des résultats récupérés**
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])

        response = chatbot.invoke({
            "question": f"Voici les résultats trouvés dans la base de données:\n\n{context}\n\nMaintenant, réponds à cette question : {user_message}",
            "chat_history": []
        })
        bot_response = response["answer"]

        print(f"🤖 Réponse générée : {bot_response}")
        supabase.table("message").insert({"chat_id": chat_id, "role": "assistant", "content": bot_response}).execute()

        time.sleep(2)


def test_chromadb_retrieval(driver_name):
    """ Vérifie si les résultats d'un pilote sont bien récupérés dans ChromaDB. """
    print(f"🔍 Test de récupération dans ChromaDB pour {driver_name}...")

    retriever = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embeddings_model).as_retriever()
    retrieved_docs = retriever.get_relevant_documents(f"Résultats de {driver_name}")

    if not retrieved_docs:
        print(f"❌ Aucun résultat trouvé pour {driver_name} dans ChromaDB.")
    else:
        print(f"✅ {len(retrieved_docs)} résultats récupérés pour {driver_name}.")
        for doc in retrieved_docs:
            print(f"📜 {doc.page_content}")


# ✅ **Exécuter le chatbot**
if __name__ == "__main__":
    if args.reload:
        print("🔄 Option `-reload` détectée : suppression et recréation de ChromaDB...")
        clear_chromadb()
        regenerate_chromadb_embeddings()
    else:
        print("⚡ Démarrage rapide : utilisation des embeddings existants dans ChromaDB.")

    process_chat()
