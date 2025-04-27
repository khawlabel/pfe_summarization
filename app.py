import streamlit as st
from outils_v1 import *
from constants import *
from langchain.embeddings import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from qdrant_client.http.models import Filter, FilterSelector
from langchain_groq import ChatGroq
from langchain_community.vectorstores import Qdrant
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from prompts_v1 import *
import re
from prompts_v0_2 import *


# deploy V1

# Interface Streamlit
st.set_page_config(page_title="🧠 AI Assistant PDF", layout="wide")

# Initialisation du cache
@st.cache_resource
def get_qdrant_client():
    return QdrantClient(QDRANT_URL, api_key=QDRANT_API)

@st.cache_resource
def get_embedding_model():
    return HuggingFaceEmbeddings(model_name=MODEL_EMBEDDING)

@st.cache_resource
def get_llm(llm_name):
    return ChatGroq(groq_api_key=GROQ_API_KEY_4, model_name=llm_name)


@st.cache_resource
def get_reranker_model(model_name):
    return HuggingFaceCrossEncoder(model_name=model_name)

# Clients et modèles
client = get_qdrant_client()
embedding_model = get_embedding_model()
vector_size = embedding_model.client.get_sentence_embedding_dimension()

# Création collection si besoin
if not client.collection_exists(QDRANT_COLLECTION_v1):
    client.create_collection(
        collection_name=QDRANT_COLLECTION_v1,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

vectorstore = Qdrant(client=client, collection_name=QDRANT_COLLECTION_v1, embeddings=embedding_model)
llm = get_llm(LLM_NAME_4)
reranker_model = get_reranker_model("BAAI/bge-reranker-v2-m3")
chain_client = ({"context": itemgetter("context"), "user_query": itemgetter("user_query")} | prompt_client | llm | StrOutputParser())
chain_titre = ({"context": itemgetter("context"), "language": itemgetter("language")} | prompt_titre | llm | StrOutputParser())
chain_resumer = ({"context": itemgetter("context"), "language": itemgetter("language")} | prompt_resumer | llm | StrOutputParser())
chain_resumer_general=({"context": itemgetter("context"), "language": itemgetter("language")} | prompt_resumer_general | llm | StrOutputParser())
chain_titre_general=({"context": itemgetter("context"), "language": itemgetter("language")} | prompt_titre_general | llm | StrOutputParser())

# 🔁 Réinitialisation
def clear_uploaded_files():
    client.delete(collection_name=QDRANT_COLLECTION_v1, points_selector=FilterSelector(filter=Filter(must=[])))
    st.session_state.clear()
    st.session_state["file_uploader"] = None
    st.markdown("<meta http-equiv='refresh' content='0'>", unsafe_allow_html=True)


# Mémoire temporaire des articles originaux (non chunkés)
if "articles_originaux" not in st.session_state:
    st.session_state["articles_originaux"] = {}

if "submit_clicked" not in st.session_state:
    st.session_state["submit_clicked"] = False  # ⚡ État du bouton Submit

st.sidebar.title("🗂️ Chargement PDF")
uploaded_files = st.sidebar.file_uploader("📥 Charger des PDF", type="pdf", accept_multiple_files=True)

# 🔘 Boutons de contrôle
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("🗑️ Reset all"):
        clear_uploaded_files()
        st.session_state["submit_clicked"] = False  # Reset Submit

with col2:
    if st.button("✅ Submit"):
        st.session_state["submit_clicked"] = True  # Activer Submit


if uploaded_files and not st.session_state.get("submit_clicked", False):
    st.sidebar.info("📂 Cliquez sur '✅ Submit' pour traiter les fichiers.")

# Traitement du PDF
if uploaded_files and st.session_state.get("submit_clicked", False):

    # 💬 Poser UNE SEULE FOIS la question AVANT le traitement
    query = st.text_input("💬 Posez votre question pour TOUS les PDFs :")

    if query:
        titres_generaux_par_pdf = []
        resumes_generaux_par_pdf = []

        for idx, uploaded_file in enumerate(uploaded_files):
            st.sidebar.header(f"📄 Fichier {idx+1} : {uploaded_file.name}")

            with st.container():
                # 🔥 Avant de traiter ce fichier : vider la collection
                client.delete(collection_name=QDRANT_COLLECTION_v1, points_selector=FilterSelector(filter=Filter(must=[])))

                # 🔄 Extraction et indexation
                articles_nettoyes = extraire_articles_pdf(uploaded_file)
                articles_decoupes = separer_articles(articles_nettoyes)

                for article in articles_decoupes:
                    article["pdf_name"] = uploaded_file.name

                st.session_state[f"articles_originaux_{uploaded_file.name}"] = {
                    a["id"]: {"contenu": a["contenu"], "pdf_name": a["pdf_name"]} for a in articles_decoupes
                }
                # ➡️ Indexation
                with st.spinner("🔄 Indexation des articles..."):
                    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
                    seen_chunks = set()
                    all_chunks = []

                    for article in articles_decoupes:
                        if "contenu" not in article or not article["contenu"]:
                            continue
                        chunks = splitter.split_text(article["contenu"])
                        docs = []
                        for i, chunk in enumerate(chunks):
                            clean_chunk = chunk.strip()
                            if clean_chunk not in seen_chunks:
                                seen_chunks.add(clean_chunk)
                                docs.append(Document(
                                    page_content=clean_chunk,
                                    metadata={"source_id": article["id"], "chunk_id": i, "pdf_name": article["pdf_name"]}
                                ))
                        if docs:
                            vectorstore.add_documents(docs)

                st.success(f"✅ {uploaded_file.name} indexé.")

                # 🔍 Faire la recherche AVEC la même question
                retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 20, "fetch_k": 40})
                compressor = CrossEncoderReranker(model=reranker_model, top_n=8)
                compression_retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=retriever)

                matching_chunks = compression_retriever.invoke(query)


                if matching_chunks:
                    ids_utilises = set()  # Initialiser un set pour éviter les doublons
                    for chunk in matching_chunks:
                        ids_utilises.add(chunk.metadata.get("source_id"))
                    #st.info(f"📰 Articles correspondants dans {uploaded_file.name} : {len(ids_utilises)}")

                    st.subheader(f"Réponses pour {uploaded_file.name}")
                    response_placeholder = st.empty()  # Placeholder unique pour toute la réponse
                    response_stream = ""  # Réponse en streaming

                    # 📝 Stocker tous les titres et tous les résumés
                    tous_les_titres = []
                    tous_les_resumes = []

                    context_blocks = []
                    for source_id in ids_utilises:
                        article_data = st.session_state[f"articles_originaux_{uploaded_file.name}"].get(source_id, {})
                        if article_data:
                            article_stream=""
                            header = f"=== Article {source_id} (Nom du journal : {article_data['pdf_name']}) === \n"
                            context_article=f"{header}\n{article_data['contenu']}"

                            for chunk in chain_client.stream({
                                "user_query": query,
                                "context": context_article
                            }):
                                response_stream += chunk
                                response_placeholder.markdown(
                                            f"""<div style="text-align: justify;"> {response_stream}</div>""",
                                            unsafe_allow_html=True
                                        )
                                article_stream += chunk  
                            # Ajouter un saut de ligne après la réponse d'un article

                            response_stream += "\n\n"  # Ajout d'un saut de ligne pour séparer les articles

                        if not article_data:
                            continue

                        # Vérifier si response_stream est une courte phrase entre parenthèses

                        text = article_stream.strip()
                        # Condition pour détecter
                        if text.startswith("(") and text.endswith(")"):
                            pass
                        else:
                            st.subheader(f"=== Article {source_id} ===")
                            # 📤 Générer le titre pour cet article
                            titre = ""
                            for chunk in chain_titre.stream({"context": article_stream, "language": "francais"}):
                                if chunk:
                                    titre += chunk

                            # 📤 Générer le résumé normal pour cet article
                            resume = ""
                            for chunk in chain_resumer.stream({"context": article_stream, "language": "francais"}):
                                if chunk:
                                    resume += chunk

                            st.markdown(
                                f"""<div style="text-align: justify;">
                                        <strong>Titre</strong> : {titre}<br><br>
                                        <strong>Résumé normal</strong> : {resume}<br><br>
                                    </div>""",
                                unsafe_allow_html=True
                            )

                            # ➡️ Ajouter le titre et le résumé à nos listes
                            tous_les_titres.append(titre)
                            tous_les_resumes.append(resume)

                        # 🧠 ➡️ Après avoir parcouru tous les articles :

                    if tous_les_titres and tous_les_resumes:
                        st.subheader("=== Synthèse générale ===")

                        # 🔹 Concaténer tous les titres pour générer UN titre général
                        titres_concatenes = "\n".join(tous_les_titres)
                        titre_general = ""
                        for chunk in chain_titre_general.stream({"context": titres_concatenes, "language": "francais"}):
                            if chunk:
                                titre_general += chunk

                        # 🔹 Concaténer tous les résumés pour générer UN résumé général
                        resumes_concatenes = "\n".join(tous_les_resumes)
                        resume_general_final = ""
                        for chunk in chain_resumer_general.stream({"context": resumes_concatenes, "language": "francais"}):
                            if chunk:
                                resume_general_final += chunk

                        # ➡️ Afficher le titre général et le résumé général final
                        st.markdown(
                            f"""<div style="text-align: justify;">
                                    <h2>Titre Général :</h2>
                                    <p><strong>{titre_general}</strong></p><br>
                                    <h2 >Résumé Général :</h2>
                                    <p><strong>{resume_general_final}</strong></p><br>
                                </div>""",
                            unsafe_allow_html=True
                        ) 
                        titres_generaux_par_pdf.append(titre_general)
                        resumes_generaux_par_pdf.append(resume_general_final)
   

                                
                else:
                    st.warning(f"😕 Aucun chunk pertinent trouvé dans {uploaded_file.name}.")
                    
        if len(titres_generaux_par_pdf) > 1 and len(resumes_generaux_par_pdf) > 1:
            st.subheader("=== Synthèse Finale sur tous les PDF ===")
            # 🔹 Concaténer tous les titres généraux
            tous_les_titres_concatenes = "\n".join(titres_generaux_par_pdf)
            titre_final_global = ""
            for chunk in chain_titre_general.stream({"context": tous_les_titres_concatenes, "language": "francais"}):
                if chunk:
                    titre_final_global += chunk

            # 🔹 Concaténer tous les résumés généraux
            tous_les_resumes_concatenes = "\n".join(resumes_generaux_par_pdf)
            resume_final_global = ""
            for chunk in chain_resumer_general.stream({"context": tous_les_resumes_concatenes, "language": "francais"}):
                if chunk:
                    resume_final_global += chunk

            st.markdown(
                f"""<div style="text-align: justify;">
                        <h2>Titre Final Global :</h2>
                        <p><strong>{titre_final_global}</strong></p><br>
                        <h2>Résumé Final Global :</h2>
                        <p><strong>{resume_final_global}</strong></p><br>
                    </div>""",
                unsafe_allow_html=True
            )
