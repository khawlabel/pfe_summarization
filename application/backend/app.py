import os
import sqlite3
from datetime import datetime, timedelta
from typing import List
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel
import jwt
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from email.mime.multipart import MIMEMultipart
from utils import *
import uuid
import asyncio
from outils import *
from fastapi.responses import StreamingResponse
from langchain.memory import ConversationBufferMemory
from qdrant_client.http.models import Filter, FilterSelector
from fastapi.middleware.cors import CORSMiddleware
from numpy import dot
import numpy as np
from fastapi import Header
from translation import translations
from langchain.retrievers import BM25Retriever
from langchain.schema import Document
from numpy import dot
from langchain.text_splitter import CharacterTextSplitter
from langdetect import detect, DetectorFactory
import json
from prompts_v0_4 import *
DetectorFactory.seed = 0  # Pour cohérence de détection de langue

# Charger les variables d'environnement
load_dotenv()

# ================= Configuration =================

SECRET_KEY ="mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DB_PATH ="users.db"

app = FastAPI()

origins = [
    "http://172.25.224.1:3000",
    "http://localhost:3000",
    "http://localhost:3000/",
    "http://frontend:3000",  # <- à ajouter pour que Docker accepte les requêtes du frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # liste précise d'origines
    allow_credentials=True,           # autoriser les cookies et authentification
    allow_methods=["*"],              # méthodes HTTP autorisées
    allow_headers=["*"],              # headers autorisés
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
serializer = URLSafeTimedSerializer(SECRET_KEY)


# =================== Modèles =====================
class RegisterRequest(BaseModel):
    firstname: str
    lastname: str
    email: str
    password: str
    role: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ChatRequest(BaseModel):
    user_input: str


# =============== Fonctions utilitaires ===============

def get_accept_language(accept_language: str = Header(default="fr")):
    return accept_language.split(",")[0]  # Prend la première langue si plusieurs

def t(key: str, lang: str = "fr") -> str:
    return translations.get(key, {}).get(lang, translations.get(key, {}).get("fr", key))

def get_db():
    return sqlite3.connect(DB_PATH)

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        if email is None or role is None:
            raise HTTPException(status_code=401, detail="Token invalide.")
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token invalide.")

def validate_password(password: str,language: str = Depends(get_accept_language)):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail=t("password_too_short", language))
    if not any(c.isupper() for c in password):
        raise HTTPException(status_code=400, detail=t("password_missing_uppercase",language))
    if not any(c.islower() for c in password):
        raise HTTPException(status_code=400, detail=t("password_missing_lowercase",language))
    if not any(c in "!@#$%^&+-&*(),.?\":{}|<>" for c in password):
        raise HTTPException(status_code=400, detail=t("password_missing_special",language))

def send_verification_email(email: str, token: str):
    import uuid
    sender_email = "belgacemkhawla32@gmail.com"
    receiver_email = email
    password = "pqcv fuom idxh oaog"
    
    # IMPORTANT : Utiliser un lien valide
    verification_link = f"http://localhost:3000/verify-email/{token}"
    message = MIMEMultipart("alternative")
    message["Subject"] = "Vérification de votre adresse email"
    message["From"] = f"Support Plateforme <{sender_email}>"
    message["To"] = receiver_email
    message["Reply-To"] = sender_email
    message["Message-ID"] = f"<{uuid.uuid4()}@gmail.com>"

    # Texte brut
    text = f"""Bonjour,

Merci pour votre inscription sur notre plateforme.

Veuillez cliquer sur ce lien pour vérifier votre adresse email :
{verification_link}

Ce lien est valable 1 heure.

Cordialement,
L'équipe Support
"""

    # HTML
    html = f"""\
<html>
  <body>
    <p>Bonjour,<br><br>
       Merci pour votre inscription sur notre plateforme.<br><br>
       <a href="{verification_link}" style="padding:10px 20px;background-color:#0d5b53;color:white;text-decoration:none;border-radius:5px;">Cliquez ici pour vérifier votre adresse email</a><br><br>
       Ce lien est valable pendant 1 heure.<br><br>
       Cordialement,<br>
       <i>L'équipe Support</i>
    </p>
  </body>
</html>
"""

    part1 = MIMEText(text, "plain", "utf-8")
    part2 = MIMEText(html, "html", "utf-8")
    message.attach(part1)
    message.attach(part2)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {e}")
        raise HTTPException(status_code=500, detail="Échec de l'envoi de l'email.")

