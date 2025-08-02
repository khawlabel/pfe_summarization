import os
import tempfile
import streamlit as st
import json
import re
from langdetect import detect, DetectorFactory
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from sentence_transformers import SentenceTransformer
from operator import itemgetter
from constants import *
from outils import *
from prompts_v0_5 import *
from langchain.retrievers import BM25Retriever
from langchain.schema import Document
from langchain.memory import ConversationBufferMemory
from numpy import dot

DetectorFactory.seed = 0  # Pour cohérence de détection de langue

st.set_page_config(page_title="5W1H Multilingue", layout="wide")
st.title("🧠 Analyse 5W1H + Vectorisation avec Groq & Qdrant")
MODEL_EMBEDDING2 = os.path.join(os.path.dirname(__file__), "./multilingual-e5-small")
# === Initialisations ===
@st.cache_resource
def get_embedding_model():
    return HuggingFaceEmbeddings(model_name=MODEL_EMBEDDING2)

embedding_model = get_embedding_model()
vector_size = embedding_model.client.get_sentence_embedding_dimension()

@st.cache_resource
def get_qdrant_client():
    return QdrantClient(QDRANT_URL, api_key=QDRANT_API)



@st.cache_resource
def load_llm1():
    return ChatGroq(groq_api_key=GROQ_API_KEY_1, model_name=LLM_NAME_4)
@st.cache_resource
def load_llm2():
    return ChatGroq(groq_api_key=GROQ_API_KEY_2, model_name=LLM_NAME_4)
@st.cache_resource
def load_llm3():
    return ChatGroq(groq_api_key=GROQ_API_KEY_3, model_name=LLM_NAME_4)

@st.cache_resource
def load_llm4():
    return ChatGroq(groq_api_key=GROQ_API_KEY_4, model_name=LLM_NAME_4)
@st.cache_resource
def load_llm5():
    return ChatGroq(groq_api_key=GROQ_API_KEY_5, model_name=LLM_NAME_4)

@st.cache_resource
def load_llm6():
    return ChatGroq(groq_api_key=GROQ_API_KEY_6, model_name=LLM_NAME_4)

@st.cache_resource
def load_llm7():
    return ChatGroq(groq_api_key=GROQ_API_KEY_7, model_name=LLM_NAME_4)
@st.cache_resource
def load_llm8():
    return ChatGroq(groq_api_key=GROQ_API_KEY_8, model_name=LLM_NAME_4)


llm1=load_llm1()
llm2=load_llm2()
llm3=load_llm3()
llm4=load_llm4()
llm5=load_llm5()
llm6=load_llm6()
llm7=load_llm7()
llm8=load_llm8()

client = get_qdrant_client()

if not client.collection_exists(QDRANT_COLLECTION):
    client.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

vectorstore = Qdrant(client=client, collection_name=QDRANT_COLLECTION, embeddings=embedding_model)


if "bm25_retriever" not in st.session_state:
    st.session_state.bm25_retriever = None

chain = prompt_5w1h | llm1 | StrOutputParser()
contxtualisation_chain = prompt_contxtualisation | llm2 | StrOutputParser()
answer_chain = prompt_answer | llm3 | StrOutputParser()
splitter = CharacterTextSplitter(chunk_size=750, chunk_overlap=100)
chain_resumer = ({"context": itemgetter("context"), "language": itemgetter("language")} | prompt_resumer | llm4 | StrOutputParser())
chain_traduction  = ({"resume_francais": itemgetter("resume_francais")} | prompt_traduction | llm5 | StrOutputParser())
chain_titre = ({"context": itemgetter("context"), "language": itemgetter("language")} | prompt_titre | llm6 | StrOutputParser())
chain_resumer_support = (
    {
        "summary": itemgetter("summary"),
        "support_summary_1": itemgetter("support_summary_1"),
        "support_summary_2": itemgetter("support_summary_2")
    } | prompt_support | llm7 | StrOutputParser()
)
chain_chat = ({"context": itemgetter("context"),"chat_history": itemgetter("chat_history"), "question": itemgetter("question")} | prompt_chat | llm8 | StrOutputParser())

