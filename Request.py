import os
import requests
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv

# 📌 Charger les variables d'environnement depuis `.env`
load_dotenv()

# 📌 Récupérer les variables Supabase
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

# 📌 Connexion à Supabase via l'API
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# 📌 Vérifier la connexion
print("✅ Connexion à Supabase API réussie !")

# 📌 Réinitialiser les tables
def reset_tables():
    try:
        supabase.table("results").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        supabase.table("races").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        supabase.table("drivers").delete().neq("driver_ref", "").execute()
        print("✅ Tables vidées avec succès sur Supabase !")
    except Exception as e:
        print(f"❌ Erreur lors de la réinitialisation des tables : {e}")

# 📌 Récupérer toutes les courses et les pilotes depuis 1950
def fetch_races_and_drivers():
    """Récupérer toutes les courses et pilotes depuis 1950."""
    for year in range(1950, 2024):
        # Récupérer les courses pour l'année
        races_url = f"http://ergast.com/api/f1/{year}.json"
        races_response = requests.get(races_url)

        if races_response.status_code == 200:
            races_data = races_response.json()
            print(f"✅ Données des courses récupérées pour {year} !")

            races = [
                {
                    "season": year,
                    "round": int(race['round']),
                    "circuit_id": race['Circuit']['circuitId'],
                    "name": race['raceName'],
                    "date": race['date'],
                    "time": race.get('time', None),
                    "url": race['url']
                }
                for race in races_data['MRData']['RaceTable']['Races']
            ]
            supabase.table("races").insert(races).execute()
        else:
            print(f"❌ Erreur récupération des courses pour {year} : {races_response.status_code}")

        # Récupérer les pilotes pour l'année
        drivers_url = f"http://ergast.com/api/f1/{year}/drivers.json"
        drivers_response = requests.get(drivers_url)

        if drivers_response.status_code == 200:
            drivers_data = drivers_response.json()
            print(f"✅ Données des pilotes récupérées pour {year} !")

            drivers = [
                {
                    "driver_ref": driver['driverId'],
                    "number": int(driver['permanentNumber']) if driver.get('permanentNumber') and driver['permanentNumber'] != "" else None,
                    "code": driver.get('code') or None,
                    "first_name": driver['givenName'],
                    "last_name": driver['familyName'],
                    "dob": driver['dateOfBirth'],
                    "nationality": driver['nationality'],
                    "url": driver['url']
                }
                for driver in drivers_data['MRData']['DriverTable']['Drivers']
            ]
            supabase.table("drivers").upsert(drivers, on_conflict=["driver_ref"]).execute()
        else:
            print(f"❌ Erreur récupération des pilotes pour {year} : {drivers_response.status_code}")

# 📌 Récupérer les résultats des courses
def fetch_results():
    """Récupérer les résultats des courses pour chaque année."""
    for year in range(1950, 2024):
        results_url = f"http://ergast.com/api/f1/{year}/results.json"
        results_response = requests.get(results_url)

        if results_response.status_code == 200:
            results_data = results_response.json()
            print(f"✅ Données des résultats récupérées pour {year} !")

            results = []
            for race in results_data['MRData']['RaceTable']['Races']:
                race_id = int(race['round'])

                for result in race['Results']:
                    driver_id = result['Driver']['driverId']
                    
                    # Vérifier si le pilote existe dans `drivers`
                    driver_exists = supabase.table("drivers").select("*").eq("driver_ref", driver_id).execute()
                    if len(driver_exists.data) == 0:
                        # Ajouter le pilote manquant
                        new_driver = {
                            "driver_ref": driver_id,
                            "number": None,
                            "code": None,
                            "first_name": result['Driver']['givenName'],
                            "last_name": result['Driver']['familyName'],
                            "dob": result['Driver'].get('dateOfBirth', None),
                            "nationality": result['Driver'].get('nationality', None),
                            "url": result['Driver'].get('url', None),
                        }
                        supabase.table("drivers").insert(new_driver).execute()
                        print(f"🔄 Pilote ajouté : {driver_id}")

                    # Ajouter les résultats
                    results.append({
                        "race_id": race_id,
                        "driver_id": driver_id,
                        "constructor": result['Constructor']['name'],
                        "grid": int(result['grid']),
                        "position": result.get('position', 'DNF'),
                        "points": float(result['points']),
                        "status": result['status']
                    })

            # Insérer les résultats
            supabase.table("results").insert(results).execute()
            print(f"✅ Données des résultats insérées pour {year} dans Supabase !")
        else:
            print(f"❌ Erreur récupération des résultats pour {year} : {results_response.status_code}")

# 📌 Exécuter les fonctions
reset_tables()
fetch_races_and_drivers()
fetch_results()

print("🚀 Script terminé avec succès sur Supabase API !")
