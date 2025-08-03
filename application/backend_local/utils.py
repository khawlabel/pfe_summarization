import os
import tempfile
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from qdrant_client.http.models import Filter, FilterSelector
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, Tool, AgentType
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import MessagesPlaceholder
from langchain_groq import ChatGroq
from operator import itemgetter
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional
import tempfile
from prompts_v0_4 import *
from constants import *


MODEL_EMBEDDING = os.path.join(os.path.dirname(__file__), "./multilingual-e5-small")

# Initialisation Qdrant
def init_qdrant():
    client = QdrantClient(QDRANT_URL, api_key=QDRANT_API)
    embedding_model = HuggingFaceEmbeddings(model_name=MODEL_EMBEDDING)
    vector_size = embedding_model.client.get_sentence_embedding_dimension()

    if not client.collection_exists(QDRANT_COLLECTION):
        client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

    vectorstore = Qdrant(client=client, collection_name=QDRANT_COLLECTION, embeddings=embedding_model)
    return client, embedding_model, vectorstore