def stream_responses(chain,queries):
    for query in queries:
        for chunk in chain.stream(query):
            yield chunk
def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def embed_text(text):
    return app.state.embedding_model.embed_query(text)

def search_support(contenu: str, resume_draft: str, alpha: float = 0.7, beta: float = 0.3, top_k: int = 2):
    emb_contenu = embed_text(contenu)
    emb_resume = embed_text(resume_draft)

    results = []
    for p in app.state.support_summaries:
        vec_source = p.payload.get("embedding_source_like")
        vec_resume = p.payload.get("embedding_resume")
        if vec_source is None or vec_resume is None:
            continue
        score = (
            alpha * cosine_similarity(emb_contenu, vec_source)
            + beta * cosine_similarity(emb_resume, vec_resume)
        )
        results.append((p.payload.get("resume"), score))

    return sorted(results, key=lambda x: x[1], reverse=True)[:top_k]

@app.on_event("startup")
async def start():
    client, embedding_model, vectorstore = init_qdrant()
    
            # Récupérer tous les points (résumés) de la collection
    points, _ = client.scroll(
        collection_name=QDRANT_COLLECTION_SUPPORT_4,
        limit=20,
        with_vectors=True,
        with_payload=True
    )


    llm1 = load_llm1()
    llm2 = load_llm2()

    template = """
    Tu es un assistant intelligent multilingue (français et arabe), spécialisé dans la *génération de questions uniquement* (pas de réponses) de type 5W1H à partir d’un texte.

    🎯 *Objectif :*
    Analyser attentivement le texte fourni (le "contexte") et générer des *questions 5W1H* pertinentes, sans jamais proposer de réponses. La sortie doit être *strictement* un objet JSON, *sans aucun ajout ou explication*.

    📘 *Définition des questions 5W1H* :
    - *Qui (Who)* : Générer une question visant à identifier la personne ou l’entité principale ayant annoncé, initié ou soutenu  le fait principal.
    - *Quoi (What)* :  Générer une question visant à identifier l'evénement ou action principale décrite dans le texte.
    - *Quand (When)* :  Générer une question visant à identifier le moment ou date de l’événement.
    - *Où (Where)* :  Générer une question visant à identifier le lieu où s’est déroulé l’événement.
    - *Pourquoi (Why)* :  Générer une question visant à identifier la raison ou cause derrière l’événement.
    - *Comment (How)* :  Générer une question visant à identifier la façon ou méthode par laquelle l’événement s’est produit.

    🌍 *Instructions multilingues :*
    - Si le contexte est *uniquement en français, génère **une seule version en français* pour chaque question.
    - Si le contexte est *uniquement en arabe, génère **une seule version en arabe* pour chaque question.
    - Si le contexte est *mixte (français + arabe)* :
    - Génère *deux versions* de chaque question :
        - La version *en français* ne doit utiliser que le contenu *en français*.
        - La version *en arabe* ne doit utiliser que le contenu *en arabe*.
    - *Ne traduis jamais* entre les langues et *ne fusionne pas* d'informations entre textes arabes et français.

    🚫 *Contraintes supplémentaires :*
    - *Ne réponds jamais aux questions*, seulement les poser.
    - *Ne produis que du JSON*, sans aucune conclusion, explication ou message supplémentaire.

    📝 *Contexte* :
    --------------------
    {context}
    --------------------

    ✅ *Format de sortie (JSON uniquement) :*
    ```json
    {{
    "questions": {{
        "who": {{
        "fr": "Ta question en français ici (si applicable)",
        "ar": "سؤالك بالعربية هنا (إن وجد)"
        }},
        "what": {{
        "fr": "...",
        "ar": "..."
        }},
        "when": {{
        "fr": "...",
        "ar": "..."
        }},
        "where": {{
        "fr": "...",
        "ar": "..."
        }},
        "why": {{
        "fr": "...",
        "ar": "..."
        }},
        "how": {{
        "fr": "...",
        "ar": "..."
        }}
    }}
    }}
    """
    prompt_5w1h = ChatPromptTemplate.from_template(template)


    prompt_answer = ChatPromptTemplate.from_template("""
    Tu es un expert en compréhension multilingue. En t’appuyant uniquement sur les éléments suivants, rédige une réponse précise, adaptée à la nature de la question, et entièrement en français :

    Question (en français) :
    {question_fr}

    Contexte (en français) :
    {fr_chunks}

    Question (en arabe) :
    {question_ar}

    Contexte (en arabe) :
    {ar_chunks}

    Ta réponse doit :
    - Être concise si la question appelle une réponse directe ou factuelle (par exemple : une date, un nom, un lieu).
    - Être détaillée si plusieurs informations ou éléments de contexte sont nécessaires pour répondre correctement.
    - S’appuyer sur toutes les informations pertinentes fournies, qu’elles soient en français ou en arabe.
    - Reprendre **autant que possible les formulations originales des extraits en français**, sans les reformuler inutilement.
    - Ne surtout pas réutiliser ou traduire des formulations en arabe.
    - Être rédigée uniquement en français, sans aucun mot ou élément en arabe.
    - Ne pas reformuler les questions ni rappeler les extraits ou les résumer.
    - Ne pas inclure de traductions, de précisions inutiles ni d’introduction.

    Commence directement par la réponse, claire et structurée, en t’appuyant prioritairement sur les formulations des extraits fournis en français.
    """)


    template_traduction_titre =  """
        Vous êtes un traducteur professionnel. Votre tâche est de traduire le texte ci-dessous du français vers l'arabe. Voici les règles que vous devez suivre pour cette traduction :
        
    
        1. *Ne modifiez pas l'ordre du texte* : Assurez-vous que l'ordre des phrases et des idées reste fidèle à l'original.
        2. *Effectuez uniquement la traduction linguistique* : Votre seul travail est de traduire le texte du français vers l'arabe, sans changer aucun autre aspect du contenu.
        3. *Veillez à la fluidité et la précision* de la traduction en arabe, en respectant les règles grammaticales et stylistiques de la langue cible.

        Voici le texte à traduire : 
        {titre_francais}
        """

    template_traduction_resume =  """
        Vous êtes un traducteur professionnel. Votre tâche est de traduire le texte ci-dessous du français vers l'arabe. Voici les règles que vous devez suivre pour cette traduction :
        
        1. *Ne modifiez pas l'ordre du texte* : Assurez-vous que l'ordre des phrases et des idées reste fidèle à l'original.
        2. *Effectuez uniquement la traduction linguistique* : Votre seul travail est de traduire le texte du français vers l'arabe, sans changer aucun autre aspect du contenu.
        3. *Veillez à la fluidité et la précision* de la traduction en arabe, en respectant les règles grammaticales et stylistiques de la langue cible.

        Voici le texte à traduire : 
        {resume_francais}
        """
        
    template_titre = """  
                        Ta tâche est de générer un titre en respectant strictement les règles suivantes :  

                        ### Contraintes sur le titre :

                        Le titre doit obligatoirement être reformulé selon un des trois modèles suivants, choisis selon l’élément le plus mis en valeur dans le contexte :

                        1. Qui puis Quoi  
                        - À utiliser si le sujet principal est une personne, institution ou groupe.  
                        - Le titre commence par le nom exact suivi de l’action ou l’événement.  
                        - Exemple : Tebboune : "L'Algérie est autosuffisante en électricité et dispose d'un excédent de 12 000 mégawatts".

                        2. Où puis Quoi  
                        - À utiliser si le lieu est central dans le contexte.  
                        - Le titre commence par le lieu (ex. nom de ville, région), suivi de l’événement.  
                        - Exemple : Oran : Mobilis ouvre un centre de services.

                        3. Quand puis Quoi ⚠ (Rare, à utiliser uniquement si le temps est l’élément principal)  
                        - À utiliser si la date ou la période est fortement mise en avant, plus que les personnes ou lieux.  
                        - Le titre commence par cette date/période suivie de l’événement.  
                        - Exemple : En janvier 2025 : Belgacem khawla a publier un article scientifique sur AI  
                        - ❗Attention : Ce modèle est rarement utilisé. Ne le choisir **que si la date est manifestement l’information la plus importante.

                        ⚠ Ne jamais mentionner un nom, une personne ou une institution qui n’est pas explicitement mentionnée dans le contexte.  
                        ⚠ Le nom cité dans le titre doit non seulement apparaître dans le texte, mais il doit aussi être **clairement l'auteur ou responsable de l'action.  
                        ❌ Interdiction stricte de commencer un titre par "Tebboune :", sauf si le texte dit explicitement que Tebboune lui-même a fait cette déclaration ou pris cette action.  
                        ✅ Si c'est un ministère ou une institution qui agit ou parle, le titre doit commencer par ce ministère, cette institution ou ce lieu.
                        ⚠ Si le titre généré ne commence PAS par un nom propre, un lieu ou une date, alors il est invalide. Recommence avec l’un des trois modèles : Qui puis Quoi, Où puis Quoi, Quand puis Quoi. 
                        ⚠ Ne pas copier ni reformuler partiellement le titre d’origine.   
                        ⚠ Il est interdit de simplement insérer un nom ou un lieu devant le titre d’origine.  
                        ✅ Le contenu du titre doit être reconstruit à partir des faits essentiels du texte.
                        ⚠ Ne jamais formuler un titre de cette manière : "Akhbar El Youm : [événement]". Le titre doit débuter par un nom propre, un **lieu, ou une **date/période.  
                        ❌ Ne jamais utiliser un mot vague ou générique comme "Hydrocarbures" ou "Énergie" comme nom propre.  
                        ✅ Utiliser le nom exact de l’institution mentionnée dans le texte (ex. "Ministère de l’Énergie et des Mines", "SONATRACH", etc.)
                        ❌ Interdiction d’utiliser des formulations floues comme “en mai prochain”, “dans les jours à venir”, “bientôt”, etc.  
                        ✅ Utiliser une date précise, ou bien une **formulation neutre comme : “en mai 2025” si la date est connue, sinon reformuler sans la mention temporelle.

                        ### ✅ Étape de validation obligatoire du TITRE :

                        1. Le titre doit impérativement commencer par :
                        - soit un nom propre (personne ou institution),
                        - soit un lieu,
                        - soit une date ou période.
                        2. Si aucun des trois n’est en première position, le titre est invalide : recommencer la génération.
                        3. Identifier d'abord dans le contexte :
                        - Si une personne ou institution est responsable de l’action → utiliser Qui puis Quoi.
                        - Sinon, si un lieu est central → utiliser Où puis Quoi.
                        - Sinon, si une date domine → utiliser Quand puis Quoi.
                        4. ⚠ Si "Nadia mohammadi" est cité comme responsable de l’annonce, le titre doit commencer par son nom : "Nadia mohammadi : ..."
                        5. ⚠ Tu dois uniquement répondre par le titre final, sans explication, sans justification. Pas d'introduction du type "Voici le titre :". Seulement la phrase du titre. Pas plus.

                        Maintenant, applique ces règles au contexte suivant :  

                        Contexte :  
                        {context}  

                        Titre (strictement en {language}) :  
                """
    prompt_titre = ChatPromptTemplate.from_template(template_titre)

    prompt_traduction_titre = ChatPromptTemplate.from_template(template_traduction_titre)
    prompt_traduction_resume = ChatPromptTemplate.from_template(template_traduction_resume)

    # 📌 Chaînes de traitement

    chain = prompt_5w1h | llm1 | StrOutputParser()
    contxtualisation_chain = prompt_contxtualisation | llm1 | StrOutputParser()
    answer_chain = prompt_answer | llm1 | StrOutputParser()
    chain_resumer = ({"context": itemgetter("context"), "language": itemgetter("language")} | prompt_resumer | llm1 | StrOutputParser())
    chain_traduction_titre  = ({"titre_francais": itemgetter("titre_francais")} | prompt_traduction_titre | llm2 | StrOutputParser())
    chain_traduction_resume  = ({"resume_francais": itemgetter("resume_francais")} | prompt_traduction_resume | llm2 | StrOutputParser())
    chain_chat = ({"context": itemgetter("context"),"chat_history": itemgetter("chat_history"), "question": itemgetter("question")} | prompt_chat | llm2 | StrOutputParser())
    chain_titre = ({"context": itemgetter("context"), "language": itemgetter("language")} | prompt_titre | llm2 | StrOutputParser())
    chain_resumer_support = (
            {
                "summary": itemgetter("summary"),
                "support_summary_1": itemgetter("support_summary_1"),
                "support_summary_2": itemgetter("support_summary_2")
            } | prompt_support | llm1 | StrOutputParser()
        )
            
    splitter = CharacterTextSplitter(chunk_size=750, chunk_overlap=100)

    app.state.support_summaries=points
    app.state.vectorstore = vectorstore
    app.state.vectorstore_qst = vectorstore
    app.state.embedding_model = embedding_model 
    app.state.client = client 
    app.state.extract_text_func = extract_text 
    app.state.extract_text = "" 
    app.state.chain_resumer = chain_resumer 
    app.state.chain_traduction_titre = chain_traduction_titre
    app.state.chain_traduction_resume = chain_traduction_resume
    app.state.chain = chain 
    app.state.contxtualisation_chain = contxtualisation_chain 
    app.state.answer_chain = answer_chain 
    app.state.chain_titre = chain_titre 
    app.state.splitter = splitter 
    app.state.chain_resumer_support = chain_resumer_support 
    app.state.summary_text = {"fr": "", "ar": ""}
    app.state.chain_chat=chain_chat
    app.state.user_histories = {}  # <- Ajout ici
    app.state.upload_files={}
    app.state.resume_fr=""
    app.state.titre_fr=""
    app.state.bm25_docs=[]
    app.state.questions_json={}
    app.state.context={}
    app.state.bm25_retriever={}
    app.state.retriever_bm25_qst={}
