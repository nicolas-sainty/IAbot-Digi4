import os
import json
import requests
from supabase import create_client
from dotenv import load_dotenv

# 📌 Charger les variables d'environnement
load_dotenv()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

# 📌 Connexion à Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def fetch_all_drivers():
    """ Récupère tous les pilotes de 1950 à 2025 et les stocke dans un fichier JSON. """
    all_drivers = []
    seen_drivers = set()

    for year in range(1950, 2025):
        print(f"🔄 Récupération des pilotes pour {year}...")
        url = f"http://ergast.com/api/f1/{year}/drivers.json"
        response = requests.get(url)

        if response.status_code == 200:
            drivers_data = response.json().get("MRData", {}).get("DriverTable", {}).get("Drivers", [])

            for driver in drivers_data:
                driver_ref = driver["driverId"]

                # ⚠️ Éviter d'ajouter les mêmes pilotes plusieurs fois
                if driver_ref not in seen_drivers:
                    all_drivers.append({
                        "driver_ref": driver_ref,
                        "first_name": driver["givenName"],
                        "last_name": driver["familyName"],
                        "dob": driver["dateOfBirth"],
                        "nationality": driver["nationality"],
                        "url": driver["url"]
                    })
                    seen_drivers.add(driver_ref)

    # ✅ Sauvegarde des pilotes dans un fichier JSON
    with open("pilotes.json", "w", encoding="utf-8") as f:
        json.dump(all_drivers, f, indent=4, ensure_ascii=False)

    print(f"✅ {len(all_drivers)} pilotes enregistrés dans `pilotes.json` !")


def insert_drivers_from_file():
    """ Charge les pilotes depuis `pilotes.json` et les insère dans Supabase. """
    if not os.path.exists("pilotes.json"):
        print("❌ Le fichier `pilotes.json` n'existe pas. Lancez `fetch_all_drivers.py` d'abord !")
        return

    with open("pilotes.json", "r", encoding="utf-8") as f:
        drivers = json.load(f)

    if not drivers:
        print("⚠️ Aucun pilote à insérer.")
        return

    print(f"🔄 Insertion de {len(drivers)} pilotes dans Supabase...")
    supabase.table("drivers").upsert(drivers, on_conflict="driver_ref").execute()
    print(f"✅ Pilotes insérés avec succès !")


if __name__ == "__main__":
    fetch_all_drivers()
    insert_drivers_from_file()
