import streamlit as st
import tempfile
import os
from operator import itemgetter
from qdrant_client import QdrantClient
from langchain_groq import ChatGroq
from qdrant_client.models import VectorParams, Distance
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain_core.output_parsers import StrOutputParser
from constants import *
from outils import extract_text
from qdrant_client.http.models import Filter, FilterSelector
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, Tool, AgentType
from prompts_v0_3 import *
from langchain.prompts import MessagesPlaceholder


def get_qdrant_client():
    return QdrantClient(QDRANT_URL, api_key=QDRANT_API)

client = get_qdrant_client()

def get_embedding_model():
    return HuggingFaceEmbeddings(model_name=MODEL_EMBEDDING)

embedding_model = get_embedding_model()
vector_size = embedding_model.client.get_sentence_embedding_dimension()

if not client.collection_exists(QDRANT_COLLECTION_SUPPORT):
    client.create_collection(
        collection_name=QDRANT_COLLECTION_SUPPORT,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

vectorstore = Qdrant(client=client, collection_name=QDRANT_COLLECTION_SUPPORT, embeddings=embedding_model)

import json

# Charger les résumés depuis le fichier JSON
file_path = os.path.join(os.path.dirname(__file__), "support.json")
with open(file_path, "r", encoding="utf-8") as f:
    resumes = json.load(f)

# Créer les documents au format attendu
from langchain.schema import Document

documents = [Document(page_content=resume) for resume in resumes]

# Ajouter les documents dans la collection Qdrant
vectorstore.add_documents(documents)