@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.post("/upload_and_store_file")
async def upload_and_store_file(
    file: List[UploadFile] = File(...),
    user_id: Optional[str] = Form(None)
):
    app.state.upload_files=file
    if user_id is None:
        user_id = uuid.uuid4().hex

    if not hasattr(app.state, "uploaded_files_metadata"):
        app.state.uploaded_files_metadata = []

    results = []

    for f in file:
        try:
            suffix = os.path.splitext(f.filename)[1]
            file_type = suffix.lstrip(".")
            file_name = f.filename

            file_bytes = await f.read()
            all_contexts = []

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(file_bytes)
                temp_file_path = temp_file.name

            text = app.state.extract_text_func(temp_file_path)
            app.state.extract_text=text
            lang = detect(text)
            lang_label = "français" if lang == "fr" else "arabe" if lang == "ar" else "inconnue"

            all_contexts.append(f"[Nom du fichier : {file_name} | Langue du fichier : {lang_label}]\n{text}")

            chunks = app.state.splitter.split_text(text)
            contextualized_versions = []
            metadatas = []
            for idx, chunk in enumerate(chunks):
                contextualized_chunk =  app.state.contxtualisation_chain.invoke({
                    "context": text,
                    "chunk": chunk
                })
                fusion_text = contextualized_chunk + ": " + chunk

                metadata = {
                    "lang": lang_label,
                    "chunk_id": idx,
                    "raw_chunk": chunk,
                    "contextualized_chunk": contextualized_chunk,
                    "file_name": file_name,
                    "file_type": file_type
                }

                contextualized_versions.append(fusion_text)
                metadatas.append(metadata)
                app.state.bm25_docs.append(Document(page_content=fusion_text, metadata=metadata))

            app.state.vectorstore.add_texts(contextualized_versions, metadatas=metadatas)

            if not text:
                results.append({"file_name": file_name, "error": "❌ Aucun texte extrait."})
                continue

            results.append({"file_name": file_name, "message": "✅ Fichier traité avec succès."})

        except ValueError as e:
            results.append({"file_name": f.filename, "error": f"⚠ Erreur d'extraction : {str(e)}"})

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Erreur serveur : {error_details}")
            results.append({
                "file_name": f.filename,
                "error": f"❌ Erreur serveur : {str(e)}",
                "details": error_details
            })

        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    # Index BM25
    if app.state.bm25_docs:
        app.state.bm25_retriever = BM25Retriever.from_documents(app.state.bm25_docs)
        app.state.bm25_retriever.k = 2
    full_context = "\n\n".join(all_contexts)
    try:
        result = app.state.chain.invoke({"context": full_context})
        match = re.search(r"\{.*\}", result, re.DOTALL)

        if not match:
            raise ValueError("❌ Impossible d’extraire un bloc JSON valide.")
        
        json_str = match.group(0)
        parsed = json.loads(json_str)

        if "questions" not in parsed:
            raise ValueError("❌ Clé 'questions' absente dans le JSON.")


        app.state.questions_json = parsed

    except Exception as e:
        raise ValueError(f"❌ Erreur pendant la génération des questions : {e}")


    parsed = app.state.questions_json
    retriever_bm25 = app.state.bm25_retriever
    context=[]
    for w in ["who", "what", "when", "where", "why", "how"]:
        pair = parsed["questions"].get(w, {})
        question_fr = pair.get("fr", "").strip()
        question_ar = pair.get("ar", "").strip()

        fr_chunks, ar_chunks = [], []
        
        for lang_key, question in pair.items():
            if question.strip():
                vectordocs = app.state.vectorstore.similarity_search(question, k=2)
                bm25docs = retriever_bm25.get_relevant_documents(question) if retriever_bm25 else []

                seen = set()
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
                response = app.state.answer_chain.invoke({
                    "question_fr": question_fr,
                    "fr_chunks": "\n".join(fr_chunks),
                    "question_ar": question_ar,
                    "ar_chunks": "\n".join(ar_chunks),
                })
                context.append(f"{w}: {response}")
            except Exception as e:
                raise ValueError(f"❌ Erreur lors de l'appel LLM pour {w}: {e}")
            
    app.state.context=context   
                    
    # ✅ Un seul return ici, après traitement de tous les fichiers
    return JSONResponse(content={
        "user_id": user_id,
        "results": app.state.context
    })

