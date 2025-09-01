
import os
from dotenv import load_dotenv
import platform

# Charger les variables d'environnement
loaded = load_dotenv()

GROQ_API_KEY_1 = os.getenv('GROQ_API_KEY_1')
GROQ_API_KEY_2 = os.getenv('GROQ_API_KEY_2')
GROQ_API_KEY_3 = os.getenv('GROQ_API_KEY_3')

CHROMADB_COLLECTION = os.getenv('CHROMADB_COLLECTION')
CHROMADB_COLLECTION_SUPPORT_4= os.getenv('CHROMADB_COLLECTION_SUPPORT_4')


# Modèles utilisés
LLM_NAME_1="llama3-8b-8192"
LLM_NAME_2="deepseek-r1-distill-qwen-32b"
LLM_correction="deepseek-r1-distill-llama-70b"
LLM_NAME_3="deepseek-ai/deepseek-llm-7b-cha"
LLM_NAME_4="llama-3.3-70b-versatile"
WHISPER="whisper-large-v3"
model_local="qwen3:4b"
MODEL_EMBEDDING="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

MODEL_EMBEDDING_v1="sentence-transformers/all-MiniLM-L6-v2"
RERANKER_MODEL="BAAI/bge-reranker-v2-m3"

if platform.system() == "Windows":
    PATH_tesseract = r"C:\Users\Dell\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
    PATH_poppler = "C:/poppler/poppler-24.08.0/Library/bin"
else:
    PATH_tesseract = "/usr/bin/tesseract"  # Chemin par défaut dans Docker Linux
    PATH_poppler = None  # Pas nécessaire sous Linux si `pdf2image` fonctionne