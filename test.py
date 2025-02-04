import os
from fastapi import FastAPI, HTTPException
from supabase import create_client
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage
from dotenv import load_dotenv
from typing import List
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import Chroma

# Charger les variables d'environnement
load_dotenv()

# Clés API
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialiser Supabase et le modèle OpenAI
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
chat_model = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)

# Initialiser FastAPI
app = FastAPI()

# Fonction pour récupérer l'historique des messages depuis Supabase
def get_chat_history(chat_id: str) -> List:
    """Récupère l'historique des messages pour un chat_id donné."""
    response = supabase.table("messages").select("*").eq("chat_id", chat_id).order("id").execute()
    if response.error:
        raise HTTPException(status_code=500, detail=f"Erreur Supabase : {response.error.message}")
    
    messages = response.data
    history = []
    for message in messages:
        if message["role"] == "user":
            history.append(HumanMessage(content=message["content"]))
        elif message["role"] == "ia":
            history.append(AIMessage(content=message["content"]))
    return history

# Endpoint API pour interagir avec le chatbot
@app.post("/chat/")
async def chat(chat_id: str, user_input: str):
    """
    Endpoint pour interagir avec le chatbot.
    - `chat_id` : Identifiant de la conversation.
    - `user_input` : Message de l'utilisateur.
    """
    try:
        # Récupérer l'historique des messages
        context = get_chat_history(chat_id)

        # Ajouter le message utilisateur
        context.append(HumanMessage(content=user_input))

        # Obtenir la réponse du chatbot
        response = chat_model(messages=context)
        bot_response = response.content

        # Sauvegarder la réponse dans Supabase
        supabase.table("messages").insert({
            "id": None,  # UUID généré par Supabase
            "chat_id": chat_id,
            "role": "assistant",
            "content": bot_response
        }).execute()

        # Retourner la réponse
        return {"response": bot_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint de santé (pour vérifier que l'API fonctionne)
@app.get("/")
def health_check():
    return {"status": "ok"}
