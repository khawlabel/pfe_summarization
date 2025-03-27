import streamlit as st

# Configuration de la page
st.set_page_config(page_title="🧠 AI Assistant", layout="wide")

# Initialiser les variables de session
if "summarized_text" not in st.session_state:
    st.session_state.summarized_text = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar pour uploader plusieurs fichiers
st.sidebar.header("📂 Chargez vos fichiers : ")
uploaded_files = st.sidebar.file_uploader("Choisir des fichiers", type=["pdf", "mp3", "mp4"], accept_multiple_files=True)

# Bouton pour supprimer les fichiers et réinitialiser le résumé
if uploaded_files:
    if st.sidebar.button("🗑️ Supprimer tous les fichiers"):
        st.session_state.summarized_text = None  # Effacer le résumé
        st.session_state.messages = []  # Effacer l'historique des messages
        st.rerun()  # Rafraîchir la page pour tout effacer

# Sidebar pour sélectionner la langue de réponse
st.sidebar.header("🌍 Sélectionnez la langue de réponse :")
lang = st.sidebar.selectbox("Langue", ["", "Français", "Anglais", "Arabe"])  # Option vide par défaut

# ✅ ✅ ✅ Affichage des fichiers chargés sous forme d'alerte ✅ ✅ ✅
if uploaded_files and lang:
    file_names = ", ".join([file.name for file in uploaded_files])  
    st.success(f"📂 **Fichiers chargés avec succès :** {file_names}")  # Alerte verte

# ✅ Affichage des messages (historique)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ✅ Affichage du message du bot pour proposer le résumé
if uploaded_files and lang and st.session_state.summarized_text is None:
    st.markdown("---")  # Ligne de séparation
    with st.chat_message("assistant"):
        st.markdown("💡 **Vous pouvez générer un résumé en cliquant sur le bouton ci-dessous.**")

    # ✅ Centrer le bouton et ajuster la taille
    st.markdown(
        """
        <style>
        div.stButton > button {
            width: 250px;
            height: 50px;
            font-size: 18px;
            font-weight: bold;
            background-color: #4C585B;
            color: white;
            border-radius: 8px;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ✅ Centrage du bouton
    col1, col2, col3 = st.columns([2, 2, 2])
    with col2:
        if st.button("📄 Résumer"):
            summary_text = f"📄 **Résumé des fichiers** :\n\nLorem ipsum dolor sit amet..."
            st.session_state.summarized_text = summary_text  # Stocker le résumé
            st.session_state.messages.append({"role": "assistant", "content": summary_text})
            st.rerun()  # Rafraîchir la page

# ✅ Affichage du résumé généré sous forme de message du bot
if st.session_state.summarized_text:
    with st.chat_message("assistant"):
        st.markdown(st.session_state.summarized_text)

# ✅ Zone de chat en bas de la page
user_input = st.chat_input("Tapez votre message ici...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Simulation de réponse de l'IA (remplace par ton modèle)
    ia_response = f"🤖 Réponse de l'IA ({lang}) : Je traite votre message..."
    st.session_state.messages.append({"role": "assistant", "content": ia_response})

    with st.chat_message("assistant"):
        st.markdown(ia_response)

    st.rerun()  # Rafraîchir la page après chaque message
