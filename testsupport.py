import streamlit as st
from qdrant_client import QdrantClient
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from numpy import dot
from constants import *
from langchain_groq import ChatGroq
from promptsarticle import prompt_support
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter
import numpy as np

# Config
st.set_page_config(page_title="Test Support", layout="wide")

@st.cache_resource
def get_client():
    return QdrantClient(QDRANT_URL, api_key=QDRANT_API)
client = get_client()

@st.cache_resource
def get_embeddings():
    return HuggingFaceEmbeddings(model_name=MODEL_EMBEDDING)
embedding_model = get_embeddings()

vectorstore2 = Qdrant(
    client=client,
    collection_name=QDRANT_COLLECTION_SUPPORT_2,
    embeddings=embedding_model,
)

def embed_text(text):
    return embedding_model.embed_query(text)

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def search_support(contenu, resume_draft, alpha=0.7, beta=0.3, top_k=2):
    emb_contenu = embed_text(contenu)
    emb_resume = embed_text(resume_draft)
    points, _ = client.scroll(
        collection_name=QDRANT_COLLECTION_SUPPORT_2,
        limit=20,
        with_vectors=True,
        with_payload=True
    )
    results = []
    for p in points:
        vec_source = p.payload.get("embedding_source_like")
        vec_resume = p.payload.get("embedding_resume")
        if vec_source is None or vec_resume is None:
            continue
        score = alpha * cosine_similarity(emb_contenu, vec_source) + beta * cosine_similarity(emb_resume, vec_resume)
        results.append((p.payload.get("resume"), score))
    return sorted(results, key=lambda x: x[1], reverse=True)[:top_k]

@st.cache_resource
def get_llm():
    return ChatGroq(groq_api_key=GROQ_API_KEY_3, model_name=LLM_NAME_4)
llm = get_llm()

chain_resumer_support = (
    {
        "summary": itemgetter("summary"),
        "support_summary_1": itemgetter("support_summary_1"),
        "support_summary_2": itemgetter("support_summary_2")
    } | prompt_support | llm | StrOutputParser()
)

# Interface de test
st.title("🔧 Test de Support")

contenu = st.text_area("Contenu du fichier")
resume_draft = st.text_area("Résumé à valider")
if st.button("Tester le support"):
    resultats = search_support(contenu, resume_draft)
    
    if resultats:
        st.subheader("📄 Résumés sélectionnés avec leurs scores :")
        for i, (resume, score) in enumerate(resultats):
            st.markdown(f"**Résumé {i+1} (score = {score:.4f})**")
            st.write(resume)
            st.markdown("---")
        
        support1 = resultats[0][0]
        support2 = resultats[1][0] if len(resultats) > 1 else ""
        
        output = chain_resumer_support.invoke({
            "summary": resume_draft,
            "support_summary_1": support1,
            "support_summary_2": support2
        })
        
        st.success("📝 Résumé final :")
        st.write(output)
    else:
        st.warning("Aucun support trouvé.")