@app.post("/chat")
async def chat_stream(data: ChatRequest):
    user_id = "123"
    user_input = data.user_input

    # Initialiser historique utilisateur s'il n'existe pas
    if user_id not in app.state.user_histories:
        app.state.user_histories[user_id] = []

    # Ajouter la question dans l'historique
    app.state.user_histories[user_id].append({"role": "user", "content": user_input})

    # Recréer l'historique du chat pour le prompt
    chat_history_text = "\n".join([
        f"{msg['role'].capitalize()}: {msg['content']}"
        for msg in app.state.user_histories[user_id]
        if msg["role"] != "system"
    ])    # Vérification sécurisée de l'existence du BM25 retriever

    retriever_bm25_qst = app.state.retriever_bm25_qst

    vectordocs = app.state.vectorstore.similarity_search(user_input, k=2)
    bm25docs = retriever_bm25_qst.get_relevant_documents(user_input) if retriever_bm25_qst else []

    seen = set()
    context_chunks = []

    for doc in vectordocs + bm25docs:
        key = (doc.metadata.get("source"), doc.metadata.get("chunk_id"))
        if key not in seen:
            seen.add(key)
            context_chunks.append(doc.metadata.get("raw_chunk", doc.page_content))

    raw_chunk = "\n\n".join(context_chunks)


    # Fonction de génération en streaming
    def generate_stream():
        full_response = ""
        for chunk in app.state.chain_chat.stream({
            "context": raw_chunk,
            "chat_history": chat_history_text,
            "question": f"User: {user_input}\nAssistant:"
        }):
            if chunk:
                full_response += chunk
                yield chunk
        # Enregistrement de la réponse complète dans l'historique
        app.state.user_histories[user_id].append({"role": "assistant", "content": full_response})

    return StreamingResponse(generate_stream(), media_type="text/event-stream")


