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
from prompts_v0_2 import *
from prompts_v1_khawla import *

## App-V0-2  ##

# 📌 Interface Streamlit
st.set_page_config(page_title="🧠 AI Assistant", layout="wide")

# 🔗 Connexion à Qdrant avec mise en cache
@st.cache_resource
def get_qdrant_client():
    return QdrantClient(QDRANT_URL, api_key=QDRANT_API)

client = get_qdrant_client()

@st.cache_resource
def get_embedding_model():
    return HuggingFaceEmbeddings(model_name=MODEL_EMBEDDING)

embedding_model = get_embedding_model()
vector_size = embedding_model.client.get_sentence_embedding_dimension()

if not client.collection_exists(QDRANT_COLLECTION):
    client.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

vectorstore = Qdrant(client=client, collection_name=QDRANT_COLLECTION, embeddings=embedding_model)

# 🔥 Chargement du modèle Groq avec mise en cache
@st.cache_resource
def get_llm(llm_name):
    return ChatGroq(groq_api_key=GROQ_API_KEY_2, model_name=llm_name)

llm = get_llm(LLM_NAME_1)
llm2=get_llm(LLM_NAME_4)
def clear_uploaded_files():
    """Réinitialisation des fichiers et de la session"""
    client.delete(collection_name=QDRANT_COLLECTION, points_selector=FilterSelector(filter=Filter(must=[])))
    st.session_state.clear()
    st.session_state["file_uploader"] = None
    st.markdown("<meta http-equiv='refresh' content='0'>", unsafe_allow_html=True) 
# 📂 Barre latérale pour uploader les fichiers
st.sidebar.header("📂 Upload your files:")
if "file_uploader_key" not in st.session_state:
    st.session_state["file_uploader_key"] = 0
if "submit_clicked" not in st.session_state:
    st.session_state["submit_clicked"] = False 
if "titles_per_file" not in st.session_state:
    st.session_state["titles_per_file"] = None
if "resumes_per_file" not in st.session_state:
    st.session_state["resumes_per_file"] = []

uploaded_files = st.sidebar.file_uploader(
    "Choose your files ",
    type=["pdf",".mp3", ".wav", ".ogg", ".flac", ".m4a",".mp4", ".avi", ".mov", ".mkv"],
    accept_multiple_files=True,
    key=f"file_uploader_{st.session_state['file_uploader_key']}",
)

# 🔘 Boutons de contrôle
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("🗑 Reset all"):
        clear_uploaded_files()
        st.session_state["submit_clicked"] = False  # Reset Submit

with col2:
    if st.button("✅ Submit"):
        st.session_state["submit_clicked"] = True  # Activer le stockage

# 📌 Initialisation des sessions
st.session_state.setdefault("messages", [])
st.session_state.setdefault("processed_files", set())
st.session_state.setdefault("summary_generated", False)
if "summary_ready" not in st.session_state:
    st.session_state["summary_ready"] = False
st.session_state.setdefault("retrieved_contexts", [])




def process_and_store_file(file):
    """Extrait le texte du fichier et stocke les embeddings"""
    suffix = os.path.splitext(file.name)[1]
    file_type = suffix.lstrip(".")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(file.read())
        temp_file_path = temp_file.name

    try:
        text = extract_text(temp_file_path)
        if text:
            vectorstore.add_texts([text], metadatas=[{"file_name": file.name, "file_type": file_type}])
            st.session_state["processed_files"].add(file.name)
    except ValueError as e:
        st.error(f"⚠ Extraction error: {e}")
    finally:
        os.remove(temp_file_path)

def retrieve_context_with_metadata_file(query, file_name=None):
    """Récupère le contexte pertinent pour la requête, éventuellement filtré par fichier"""
    retriever = vectorstore.as_retriever(search_kwargs={"k": len(st.session_state["processed_files"])})
    retrieved_docs = retriever.invoke(query)

    if file_name:
        # Ne garder que les documents liés à ce fichier
        retrieved_docs = [doc for doc in retrieved_docs if doc.metadata.get("file_name") == file_name]

    formatted_context = "\n\n".join(
        [
            f"📂 *Fichier*: {doc.metadata.get('file_name', 'Inconnu')}\n"
            f"📄 *Type*: {doc.metadata.get('file_type', 'Inconnu')}\n"
            f"🔹 *Contenu*:\n{doc.page_content}"
            for doc in retrieved_docs
        ]
    )

    return formatted_context


def document_retrieval_tool(query: str) -> str:
    context = st.session_state.get("retrieved_context", "")
    prompt = f"Contexte :\n{context}\n\nQuestion : {query}"
    return prompt  # C'est ce que l'agent envoie ensuite au LLM