uploaded_files = st.file_uploader("📎 Déposez vos fichiers (PDF, audio, vidéo)", type=["pdf", "mp3", "wav", "mp4", "avi", "mkv"], accept_multiple_files=True)

vectorstore2 = Qdrant(
    client=client,
    collection_name=QDRANT_COLLECTION_SUPPORT_3,
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
        collection_name=QDRANT_COLLECTION_SUPPORT_3,
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

if uploaded_files and st.button("🚀 Lancer toute l'analyse"):
    all_contexts = []
    bm25_docs = []

    # Nettoyage collection Qdrant
    if client.collection_exists(QDRANT_COLLECTION):
        client.delete_collection(QDRANT_COLLECTION)
    client.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

    # === Étape 1 : Extraction, vectorisation, contextualisation ===
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name) as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        try:
            text = extract_text(tmp_path)
            lang = detect(text)
            lang_label = "français" if lang == "fr" else "arabe" if lang == "ar" else "inconnue"

            all_contexts.append(f"[Nom du fichier : {uploaded_file.name} | Langue du fichier : {lang_label}]\n{text}")

            chunks = splitter.split_text(text)
            contextualized_versions = []
            metadatas = []

            for idx, chunk in enumerate(chunks):
                contextualized_chunk = contxtualisation_chain.invoke({
                    "context": text,
                    "chunk": chunk
                })
                fusion_text = contextualized_chunk + ": " + chunk

                metadata = {
                    "source": uploaded_file.name,
                    "lang": lang_label,
                    "chunk_id": idx,
                    "raw_chunk": chunk,
                    "contextualized_chunk": contextualized_chunk
                }

                contextualized_versions.append(fusion_text)
                metadatas.append(metadata)
                bm25_docs.append(Document(page_content=fusion_text, metadata=metadata))

            vectorstore.add_texts(contextualized_versions, metadatas=metadatas)
            st.success(f"✅ {uploaded_file.name} traité ({lang_label})")
            with st.expander(f"📃 Aperçu de {uploaded_file.name}"):
                st.write(text)

        except Exception as e:
            st.error(f"❌ Erreur avec {uploaded_file.name} : {e}")
        finally:
            os.remove(tmp_path)

    # Index BM25
    if bm25_docs:
        st.session_state.bm25_retriever = BM25Retriever.from_documents(bm25_docs)
        st.session_state.bm25_retriever.k = 2

    # === Étape 2 : Génération des questions 5W1H ===
    full_context = "\n\n".join(all_contexts)

    try:
        result = chain.invoke({"context": full_context})
        st.subheader("📌 Réponse brute du LLM (5w1h)")
        st.code(result, language="json")

        match = re.search(r"\{.*\}", result, re.DOTALL)
        if not match:
            st.error("❌ Impossible d’extraire un bloc JSON valide.")
            st.stop()

        json_str = match.group(0)
        parsed = json.loads(json_str)
        if "questions" not in parsed:
            st.error("❌ Clé 'questions' absente dans le JSON.")
            st.stop()

        st.success("✅ JSON extrait et valide.")
        st.session_state["questions_json"] = parsed

    except Exception as e:
        st.error(f"❌ Erreur pendant la génération des questions : {e}")
        st.stop()

    # === Étape 3 : Recherche hybride pour chaque question ===
    st.markdown("---")
    st.markdown("## 🔎 Résultats de recherche 5W1H")

    parsed = st.session_state["questions_json"]
    retriever_bm25 = st.session_state.bm25_retriever
    context=[]
    for w in ["who", "what", "when", "where", "why", "how"]:
        st.subheader(f"📍 {w.upper()}")
        pair = parsed["questions"].get(w, {})
        question_fr = pair.get("fr", "").strip()
        question_ar = pair.get("ar", "").strip()

        fr_chunks, ar_chunks = [], []
        
        for lang_key, question in pair.items():
            if question.strip():
                st.markdown(f"{lang_key.upper()}** — {question}")
                vectordocs = vectorstore.similarity_search(question, k=2)
                bm25docs = retriever_bm25.get_relevant_documents(question) if retriever_bm25 else []

                seen = set()
                merged = []
                for doc in vectordocs + bm25docs :
                    key = (doc.metadata.get("source"), doc.metadata.get("chunk_id"))
                    if key not in seen:
                        seen.add(key)
                        raw_chunk = doc.metadata.get("raw_chunk", doc.page_content)

                        if lang_key == "fr":
                            fr_chunks.append(raw_chunk)
                        elif lang_key == "ar":
                            ar_chunks.append(raw_chunk)

         # Appel au LLM pour générer la réponse fusionnée
        if question_fr or question_ar:
            try:
                response = answer_chain.invoke({
                    "question_fr": question_fr,
                    "fr_chunks": "\n".join(fr_chunks),
                    "question_ar": question_ar,
                    "ar_chunks": "\n".join(ar_chunks),
                })

                st.markdown("### 🧠 Réponse synthétisée du LLM")
                st.write(response)
                # Ou si c'est une liste :
                context.append(f"{w}: {response}")
            except Exception as e:
                st.error(f"❌ Erreur lors de l'appel LLM pour {w}: {e}")
                    
                 # Initialisation des sessions si elles n'existent pas
    if "summary_text" not in st.session_state:
        st.session_state["summary_text"] = {"fr": "", "ar": ""} 
        
    if "summary_text_support" not in st.session_state:
        st.session_state["summary_text_support"] = {"fr": "", "ar": ""} 
    

    with st.expander("📌 Résumé en Français", expanded=True):
                        # Générer le titre en streaming
        titre_fr_placeholder = st.empty()
        summary_fr_placeholder = st.empty()
        titre = ""
        resume = ""
        for chunk in chain_titre.stream({"context": context, "language": "francais"}):
            if chunk:
                titre += chunk
                titre_fr_placeholder.markdown(
                    f"""<div style="text-align: justify;"><strong>Titre</strong> : {titre}</div>""",
                    unsafe_allow_html=True
                )
        if not st.session_state["summary_text"]["fr"]:
            for chunk in chain_resumer.stream({"context": context, "language": "francais"}):
                if chunk:
                    resume += chunk
                    summary_fr_placeholder.markdown(
                        f"""<div style="text-align: justify;"><strong>Resumer</strong>:{resume}</div>""",
                        unsafe_allow_html=True
                    )
        else:
            summary_fr_placeholder.markdown(st.session_state["summary_text"]["fr"])
        st.session_state["summary_text"]["fr"] = f"Titre : {titre}\n\n*Résumé* : {resume}" 

    with st.expander("📌 Résumé en Français avec support", expanded=True):

        resultats = search_support(text, resume)
        resume_generer= st.session_state["summary_text"]["fr"]
        if resultats:
            for i, (resume_, score) in enumerate(resultats):
                st.markdown(f"*Résumé {i+1} (score = {score:.4f})*")
                st.write(resume_)
                st.markdown("---")
            support1 = resultats[0][0]
            support2 = resultats[1][0] if len(resultats) > 1 else ""
            summary_support_fr_placeholder = st.empty()
            resume_support = ""
            if not st.session_state["summary_text_support"]["fr"]:
                for chunk in chain_resumer_support.stream( {
                    "summary": resume_generer,
                    "support_summary_1": support1,
                    "support_summary_2": support2}):
                    if chunk:
                        resume_support += chunk
                        summary_support_fr_placeholder.markdown(
                            f"""<div style="text-align: justify;">
                                    <strong>Résumé avec support</strong> : {resume_support}
                                </div>""",
                            unsafe_allow_html=True
                        )    
            else:
                summary_support_fr_placeholder.markdown(st.session_state["summary_text_support"]["fr"])
        st.session_state["summary_text_support"]["fr"] = f"Titre : {titre}\n\n*Résumé* : {resume_support}"  
        
    with st.expander("📌 ملخص باللغة العربية", expanded=True):
        summary_ar_placeholder = st.empty()
        if not st.session_state["summary_text"]["ar"]:
            
            # 2. Améliorer le résumé en streaming et afficher uniquement le texte corrigé
            st.session_state["summary_text"]["ar"] = ""
            for chunk in chain_traduction.stream({"resume_francais": st.session_state["summary_text"]["fr"]}):
                if chunk:
                    st.session_state["summary_text"]["ar"] += chunk
                    summary_ar_placeholder.markdown(f'<div style="font-size: 21px; text-align: justify; direction: rtl; line-height: 1.5; font-family: \'Traditional Arabic\', sans-serif;">{st.session_state["summary_text"]["ar"]}</div>', unsafe_allow_html=True)

                else:
                    summary_ar_placeholder.markdown(f'<div style="font-size: 21px; text-align: justify; direction: rtl; line-height: 1.5; font-family: \'Traditional Arabic\', sans-serif;">{st.session_state["summary_text"]["ar"]}</div>', unsafe_allow_html=True)
    with st.expander("📌 ملخص باللغة العربية with support", expanded=True):
        summary_ar_support_placeholder = st.empty()
        if not st.session_state["summary_text_support"]["ar"]:
            
            # 2. Améliorer le résumé en streaming et afficher uniquement le texte corrigé
            st.session_state["summary_text_support"]["ar"] = ""
            for chunk in chain_traduction.stream({"resume_francais": st.session_state["summary_text_support"]["fr"]}):
                if chunk:
                    st.session_state["summary_text_support"]["ar"] += chunk
                    summary_ar_support_placeholder.markdown(f'<div style="font-size: 21px; text-align: justify; direction: rtl; line-height: 1.5; font-family: \'Traditional Arabic\', sans-serif;">{st.session_state["summary_text_support"]["ar"]}</div>', unsafe_allow_html=True)

                else:
                    summary_ar_support_placeholder.markdown(f'<div style="font-size: 21px; text-align: justify; direction: rtl; line-height: 1.5; font-family: \'Traditional Arabic\', sans-serif;">{st.session_state["summary_text_support"]["ar"]}</div>', unsafe_allow_html=True)