@app.get("/reset")
async def reset_app_state():
    # Suppression de tous les points dans Qdrant
    app.state.client.delete(
        collection_name=QDRANT_COLLECTION,
        points_selector=FilterSelector(filter=Filter(must=[]))
    )

    # Réinitialisation des états internes
    app.state.user_histories = {}
    app.state.summary_text = {"fr": "", "ar": ""}
    app.state.upload_files={}
    app.state.resume_fr=""
    app.state.titre_fr=""
    app.state.context={}
    app.state.bm25_docs=[]
    app.state.questions_json={}
    app.state.bm25_retriever={}
    app.state.bm25_retriever_qst={}
    
    return {"status": "reset complete"}


@app.get("/generate_summary_fr")
async def generate_summary_stream():

    resume = app.state.chain_resumer.invoke({"context": app.state.context, "language": "francais"})

    resultats = search_support(app.state.extract_text, resume)

    if resultats:
        support1 = resultats[0][0]
        support2 = resultats[1][0] if len(resultats) > 1 else ""
        def full_stream():
            complete_resume = ""
            for chunk in app.state.chain_resumer_support.stream({
            "summary": resume,
            "support_summary_1": support1,
            "support_summary_2": support2
             }):
                complete_resume += chunk
                yield chunk
            app.state.resume_fr=complete_resume
        return StreamingResponse(full_stream(), media_type="text/event-stream")