# Définir les outils à utiliser par l'agent
tools = [
    Tool(
        name="Document Retrieval",
        func=document_retrieval_tool,
        description = "Récupère les informations pertinentes à partir des documents et répond aux questions des utilisateurs de manière claire, précise et structurée."

    )
]

# Initialiser l'agent avec des outils
agent = initialize_agent(
    tools=tools,
    llm=llm2,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True  # Activer cette option
)


# 📌 Chaînes de traitement
chain_chat = ({"context": itemgetter("context"), "question": itemgetter("question")} | prompt_chat | llm | StrOutputParser())
chain_titre = ({"context": itemgetter("context"), "language": itemgetter("language")} | prompt_titre | llm | StrOutputParser())
chain_resumer = ({"context": itemgetter("context"), "language": itemgetter("language")} | prompt_resumer | llm | StrOutputParser())
chain_ameliore_ar  = ({"texte_brut": itemgetter("texte_brut")} | prompt_ameliore_ar | llm2| StrOutputParser())
chain_traduction  = ({"resume_francais": itemgetter("resume_francais")} | prompt_traduction | llm2| StrOutputParser())
chain_resumer_general=({"context": itemgetter("context"), "language": itemgetter("language")} | prompt_resumer_general | llm | StrOutputParser())
chain_titre_general=({"context": itemgetter("context"), "language": itemgetter("language")} | prompt_titre_general | llm | StrOutputParser())

memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")

# 🛑 Suppression des données uniquement si tous les fichiers ont été supprimés manuellement
if not uploaded_files and st.session_state["processed_files"]:
    client.delete(collection_name=QDRANT_COLLECTION, points_selector=FilterSelector(filter=Filter(must=[])))
    st.session_state["processed_files"].clear()  # Réinitialisation des fichiers traités
    st.session_state["summary_generated"] = False  # Autoriser une nouvelle génération de résumé
    st.session_state.pop("summary_text", None)  # Supprime l'ancien résumé s'il existe
    st.session_state["messages"] = []  # Réinitialise les messages du chat
    st.session_state.setdefault("retrieved_contexts", [])
    st.session_state["titles_per_file"] = None
    st.session_state["resumes_per_file"] = []

# 🛑 Suppression des données une seule fois
if uploaded_files and not st.session_state["summary_generated"]:
    client.delete(collection_name=QDRANT_COLLECTION, points_selector=FilterSelector(filter=Filter(must=[])))
    st.session_state["summary_generated"] = True

