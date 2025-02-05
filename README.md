# 🏎️ Chatbot F1 avec Supabase & ChromaDB

Ce projet est un **chatbot intelligent** qui répond aux questions sur la **Formule 1** en utilisant des **données issues de l'API Ergast**, stockées dans **Supabase** et vectorisées avec **ChromaDB**. Il fonctionne avec **LangChain et OpenAI** pour générer des réponses basées sur un historique de conversation.

## 🚀 **Installation et Configuration**

### 1️⃣ **Prérequis**
Avant de commencer, assure-toi d'avoir installé :
- **Python 3.9+**
- **pip** (gestionnaire de paquets Python)
- **Git** (si tu veux cloner le repo)

### 2️⃣ **Cloner le projet**
```
git clone https://github.com/votre-utilisateur/MonProjetChatbot.git
cd MonProjetChatbot
```
3️⃣ Créer un environnement virtuel (optionnel mais recommandé)
```
python -m venv venv
source venv/bin/activate  # Pour macOS/Linux
venv\Scripts\activate     # Pour Windows
```
4️⃣ Installer les dépendances
```
pip install -r requirements.txt
```
5️⃣ Créer et configurer le fichier .env
Le projet utilise Supabase pour stocker les données et OpenAI pour générer des réponses.
Crée un fichier .env à la racine du projet et ajoute :
```
NEXT_PUBLIC_SUPABASE_URL="https://your-supabase-url.supabase.co"
NEXT_PUBLIC_SUPABASE_ANON_KEY="your-supabase-anon-key"
OPENAI_API_KEY="your-openai-api-key"
```
Remplace les valeurs par tes propres clés API.
👉 Ne partage jamais ce fichier publiquement !

🔄 Récupération des données F1 et stockage dans Supabase
Avant d'exécuter le chatbot, tu dois récupérer les données et les stocker dans Supabase.

📌 Exécute request.py pour récupérer et stocker les données :
```
python request.py
```
Ce script :

1- Vérifie quelles années de données sont déjà présentes.
2- Récupère les courses, pilotes et résultats depuis l'API Ergast.
3- Stocke les données dans Supabase.
💬 Lancer le Chatbot
Une fois les données chargées, exécute le chatbot interactif :
```
python chatbot.py
```
💡 Le chatbot :

- Charge les embeddings une seule fois depuis Supabase.
- Écoute en continu les nouveaux messages utilisateurs.
- Génère une réponse uniquement si le dernier message provient d’un utilisateur.
- Stocke les réponses du bot dans Supabase.
📌 Pour quitter le chatbot, tape simplement :
```
exit
```

🤝 Contribuer
Si tu souhaites améliorer ce projet :

Forke le repo sur GitHub.
Clone-le et crée une branche feature :
```
git checkout -b ma-nouvelle-fonctionnalité
```
Apporte tes modifications, commit et push :
```
git commit -m "Ajout d'une nouvelle feature"
git push origin ma-nouvelle-fonctionnalité
```
⚠️ Licence & Confidentialité
Ce projet est sous licence de MOI
⚠️ Ne partage jamais ta clé OpenAI ou Supabase publiquement !
