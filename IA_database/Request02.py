import os
import requests
import json
import argparse
import numpy as np
from supabase import create_client
from dotenv import load_dotenv
from langchain_openai.embeddings import OpenAIEmbeddings
import uuid
import time


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
parser.add_argument("-force-update", action="store_true", help="Forcer la mise à jour de toutes les données (résultats, pilotes, constructeurs)")
args = parser.parse_args()

# ✅ Vérifier les circuits existants en base
def get_existing_circuits():
    response = supabase.table("circuits").select("circuit_id").execute()
    return {row["circuit_id"] for row in response.data} if response.data else set()

# ✅ Vérifier les années présentes en base
def get_existing_years(table_name, column_name="season"):
    response = supabase.table(table_name).select(column_name).execute()
    return {row[column_name] for row in response.data if row[column_name] is not None} if response.data else set()

# ✅ Vérifier les données manquantes
def get_years_to_fetch():
    existing_driver_years = get_existing_years("drivers", column_name="season")
    existing_result_years = get_existing_years("results", column_name="season")
    existing_constructor_years = get_existing_years("constructors", column_name="season")

    missing_driver_years = set(range(1950, 2025)) - existing_driver_years
    missing_result_years = existing_driver_years - existing_result_years
    missing_constructor_years = set(range(1950, 2025)) - existing_constructor_years

    return sorted(missing_driver_years), sorted(missing_result_years), sorted(missing_constructor_years)



def create_placeholder_driver(driver_id, season):
    """ Crée un pilote avec des valeurs fictives si le pilote est introuvable. """
    placeholder_driver = {
        "driver_ref": driver_id,
        "season": season,
        "first_name": driver_id.capitalize(),
        "last_name": "Unknown",
        "dob": "1900-01-01",  # Date de naissance fictive
        "nationality": "Unknown",
        "url": "https://en.wikipedia.org/wiki/Formula_1"  # Lien générique
    }
    print(f"🚨 Création d'un pilote fictif : {placeholder_driver}")
    supabase.table("drivers").insert(placeholder_driver).execute()


# ✅ Récupérer et insérer les constructeurs
def fetch_constructors(years):
    for year in years:
        print(f"🔄 Récupération des constructeurs pour {year}...")
        constructors_url = f"http://ergast.com/api/f1/{year}/constructors.json"
        response = requests.get(constructors_url)
        if response.status_code == 200:
            constructors_data = response.json()
            constructors = [
                {
                    "constructor_ref": constructor['constructorId'],
                    "season": year,
                    "name": constructor['name'],
                    "nationality": constructor['nationality'],
                    "url": constructor['url']
                }
                for constructor in constructors_data['MRData']['ConstructorTable']['Constructors']
            ]
            supabase.table("constructors").upsert(constructors, on_conflict=["constructor_ref", "season"]).execute()

def get_existing_drivers():
    """ Vérifie tous les pilotes déjà en base. """
    response = supabase.table("drivers").select("driver_ref").execute()
    return {row["driver_ref"] for row in response.data} if response.data else set()

def fetch_drivers(years):
    for year in years:
        print(f"🔄 Récupération des pilotes pour {year}...")

        drivers_url = f"http://ergast.com/api/f1/{year}/drivers.json"
        response = requests.get(drivers_url)
        if response.status_code == 200:
            drivers_data = response.json()
            drivers = [
                {
                    "driver_ref": driver['driverId'],
                    "season": year,
                    "first_name": driver['givenName'],
                    "last_name": driver['familyName'],
                    "dob": driver['dateOfBirth'],
                    "nationality": driver['nationality'],
                    "url": driver['url']
                }
                for driver in drivers_data['MRData']['DriverTable']['Drivers']
            ]

            print(f"🌟 {len(drivers)} pilotes récupérés pour {year}. Exemple : {drivers[:3]}")

            if drivers:
                supabase.table("drivers").upsert(drivers, on_conflict=["driver_ref", "season"]).execute()
                print(f"✅ Pilotes insérés/mis à jour pour {year}.")
            else:
                print(f"⚠️ Aucun pilote récupéré pour {year}.")

            # 🕒 Pause pour laisser Supabase valider l'ajout des pilotes
            time.sleep(2)

            # 🔍 Vérifier si les pilotes sont bien en base
            existing_drivers = get_existing_drivers()
            missing_after_insert = [driver['driver_ref'] for driver in drivers if driver['driver_ref'] not in existing_drivers]

            if missing_after_insert:
                print(f"❌ Pilotes toujours absents après insertion : {missing_after_insert}")