@app.get("/generate_titre_fr")
async def generate_titre_stream():

    def full_stream():
        titre = ""
        for chunk in app.state.chain_titre.stream({"context": app.state.context, "language": "francais"}):
            titre += chunk
            yield chunk
        app.state.titre_fr = titre

    return StreamingResponse(full_stream(), media_type="text/event-stream")



@app.get("/generate_summary_ar")
async def generate_titre_stream():

    while not app.state.resume_fr:
        await asyncio.sleep(0.5)  # vérifie toutes les 500 ms

    def full_stream():
        for chunk in app.state.chain_traduction_resume.stream({"resume_francais": app.state.resume_fr}):
            yield chunk 
    return StreamingResponse(full_stream(), media_type="text/event-stream")


@app.get("/generate_titre_ar")
async def generate_titre_stream():

    while not app.state.titre_fr:
        await asyncio.sleep(0.5)  # vérifie toutes les 500 ms

    def full_stream():
        for chunk in app.state.chain_traduction_titre.stream({"titre_francais": app.state.titre_fr}):
            yield chunk 
    return StreamingResponse(full_stream(), media_type="text/event-stream")



@app.post("/register")
def register(request: RegisterRequest, language: str = Depends(get_accept_language)):
    print("📥 Langue reçue dans l'en-tête:", language)  # 🔍 Debug ici
    validate_password(request.password, language)

    if request.role not in ("admin", "user"):
        raise HTTPException(status_code=400, detail=t("invalid_role", language))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (request.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail=t("email_already_used", language))

    hashed_pwd = get_password_hash(request.password)
    cursor.execute('''
        INSERT INTO users (firstname, lastname, email, password, role, bloc, is_verified)
        VALUES (?, ?, ?, ?, ?, 0, 0)
    ''', (request.firstname, request.lastname, request.email, hashed_pwd, request.role))
    conn.commit()

    # Générer le token de vérification
    token = serializer.dumps(request.email, salt="email-confirm")

    # Envoyer l'email de vérification
    send_verification_email(request.email, token)

    conn.close()
    return {"message": t("user_created_check_email", language), "token": token}