# === Partie chat : gestion du contexte, affichage et réponses ===

# Initialisation de l'historique de chat
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Affichage de l'historique de chat
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Boîte de saisie utilisateur
user_input = st.chat_input("Posez votre question ici...")
st.markdown("""
    <style>
        .stChatInput textarea {
            font-size: 18px !important;
            border-radius: 8px !important;
            padding: 10px !important;
        }
    </style>
""", unsafe_allow_html=True)

# Traitement de la requête utilisateur
if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
     # Création du contexte enrichi avec l'historique
    chat_history = "\n".join(
        [f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state["messages"] if msg['role'] != "system"]
    )
    with st.chat_message("user"):
        st.markdown(user_input)

    # Vérification sécurisée de l'existence du BM25 retriever
    retriever_bm25 = st.session_state.get("bm25_retriever", None)

    vectordocs = vectorstore.similarity_search(user_input, k=2)
    bm25docs = retriever_bm25.get_relevant_documents(user_input) if retriever_bm25 else []

    seen = set()
    context_chunks = []

    for doc in vectordocs + bm25docs:
        key = (doc.metadata.get("source"), doc.metadata.get("chunk_id"))
        if key not in seen:
            seen.add(key)
            context_chunks.append(doc.metadata.get("raw_chunk", doc.page_content))

    raw_chunk = "\n\n".join(context_chunks)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        response_stream = ""
        for chunk in chain_chat.stream({
            "context": raw_chunk,
            "chat_history": chat_history,
            "question": f"User: {user_input}\nAssistant:"
        }):
            if chunk:
                response_stream += chunk
                message_placeholder.markdown(response_stream)

        st.session_state["messages"].append({"role": "assistant", "content": response_stream})