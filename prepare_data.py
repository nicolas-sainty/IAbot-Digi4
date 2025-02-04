import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.schema import Document
from dotenv import load_dotenv
from supabase import create_client

# Charger les variables d'environnement
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialiser Supabase et Embeddings
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# Fonction pour extraire les données depuis Supabase
def fetch_data_from_supabase():
    """Récupérer les données des tables Supabase"""
    races = supabase.table("races").select("*").execute().data
    drivers = supabase.table("drivers").select("*").execute().data
    results = supabase.table("results").select("*").execute().data

    documents = []

    # Transformer les données en texte structuré pour le modèle
    for race in races:
        doc = Document(
            page_content=f"Course : {race['name']} - {race['date']} au circuit {race['circuit_id']}.",
            metadata={"type": "race", "id": race['id']}
        )
        documents.append(doc)

    for driver in drivers:
        doc = Document(
            page_content=f"Pilote : {driver['first_name']} {driver['last_name']}, nationalité : {driver['nationality']}.",
            metadata={"type": "driver", "id": driver['driver_ref']}
        )
        documents.append(doc)

    for result in results:
        doc = Document(
            page_content=f"Résultat : {result['driver_id']} a terminé {result['position']} avec {result['points']} points.",
            metadata={"type": "result", "id": result['id']}
        )
        documents.append(doc)

    return documents

# Charger les données et créer un index vectoriel
def create_vector_store(documents):
    """Créer un index vectoriel avec Chroma pour la recherche"""
    vector_store = Chroma.from_documents(documents, embeddings, persist_directory="./chroma_db")
    vector_store.persist()  # Sauvegarder l'index
    print("✅ Index vectoriel créé et sauvegardé !")
    return vector_store

# Fonction principale
def prepare_data():
    print("🔄 Récupération des données depuis Supabase...")
    documents = fetch_data_from_supabase()
    print(f"✅ {len(documents)} documents récupérés et préparés.")
    
    print("🔄 Création de l'index vectoriel...")
    vector_store = create_vector_store(documents)
    return vector_store

# Exécuter la préparation des données
if __name__ == "__main__":
    prepare_data()