# ✅ Récupérer et insérer les résultats

def ensure_circuits_exist(circuit_ids):
    """ Vérifie que tous les circuits existent dans la table circuits, sinon les ajoute avec des valeurs par défaut. """
    existing_circuits = get_existing_circuits()
    missing_circuits = circuit_ids - existing_circuits

    if missing_circuits:
        print(f"🔍 {len(missing_circuits)} circuits manquants détectés. Ajout en cours...")

        circuits_data = [
            {
                "circuit_id": circuit_id,
                "circuit_name": f"Circuit {circuit_id.capitalize()}",
                "locality": "Unknown",
                "country": "Unknown",
                "latitude": 0.0,
                "longitude": 0.0,
                "url": "https://en.wikipedia.org/wiki/List_of_Formula_One_circuits"
            }
            for circuit_id in missing_circuits
        ]

        supabase.table("circuits").upsert(circuits_data, on_conflict=["circuit_id"]).execute()
        print(f"✅ {len(circuits_data)} circuits ajoutés en base avec des valeurs par défaut.")



# Ajout dans fetch_results
def fetch_circuits():
    print("🔄 Récupération de tous les circuits...")
    circuits_url = "http://ergast.com/api/f1/circuits.json"
    response = requests.get(circuits_url)
    
    if response.status_code == 200:
        circuits_data = response.json()
        circuits = [
            {
                "circuit_id": circuit['circuitId'],
                "circuit_name": circuit['circuitName'],
                "locality": circuit['Location']['locality'],
                "country": circuit['Location']['country'],
                "latitude": float(circuit['Location']['lat']),
                "longitude": float(circuit['Location']['long']),
                "url": circuit['url']
            }
            for circuit in circuits_data['MRData']['CircuitTable']['Circuits']
        ]
        supabase.table("circuits").upsert(circuits, on_conflict=["circuit_id"]).execute()
        print(f"✅ {len(circuits)} circuits ajoutés ou mis à jour !")
    else:
        print(f"❌ Erreur lors de la récupération des circuits : {response.status_code}")


def fetch_results(years):
    for year in years:
        print(f"🔄 Récupération des résultats pour {year}...")

        results = []
        circuit_ids = set()
        missing_drivers = set()

        offset = 0
        limit = 30

        while True:
            results_url = f"http://ergast.com/api/f1/{year}/results.json?limit={limit}&offset={offset}"
            response = requests.get(results_url)

            if response.status_code == 200:
                results_data = response.json()
                races = results_data['MRData']['RaceTable']['Races']

                if not races:
                    break

                for race in races:
                    circuit_id = race['Circuit']['circuitId']
                    circuit_ids.add(circuit_id)

                    for result in race['Results']:
                        driver_id = result['Driver']['driverId']

                        # ✅ Vérifier si le pilote existe en base
                        existing_drivers = get_existing_drivers()
                        if driver_id not in existing_drivers:
                            missing_drivers.add(driver_id)

                        # ✅ Vérification et remplacement des NULL
                        constructor = result['Constructor']['constructorId'] if 'Constructor' in result and 'constructorId' in result['Constructor'] else "Unknown"
                        grid = int(result['grid']) if result['grid'] else "N/A"
                        position = result.get('position', 'DNF')
                        points = float(result['points']) if 'points' in result else 0
                        status = result['status'] if 'status' in result else "Unknown"

                        # 🏁 Ajouter à la liste des résultats
                        results.append({
                            "season": year,
                            "circuit_id": circuit_id,
                            "driver_id": driver_id,
                            "constructor_id": constructor,
                            "grid": grid,
                            "position": position,
                            "points": points,
                            "status": status
                        })

                offset += limit

            else:
                print(f"❌ Erreur lors de la récupération des résultats pour {year} : {response.status_code}")
                break

        # 🏎 Vérifier et ajouter les circuits manquants AVANT l'insertion des résultats
        ensure_circuits_exist(circuit_ids)

        # 🏎 Ajouter les pilotes manquants
        if missing_drivers:
            print(f"⚠️ {len(missing_drivers)} pilotes manquants détectés. Ajout en cours...")
            fetch_drivers([year])
            time.sleep(2)

            # 🔄 Vérification finale des pilotes après mise à jour
            existing_drivers = get_existing_drivers()
            still_missing = [driver for driver in missing_drivers if driver not in existing_drivers]

            if still_missing:
                print(f"❌ Pilotes toujours absents après mise à jour : {still_missing}")

        # 🔄 Supprimer les entrées en double avant d'insérer
        results = list({(r["season"], r["circuit_id"], r["driver_id"]): r for r in results}.values())

        # 🏁 Insérer tous les résultats avec vérification des pilotes
        batch_upsert("results", results, "season, circuit_id, driver_id")



