import os
import requests
import json
import argparse
import numpy as np
from supabase import create_client
from dotenv import load_dotenv
from langchain_openai.embeddings import OpenAIEmbeddings

# 📌 Charger les variables d'environnement
load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Vérification des clés essentielles
if not SUPABASE_URL or not SUPABASE_ANON_KEY or not OPENAI_API_KEY:
    raise ValueError("Vérifiez que SUPABASE_URL, SUPABASE_ANON_KEY et OPENAI_API_KEY sont bien définis.")

# 📌 Connexion à Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
embeddings_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# 📌 Gestion des arguments CLI
parser = argparse.ArgumentParser(description="Script de récupération et d'embeddings F1")
parser.add_argument("-embeddings", action="store_true", help="Régénérer uniquement les embeddings")
args = parser.parse_args()

# ✅ Vérifier les années présentes en base
def get_existing_years(table_name, column_name="season"):
    response = supabase.table(table_name).select(column_name).execute()
    return {row[column_name] for row in response.data if row[column_name] is not None} if response.data else set()

# ✅ Vérifier les courses et pilotes existants
def get_years_to_fetch():
    existing_race_years = get_existing_years("races")
    existing_driver_years = get_existing_years("drivers", column_name="season")
    existing_result_years = get_existing_years("results", column_name="season")

    missing_race_driver_years = set(range(1950, 2024)) - (existing_race_years & existing_driver_years)
    missing_result_years = (existing_race_years & existing_driver_years) - existing_result_years

    return sorted(missing_race_driver_years), sorted(missing_result_years)

# ✅ Ajouter les courses et pilotes
def fetch_races_and_drivers(years):
    for year in years:
        print(f"🔄 Récupération des courses et pilotes pour {year}...")

        # 📌 Courses
        races_url = f"http://ergast.com/api/f1/{year}.json"
        races_response = requests.get(races_url)
        if races_response.status_code == 200:
            races_data = races_response.json()
            races = [
                {
                    "season": year,
                    "round": int(race['round']),
                    "circuit_id": race['Circuit']['circuitId'],
                    "name": race['raceName'],
                    "date": race['date'],
                    "time": race.get('time', None),
                    "url": race['url'],
                    "embedding": json.dumps(embeddings_model.embed_query(
                        f"Grand Prix {race['raceName']} - Saison {year}, Manche {race['round']} sur le circuit {race['Circuit']['circuitId']}."
                    ))
                }
                for race in races_data['MRData']['RaceTable']['Races']
            ]
            supabase.table("races").insert(races).execute()

        # 📌 Pilotes
        drivers_url = f"http://ergast.com/api/f1/{year}/drivers.json"
        drivers_response = requests.get(drivers_url)
        if drivers_response.status_code == 200:
            drivers_data = drivers_response.json()
            drivers = [
                {
                    "driver_ref": driver['driverId'],
                    "season": year,
                    "first_name": driver['givenName'],
                    "last_name": driver['familyName'],
                    "dob": driver['dateOfBirth'],
                    "nationality": driver['nationality'],
                    "url": driver['url'],
                    "embedding": json.dumps(embeddings_model.embed_query(
                        f"Pilote {driver['givenName']} {driver['familyName']} ({driver['nationality']}), saison {year}."
                    ))
                }
                for driver in drivers_data['MRData']['DriverTable']['Drivers']
            ]
            supabase.table("drivers").upsert(drivers, on_conflict=["driver_ref", "season"]).execute()

# ✅ Ajouter les résultats
def fetch_results(years):
    existing_races_response = supabase.table("races").select("id", "season", "round").execute()
    existing_races = {(r["season"], r["round"]): r["id"] for r in existing_races_response.data}

    existing_drivers_response = supabase.table("drivers").select("driver_ref").execute()
    existing_drivers = {d["driver_ref"] for d in existing_drivers_response.data}

    for year in years:
        results_url = f"http://ergast.com/api/f1/{year}/results.json"
        results_response = requests.get(results_url)
        if results_response.status_code == 200:
            results_data = results_response.json()
            results = []
            for race in results_data['MRData']['RaceTable']['Races']:
                season = int(race['season'])
                round_number = int(race['round'])
                race_id = existing_races.get((season, round_number))

                if not race_id:
                    print(f"⚠️ Aucune course trouvée pour Saison {season}, Manche {round_number}. Skipping...")
                    continue

                for result in race['Results']:
                    driver_id = result['Driver']['driverId']
                    if driver_id not in existing_drivers:
                        print(f"⚠️ Skipping result for {driver_id} (driver not in database)")
                        continue

                    results.append({
                        "season": season,
                        "race_id": race_id,
                        "driver_id": driver_id,
                        "constructor": result['Constructor']['name'],
                        "grid": int(result['grid']),
                        "position": result.get('position', 'DNF'),
                        "points": float(result['points']),
                        "status": result['status'],
                        "embedding": json.dumps(embeddings_model.embed_query(
                            f"Résultats F1 - Saison {season}. "
                            f"Grand Prix {round_number}, ID de la course: {race_id}. "
                            f"Pilote: {driver_id}, écurie: {result['Constructor']['name']}. "
                            f"Départ: {result['grid']}, Position finale: {result.get('position', 'DNF')}, "
                            f"Points marqués: {result['points']}, Statut: {result['status']}."
                        ))
                    })

            if results:
                supabase.table("results").insert(results).execute()
                print(f"✅ Résultats insérés pour {year} !")

# ✅ Lancer avec option `-embeddings` ou récupération complète
if args.embeddings:
    print("🔄 Régénération des embeddings sans retéléchargement des données...")
    fetch_results(get_existing_years("results"))
    print("✅ Embeddings régénérés avec succès !")
    exit()

missing_race_driver_years, missing_result_years = get_years_to_fetch()
if missing_race_driver_years:
    fetch_races_and_drivers(missing_race_driver_years)
if missing_result_years:
    fetch_results(missing_result_years)

print("🚀 Script terminé avec succès sur Supabase API !")
