Il programma si basa su Google API e Google Custom Search API e richiede un file config.py nella cartella src/pleiades con questa struttura:

import os

class Config:
    
    LLM_MODEL_LOW = nome del modello
    AI_API_URL = URL da fornire all'API dell'LLM
    AI_API_KEY = Chiave API
    SEARCH_API_KEY = Chiave API del motore di ricerca
    SEARCH_ENGINE_ID = Id del motore di ricerca

richiede di lanciare un "poetry install" e successivamente "run chainlit src/pleiades/__init__.py -w"