# 📌 Traitement des fichiers uploadés
if uploaded_files and st.session_state["submit_clicked"]:
    for file in uploaded_files:
        if file.name not in st.session_state["processed_files"]:
            process_and_store_file(file)

    # 📖 Génération du résumé seulement si de nouveaux fichiers sont présents
    if uploaded_files:
        query = "Fais un résumé clair et structuré des informations disponibles."
        for idx, uploaded_file in enumerate(uploaded_files):
            context = retrieve_context_with_metadata_file(query, file_name=uploaded_file.name)

            st.session_state["retrieved_contexts"].append(context)

            # Générer le résumé
            resume = ""
            for chunk in chain_resumer.stream({"context": context, "language": "francais"}):
                if chunk:
                    resume += chunk
            print(uploaded_file.name,"resumer: ",resume)

            st.session_state["resumes_per_file"].append(resume)

        # Initialisation des sessions si elles n'existent pas
        if "summary_text" not in st.session_state:
            st.session_state["summary_text"] = {"fr": "", "ar": ""} 
        st.markdown('<h2 style="font-size: 22px;">📖 Résumé des documents</h2>', unsafe_allow_html=True)
        st.divider()  # Ligne de séparation visuelle

        # 📌 *Résumé en Français*
        with st.expander("📌 *Résumé en Français*", expanded=True):
            summary_fr_placeholder = st.empty()

            if not st.session_state["summary_text"]["fr"]:
                # Cas de plusieurs fichiers → faire appel à titre/résumé global
                all_resumes = "\n\n".join(st.session_state["resumes_per_file"])
                # Générer le titre en streaming
                titre = ""
                for chunk in chain_titre_general.stream({"context": all_resumes, "language": "francais"}):
                    if chunk:
                        titre += chunk
                        summary_fr_placeholder.markdown(
                            f"""<div style="text-align: justify;"><strong>Titre</strong> : {titre}</div>""",
                            unsafe_allow_html=True
                        )
                st.session_state["titles_per_file"]=titre
                if len(uploaded_files) == 1:
                    # Cas d’un seul fichier → utiliser le résumé déjà généré
                    titre = st.session_state["titles_per_file"]
                    resume = st.session_state["resumes_per_file"][0]

                    summary_fr_placeholder.markdown(
                        f"""<div style="text-align: justify;">
                                <strong>Titre</strong> : {titre}<br><br>
                                <strong>Résumé</strong> : {resume}
                            </div>""",
                        unsafe_allow_html=True
                    )

                    st.session_state["summary_text"]["fr"] = f"*Titre* : {titre}\n\n*Résumé* : {resume}"
                else:
                    all_resumes = "\n\n".join(st.session_state["resumes_per_file"])
                    titre = st.session_state["titles_per_file"]
                    # Générer le résumé en streaming
                    resume = ""
                    for chunk in chain_resumer_general.stream({"context": all_resumes, "language": "francais"}):
                        if chunk:
                            resume += chunk
                            summary_fr_placeholder.markdown(
                                f"""<div style="text-align: justify;">
                                        <strong>Titre</strong> : {titre}<br><br>
                                        <strong>Résumé</strong> : {resume}
                                    </div>""",
                                unsafe_allow_html=True
                            )

                    st.session_state["summary_text"]["fr"] = f"*Titre* : {titre}\n\n*Résumé* : {resume}"

                # 📌 *Résumé en Arabe*
        with st.expander("📌 *ملخص باللغة العربية*", expanded=True):
            summary_ar_placeholder = st.empty()

            if not st.session_state["summary_text"]["ar"]:
                # 1. Générer le résumé brut en une seule fois (pas de streaming ici)
                st.session_state["summary_text"]["ar"] = ""
                for chunk in chain_traduction.stream({"resume_francais": st.session_state["summary_text"]["fr"]}):
                    if chunk:
                        st.session_state["summary_text"]["ar"] += chunk
                        summary_ar_placeholder.markdown(f'<div style="font-size: 21px; text-align: justify; direction: rtl; line-height: 1.5; font-family: \'Traditional Arabic\', sans-serif;">{st.session_state["summary_text"]["ar"]}</div>', unsafe_allow_html=True)

            else:
                summary_ar_placeholder.markdown(f'<div style="font-size: 21px; text-align: justify; direction: rtl; line-height: 1.5; font-family: \'Traditional Arabic\', sans-serif;">{st.session_state["summary_text"]["ar"]}</div>', unsafe_allow_html=True)


        # Réinitialiser le bouton Submit après la génération du résumé
        st.session_state["submit_clicked"] = False

        st.session_state["summary_ready"] = True  # Indiquer que le résumé est prêt


    # 💬 *Message après le résumé*
    st.markdown('<h3 style="font-size: 20px;">💬 <b>Vous pouvez maintenant poser vos questions dans le chat ci-dessous</b></h3>', unsafe_allow_html=True)
elif "summary_text" in st.session_state :  # S'affiche uniquement si un résumé existe et qu'aucun fichier n'est uploadé
    st.markdown('<h2 style="font-size: 22px;">📖 Résumé des documents</h2>', unsafe_allow_html=True)
    st.divider()  # Ligne de séparation visuelle

    with st.expander("📌 *Résumé en Français*", expanded=True):
        st.markdown(  f'''
                    <div style="text-align: justify;">
                        {st.session_state["summary_text"]["fr"]}
                    </div>
                    ''', 
                    unsafe_allow_html=True
                )

    with st.expander("📌 *ملخص باللغة العربية*", expanded=True):
        st.markdown(f'<div style="font-size: 21px; text-align: justify; direction: rtl; line-height: 1.5; font-family: \'Traditional Arabic\', sans-serif;">{st.session_state["summary_text"]["ar"]}</div>', unsafe_allow_html=True)

    st.markdown('<h3 style="font-size: 20px;">💬 <b>Vous pouvez maintenant poser vos questions dans le chat ci-dessous</b></h3>', unsafe_allow_html=True)


# 🔄 Affichage des messages existants
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ✅ *Activation du chat après le résumé*

user_input = st.chat_input(
    "Ask your questions here..." if st.session_state["summary_ready"] else "❌ Please upload and submit a file first.", 
    disabled=not st.session_state["summary_ready"]
)
st.markdown("""
    <style>
        .stChatInput textarea {
            font-size: 18px !important;
            border-radius: 8px !important;
            padding: 10px !important;
          
        }
    </style>
""", unsafe_allow_html=True)
if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})

     # Création du contexte enrichi avec l'historique
    chat_history = "\n".join(
        [f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state["messages"] if msg['role'] != "system"]
    )

    context = st.session_state["retrieved_contexts"]

    with st.chat_message("user"):
        st.markdown(user_input) 
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        response_stream = ""

        response = agent.run(user_input)
        message_placeholder.markdown(response)

        st.session_state["messages"].append({"role": "assistant", "content": response})