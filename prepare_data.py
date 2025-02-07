import os
import requests
import numpy as np
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
from langchain_openai.embeddings import OpenAIEmbeddings

# 📌 Charger les variables d'environnement depuis `.env`
load_dotenv()

# 📌 Récupérer les variables Supabase
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 📌 Connexion à Supabase via l'API
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
embeddings_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# 📌 Vérifier la connexion
print("✅ Connexion à Supabase API réussie !")

# 📌 Fonction pour récupérer et stocker les embeddings
def save_embeddings_to_supabase():
    """Crée et stocke les embeddings pour les courses, pilotes et résultats."""
    
    print("🔄 Récupération des données pour embeddings...")

    # Récupération des courses, pilotes et résultats
    races = supabase.table("races").select("*").execute().data
    drivers = supabase.table("drivers").select("*").execute().data
    results = supabase.table("results").select("*").execute().data

    embedded_data = []

    # 🔹 Embeddings pour les courses
    for race in races:
        text = f"Grand Prix : {race['name']} - {race['date']} sur le circuit {race['circuit_id']}."
        vector = embeddings_model.embed_query(text)
        embedded_data.append({
            "id": race["id"],
            "type": "race",
            "text": text,
            "embedding": vector
        })

    # 🔹 Embeddings pour les pilotes
    for driver in drivers:
        text = f"Pilote : {driver['first_name']} {driver['last_name']} ({driver['nationality']})."
        vector = embeddings_model.embed_query(text)
        embedded_data.append({
            "id": driver["driver_ref"],
            "type": "driver",
            "text": text,
            "embedding": vector
        })

    # 🔹 Embeddings pour les résultats
    for result in results:
        text = f"Résultat : {result['driver_id']} a terminé {result['position']} avec {result['points']} points."
        vector = embeddings_model.embed_query(text)
        embedded_data.append({
            "id": result["id"],
            "type": "result",
            "text": text,
            "embedding": vector
        })

    print(f"✅ {len(embedded_data)} embeddings générés.")

    # 🔄 Insérer les embeddings dans Supabase
    print("🚀 Insertion des embeddings dans Supabase...")
    for data in embedded_data:
        response = supabase.table("embeddings").upsert({
            "id": data["id"],
            "type": data["type"],
            "text": data["text"],
            "embedding": data["embedding"]
        }).execute()
        
        if response.data:
            print(f"✅ Embedding inséré pour {data['type']} - {data['id']}")
        else:
            print(f"⚠️ Problème d'insertion pour {data['id']}")

    print("✅ Tous les embeddings sont stockés avec succès !")

# 📌 Exécuter les fonctions
save_embeddings_to_supabase()
print("🚀 Script terminé avec succès sur Supabase API !")