def batch_upsert(table, data, conflict_columns):
    """ Gère les upserts en batch pour éviter les doublons sur ON CONFLICT DO UPDATE """
    BATCH_SIZE = 1000
    for i in range(0, len(data), BATCH_SIZE):
        batch = data[i:i + BATCH_SIZE]
        try:
            print(f"🔄 Insertion batch {i+1}/{len(data)} ({len(batch)} entrées) dans {table}...")
            supabase.table(table).upsert(batch, on_conflict=conflict_columns).execute()
            print(f"✅ Batch {i+1}/{len(data)} inséré avec succès !")
        except Exception as e:
            print(f"❌ Erreur lors de l'update de {table} (Batch {i+1}/{len(data)}) : {e}")




def regenerate_embeddings():
    print("🔄 Régénération des embeddings pour pilotes et résultats...")

    # 🚀 Embeddings pour Pilotes
    drivers = supabase.table("drivers").select("driver_ref", "first_name", "last_name", "dob", "nationality", "url").execute().data
    updated_drivers = [
        {
            "driver_ref": driver["driver_ref"],
            "embedding": json.dumps(embeddings_model.embed_query(
                f"Pilote {driver['first_name']} {driver['last_name']} ({driver['nationality']}). "
                f"Né le {driver['dob']}. "
                f"Plus d'informations : {driver['url']}."
            ))
        }
        for driver in drivers
    ]
    batch_upsert("drivers", updated_drivers, "driver_ref")

    # 🏎️ Embeddings pour Résultats (Vérification `constructor_id`)
    results = supabase.table("results").select("season", "circuit_id", "driver_id", "constructor_id", "grid", "position", "points", "status").execute().data
    updated_results = []

    for result in results:
        constructor = result["constructor_id"] if result["constructor_id"] is not None else "Unknown"

        updated_results.append({
            "season": result["season"],
            "circuit_id": result["circuit_id"],
            "driver_id": result["driver_id"],
            "embedding": json.dumps(embeddings_model.embed_query(
                f"Résultat de la saison {result['season']}. "
                f"Circuit: {result['circuit_id']}. "
                f"Pilote: {result['driver_id']}. "
                f"Écurie: {constructor}. "
                f"Position sur la grille: {result.get('grid', 'N/A')}. "
                f"Position finale: {result.get('position', 'N/A')}. "
                f"Points marqués: {result.get('points', 0)}. "
                f"Statut de la course: {result.get('status', 'N/A')}."
            ))
        })

    batch_upsert("results", updated_results, "season, circuit_id, driver_id")

    print("✅ Régénération des embeddings terminée !")




def get_years_to_fetch(force_update=False):
    if force_update:
        return list(range(1950, 2025)), list(range(1950, 2025)), list(range(1950, 2025))

    existing_driver_years = get_existing_years("drivers", column_name="season")
    existing_result_years = get_existing_years("results", column_name="season")
    existing_constructor_years = get_existing_years("constructors", column_name="season")

    missing_driver_years = set(range(1950, 2025)) - existing_driver_years
    #missing_result_years = existing_driver_years - existing_result_years
    missing_result_years = set(range(1950, 2025))
    missing_constructor_years = set(range(1950, 2025)) - existing_constructor_years

    return sorted(missing_driver_years), sorted(missing_result_years), sorted(missing_constructor_years)


# ✅ Vérifier les données à télécharger
missing_driver_years, missing_result_years, missing_constructor_years = get_years_to_fetch(args.force_update)

if args.embeddings:
    regenerate_embeddings()
    exit()

fetch_circuits()
fetch_constructors(missing_constructor_years)
fetch_drivers(missing_driver_years)
if missing_result_years:
    fetch_results(missing_result_years)



print("🚀 Script terminé avec succès sur Supabase API !")
