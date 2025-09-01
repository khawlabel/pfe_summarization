import os
import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, Tool, AgentType
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import MessagesPlaceholder
from langchain_groq import ChatGroq
from operator import itemgetter
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional
from prompts_v0_5 import *
from constants import *

# === Config ===
MODEL_EMBEDDING = os.path.join(os.path.dirname(__file__), "./multilingual-e5-small")
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "./support_chroma/chroma_db")  # chemin unique

# === Initialisation Chroma ===
def init_chroma():
    # Modèle d’embedding
    embedding_model = HuggingFaceEmbeddings(model_name=MODEL_EMBEDDING)

    # Client persistant Chroma
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Vectorstore avec LangChain
    vectorstore = Chroma(
        client=client,
        collection_name=CHROMADB_COLLECTION,  # ⚠️ choisis ton nom de collection
        embedding_function=embedding_model
    )

    return client, embedding_model, vectorstore


# === Chargement LLM ===
def load_llm1():
    return ChatGroq(groq_api_key=GROQ_API_KEY_1, model_name=LLM_NAME_4)

def load_llm2():
    return ChatGroq(groq_api_key=GROQ_API_KEY_2, model_name=LLM_NAME_4)

