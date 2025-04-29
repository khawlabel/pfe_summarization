import streamlit as st
from operator import itemgetter
from langchain.agents import initialize_agent, Tool, AgentType
from qdrant_client.models import VectorParams, Distance
from langchain.agents import AgentExecutor
from qdrant_client import QdrantClient
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain_core.output_parsers import StrOutputParser
from constants import *
from outils import extract_text
from qdrant_client.http.models import Filter, FilterSelector
from prompts_v0_2 import *
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder


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
    return ChatGroq(groq_api_key=GROQ_API_KEY_4, model_name=llm_name)

llm = get_llm(LLM_NAME_4)

# Fonction pour récupérer le contexte pertinent
def retrieve_context_with_metadata(query):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})  # Récupère les 3 documents les plus pertinents
    retrieved_docs = retriever.invoke(query)
    return retrieved_docs
# 📌 Chaînes de traitement
chain_chat = ({"context": itemgetter("context"), "question": itemgetter("question")} | prompt_chat | llm | StrOutputParser())
chain_resumer = ({"context": itemgetter("context"), "language": itemgetter("language")} | prompt_resumer | llm | StrOutputParser())
# Outil de récupération de documents
def document_retrieval_tool(query):
    """Récupère les documents pertinents à partir de la base Qdrant et génère un résumé."""
    retrieved_docs = retrieve_context_with_metadata(query)
    context = " ".join([doc.page_content for doc in retrieved_docs])  # Combiner les textes des documents récupérés
    response = chain_chat.invoke({"context": context, "question": query})
    return response  # Retourner la sortie unique

chat_history = MessagesPlaceholder(variable_name="chat_history")

if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(
        memory_key="chat_history",
        #input_key="input",
       # output_key="output",
        return_messages=True
    )
memory = st.session_state.memory

# Définir les outils à utiliser par l'agent
tools = [
    Tool(
        name="Document Retrieval",
        func=document_retrieval_tool,
        description = "Récupère les informations pertinentes à partir des documents et répond aux questions des utilisateurs de manière claire, précise et structurée."

    )
]

# Initialiser l'agent avec des outils
if "agent" not in st.session_state:
    st.session_state.agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent_type=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        #system_prompt="You are an assistant named Mikey",
        memory=memory,
        agent_kwargs={
            "input_messages": [chat_history],
            "system_message": "You are an assistant named Mikey. You help users by retrieving relevant documents and remembering previous questions to assist in follow-ups.",
        },
        
    )

agent = st.session_state.agent


  
# Fonction pour générer un résumé via l'agent
def agent_chat(query, language="francais"):
    response = agent.run(query) 
    #memory.save_context({"input": query}, {"output": response})
    return response


# 🧠 Interface utilisateur interactive avec st.chat_input
st.title("🧠 Assistant IA - Chatbot")

# Initialiser ou récupérer l'historique de la conversation
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher les anciens messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Entrée utilisateur via st.chat_input
user_input = st.chat_input("Posez votre question ici...")

if user_input:
    # Afficher le message utilisateur
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Réponse de l'agent
    with st.chat_message("assistant"):
        with st.spinner("Analyse en cours..."):
            response = agent_chat(user_input)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
with st.sidebar:
    st.write("📚 Mémoire :")
    for m in memory.chat_memory.messages:
        st.markdown(f"**{m.type}**: {m.content}")