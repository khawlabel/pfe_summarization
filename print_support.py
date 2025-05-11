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

st.title("📄 Tous les résumés dans Qdrant")

# Récupérer tous les points (résumés) de la collection
scroll_result = client.scroll(
    collection_name=QDRANT_COLLECTION_SUPPORT,
    limit=1000,  # ajuste selon le nombre total de documents
    with_payload=True
)

# Afficher les résumés
if scroll_result:
    for i, point in enumerate(scroll_result[0], 1):
        content = point.payload.get("page_content", "Résumé vide")
        st.markdown(f"**Résumé {i}:**")
        st.write(content)
        st.markdown("---")
else:
    st.warning("Aucun résumé trouvé dans la collection.")
