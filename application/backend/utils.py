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
from outils import extract_text  # (ou ailleurs si tu l’as)

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

# Chargement LLM
def load_llm():
    return ChatGroq(groq_api_key=GROQ_API_KEY_3, model_name=LLM_NAME_1)

def load_llm2():
    return ChatGroq(groq_api_key=GROQ_API_KEY_3, model_name=LLM_NAME_4)

# Mémoire
def get_memory():
    return ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

# Agent avec outils
def init_agent(llm, llm2, memory, vectorstore):
    def document_retrieval_tool(query: str) -> str:
        context = "\n\n".join(st.session_state.get("retrieved_contexts", []))
        return f"Contexte :\n{context}\n\nQuestion : {query}"

    def outil_consulter_memoire(_):
        messages = memory.chat_memory.messages
        if not messages:
            return "La mémoire est actuellement vide."
        historique = []
        for msg in messages:
            role = "👤 Utilisateur" if msg.type == "human" else "🤖 Assistant"
            historique.append(f"{role} : {msg.content}")
        return "\n\n".join(historique)

    tools = [
        Tool(name="Document Retrieval", func=document_retrieval_tool,
             description="Récupère les infos pertinentes à partir des documents."),
        Tool(name="Consulter la mémoire", func=outil_consulter_memoire,
             description="Consulte l’historique de la conversation.")
    ]

    return initialize_agent(
        tools=tools,
        llm=llm2,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        memory=memory
    )


