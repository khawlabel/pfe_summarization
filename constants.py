
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Récupérer les clés API de manière sécurisée
QDRANT_API = os.getenv('QDRANT_API')
QDRANT_URL = os.getenv('QDRANT_URL')

GROQ_API_KEY = os.getenv('GROQ_API_KEY')

QDRANT_COLLECTION = os.getenv('QDRANT_COLLECTION')

# Modèles utilisés
LLM_NAME_1="llama3-8b-8192"
LLM_NAME_2="deepseek-r1-distill-qwen-32b"
LLM_correction="deepseek-r1-distill-llama-70b"
WHISPER="whisper-large-v3"
MODEL_EMBEDDING="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

PATH_tesseract = r"C:\Users\Dell\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
PATH_poppler = "C:/poppler/poppler-24.08.0/Library/bin"