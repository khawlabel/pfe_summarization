import streamlit as st

# Configuration de la page
st.set_page_config(page_title="🧠 AI Assistant", layout="wide")

# Ajout du CSS pour la mise en page et les couleurs
st.markdown("""
    <style>
        /* Styles globaux */
        body {
            font-family: Arial, sans-serif;
        }

        /* Colonnes latérales gauche et droite */
        .left-sidebar {
            background-color: #cce5ff; /* Bleu clair */
            padding: 20px;
            border-radius: 10px;
            height: 100vh;  /* Prend toute la hauteur de la page */
        }

        .right-sidebar {
            background-color: #ffccdd; /* Rose clair */
            padding: 20px;
            border-radius: 10px;
            height: 100vh; /* Prend toute la hauteur de la page */
        }

        /* Contenu principal */
        .main-content {
            background-color: #ffffff; /* Blanc normal */
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Création de la disposition en colonnes
col1, col2, col3 = st.columns([1.5, 2, 1.5])

# 🎯 Barre latérale gauche (Bleu clair)
with col1:
    st.markdown('<div class="left-sidebar">', unsafe_allow_html=True)
    st.header("📂 Chargez vos fichiers :")
    uploaded_file = st.file_uploader("Choisir un fichier", type=["pdf", "mp3", "mp4"])

    st.header("🌍 Sélectionnez la langue :")
    lang = st.selectbox("Langue", ["", "Français", "Anglais", "Arabe"])  # Option vide par défaut
    st.markdown('</div>', unsafe_allow_html=True)

# 📌 Contenu principal (Blanc normal)
with col2:
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.title("🧠 AI Assistant")
    user_input = st.text_input("💬 Posez votre question ici...", key="chat_input")
    send_btn = st.button("Envoyer")
    st.markdown('</div>', unsafe_allow_html=True)

# 🔹 Barre latérale droite (Rose clair)
with col3:
    st.markdown('<div class="right-sidebar">', unsafe_allow_html=True)
    st.header("🔧 Paramètres")
    option1 = st.checkbox("Mode avancé")
    st.markdown('</div>', unsafe_allow_html=True)