# ==================== Route de vérification ====================

@app.get("/verify-email/{token}")
def verify_email(token: str, language: str = Depends(get_accept_language)):
    try:
        email = serializer.loads(token, salt="email-confirm", max_age=3600)  # 1 heure
    except Exception:
        raise HTTPException(status_code=400, detail=t("invalid_or_expired_token", language))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_verified = 1 WHERE email = ?", (email,))
    conn.commit()
    conn.close()

    return {"message": t("email_verified", language)}
"""
"""
@app.post("/login")
def login(request: LoginRequest, language: str = Depends(get_accept_language)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, firstname, lastname, email, password, role, bloc, is_verified FROM users WHERE email = ?
    ''', (request.email,))
    user = cursor.fetchone()

    # Vérification si l'utilisateur existe et si le mot de passe est correct
    if not user or not verify_password(request.password, user[4]):
        conn.close()
        raise HTTPException(status_code=400, detail=t("invalid_email_or_password", language))

    # Vérification si le compte est bloqué
    if user[6]:  # bloc == True
        conn.close()
        raise HTTPException(status_code=403, detail=t("account_blocked", language))

    # Vérification si l'email est validé
    if not user[7]:  # is_verified == False
        conn.close()
        raise HTTPException(status_code=400, detail=t("email_not_verified", language))

    # Si l'utilisateur est valide, créer un token JWT
    access_token = create_access_token(
        data={"sub": user[3], "role": user[5]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    cursor.execute("UPDATE users SET tokenAuth = ?, tokenAuthExpires = ? WHERE id = ?", (access_token, expires, user[0]))
    conn.commit()
    conn.close()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user[0],
            "firstname": user[1],
            "lastname": user[2],
            "email": user[3],
            "role": user[5]
        }
    }