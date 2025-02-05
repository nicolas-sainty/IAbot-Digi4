import os
import requests
import json
import numpy as np
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
from langchain_openai.embeddings import OpenAIEmbeddings

# 📌 Charger les variables d'environnement
load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 📌 Connexion à Supabase via l'API
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
embeddings_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# 📌 Vérifier la connexion
print("✅ Connexion à Supabase API réussie !")

# 📌 Vérifier les années déjà présentes dans Supabase
def get_existing_years(table_name, column_name="season"):
    """Retourne la liste des années déjà présentes dans une table en filtrant les valeurs None."""
    response = supabase.table(table_name).select(column_name).execute()

    if response.data:
        return {row[column_name] for row in response.data if row[column_name] is not None}
    
    return set()


# 📌 Déterminer les années à récupérer
def get_years_to_fetch():
    """Retourne deux listes :
    - `missing_race_driver_years` : Années où `races` et `drivers` doivent être récupérées.
    - `missing_result_years` : Années où `results` sont absents, mais où `races` et `drivers` existent déjà.
    """
    existing_race_years = get_existing_years("races")
    existing_driver_years = get_existing_years("drivers", column_name="season")
    existing_result_years = get_existing_years("results", column_name="season")

    print("📌 Années dans races :", sorted(existing_race_years))
    print("📌 Années dans drivers :", sorted(existing_driver_years))
    print("📌 Années dans results :", sorted(existing_result_years))

    # 1️⃣ Années où races et drivers sont absents => il faut tout récupérer
    missing_race_driver_years = set(range(1950, 2024)) - (existing_race_years & existing_driver_years)

    # 2️⃣ Années où races et drivers existent mais results est absent
    missing_result_years = (existing_race_years & existing_driver_years) - existing_result_years

    return sorted(missing_race_driver_years), sorted(missing_result_years)



# 📌 Récupérer et insérer les courses et pilotes pour les années manquantes
def fetch_races_and_drivers(years):
    """Récupérer toutes les courses et pilotes uniquement pour les années manquantes."""
    for year in years:
        print(f"🔄 Récupération des données pour l'année {year}...")

        # 🔹 Récupérer les courses
        races_url = f"http://ergast.com/api/f1/{year}.json"
        races_response = requests.get(races_url)

        if races_response.status_code == 200:
            races_data = races_response.json()
            print(f"✅ Courses récupérées pour {year} !")

            races = [
                {
                    "season": year,
                    "round": int(race['round']),
                    "circuit_id": race['Circuit']['circuitId'],
                    "name": race['raceName'],
                    "date": race['date'],
                    "time": race.get('time', None),
                    "url": race['url'],
                    "embedding": json.dumps(embeddings_model.embed_query(f"Course: {race['raceName']} - {race['date']} sur {race['Circuit']['circuitId']}"))
                }
                for race in races_data['MRData']['RaceTable']['Races']
            ]
            supabase.table("races").insert(races).execute()
        else:
            print(f"❌ Erreur récupération des courses pour {year} : {races_response.status_code}")

        # 🔹 Récupérer les pilotes
        drivers_url = f"http://ergast.com/api/f1/{year}/drivers.json"
        drivers_response = requests.get(drivers_url)

        if drivers_response.status_code == 200:
            drivers_data = drivers_response.json()
            print(f"✅ Pilotes récupérés pour {year} !")

            drivers = [
                {
                    "driver_ref": driver['driverId'],
                    "season": year,
                    "number": int(driver['permanentNumber']) if driver.get('permanentNumber') and driver['permanentNumber'] != "" else None,
                    "code": driver.get('code') or None,
                    "first_name": driver['givenName'],
                    "last_name": driver['familyName'],
                    "dob": driver['dateOfBirth'],
                    "nationality": driver['nationality'],
                    "url": driver['url'],
                    "embedding": json.dumps(embeddings_model.embed_query(f"Pilote: {driver['givenName']} {driver['familyName']} ({driver['nationality']}), né le {driver['dateOfBirth']}"))
                }
                for driver in drivers_data['MRData']['DriverTable']['Drivers']
            ]
            supabase.table("drivers").upsert(drivers, on_conflict=["driver_ref", "season"]).execute()
        else:
            print(f"❌ Erreur récupération des pilotes pour {year} : {drivers_response.status_code}")

# 📌 Récupérer et insérer les résultats pour les années manquantes
def fetch_results(years):
    """Récupérer uniquement les résultats pour les années qui manquent."""
    for year in years:
        results_url = f"http://ergast.com/api/f1/{year}/results.json"
        results_response = requests.get(results_url)

        if results_response.status_code == 200:
            results_data = results_response.json()
            print(f"✅ Résultats récupérés pour {year} !")

            # 🔹 Récupérer les pilotes existants dans Supabase
            existing_drivers_response = supabase.table("drivers").select("driver_ref").execute()
            existing_drivers = {d["driver_ref"] for d in existing_drivers_response.data}

            results = []
            for race in results_data['MRData']['RaceTable']['Races']:
                race_id = int(race['round'])

                for result in race['Results']:
                    driver_id = result['Driver']['driverId']

                    # 🔥 Vérifier si le pilote existe avant d'insérer
                    if driver_id not in existing_drivers:
                        print(f"⚠️ Skipping result for {driver_id} (driver not in database)")
                        continue

                    results.append({
                        "season": year,
                        "race_id": race_id,
                        "driver_id": driver_id,
                        "constructor": result['Constructor']['name'],
                        "grid": int(result['grid']),
                        "position": result.get('position', 'DNF'),
                        "points": float(result['points']),
                        "status": result['status'],
                        "embedding": json.dumps(embeddings_model.embed_query(
                            f"Résultat: {driver_id} a terminé {result.get('position', 'DNF')} avec {result['points']} points."
                        ))
                    })

            # Insérer les résultats filtrés
            if results:
                supabase.table("results").insert(results).execute()
                print(f"✅ Résultats insérés pour {year} dans Supabase !")
            else:
                print(f"⚠️ Aucun résultat inséré pour {year}, pilotes manquants.")
        else:
            print(f"❌ Erreur récupération des résultats pour {year} : {results_response.status_code}")

# 📌 Exécuter les fonctions
# 📌 Exécuter les fonctions avec les années adaptées
missing_race_driver_years, missing_result_years = get_years_to_fetch()

if missing_race_driver_years:
    print(f"📌 Années où races et drivers sont manquants : {missing_race_driver_years}")
    fetch_races_and_drivers(missing_race_driver_years)  # Ne télécharge races et drivers que si nécessaire

if missing_result_years:
    print(f"📌 Années où seulement les résultats sont manquants : {missing_result_years}")
    fetch_results(missing_result_years)  # Ne télécharge les résultats que si races et drivers existent déjà

print("🚀 Script terminé avec succès sur Supabase API !")


print("🚀 Script terminé avec succès sur Supabase API !")
