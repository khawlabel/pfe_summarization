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
from prompts_v0_4 import *
from qdrant_client.http.models import Filter, FilterSelector
from fastapi.middleware.cors import CORSMiddleware
from numpy import dot
import numpy as np
from fastapi import Header
from translation import translations



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

def retrieve_context_with_metadata_file(query, file_name=None,length=1):
    """Récupère le contexte pertinent pour la requête, éventuellement filtré par fichier"""
    retriever = app.state.vectorstore.as_retriever(search_kwargs={"k": length})
    retrieved_docs = retriever.invoke(query)

    if file_name:
        # Ne garder que les documents liés à ce fichier
        retrieved_docs = [doc for doc in retrieved_docs if doc.metadata.get("file_name") == file_name]

    formatted_context = "\n\n".join(
        [
            f"📂 Fichier: {doc.metadata.get('file_name', 'Inconnu')}\n"
            f"📄 Type: {doc.metadata.get('file_type', 'Inconnu')}\n"
            f"🔹 Contenu:\n{doc.page_content}"
            for doc in retrieved_docs
        ]
    )

    return formatted_context    

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
        collection_name=QDRANT_COLLECTION_SUPPORT_2,
        limit=20,
        with_vectors=True,
        with_payload=True
    )


    llm1 = load_llm1()
    llm2=load_llm2()
    llm3 = load_llm3()
    llm4=load_llm4()
    llm5 = load_llm5()
    llm6=load_llm6()
    llm7=load_llm7()
   

    # 📌 Chaînes de traitement

    chain_chat = ({"context": itemgetter("context"), "question": itemgetter("question")} | prompt_chat | llm1 | StrOutputParser())
    chain_resumer = ({"context": itemgetter("context"), "language": itemgetter("language")} | prompt_resumer | llm2 | StrOutputParser())
    chain_traduction_titre  = ({"titre_francais": itemgetter("titre_francais")} | prompt_traduction_titre | llm3 | StrOutputParser())
    chain_traduction_resume  = ({"resume_francais": itemgetter("resume_francais")} | prompt_traduction_resume | llm3 | StrOutputParser())
    chain_resumer_general=({"context": itemgetter("context"), "language": itemgetter("language")} | prompt_resumer_general | llm5 | StrOutputParser())
    chain_titre_general=({"context": itemgetter("context"), "language": itemgetter("language")} | prompt_titre_general | llm6 | StrOutputParser())
    chain_resumer_support = (
            {
                "summary": itemgetter("summary"),
                "support_summary_1": itemgetter("support_summary_1"),
                "support_summary_2": itemgetter("support_summary_2")
            } | prompt_support | llm7 | StrOutputParser()
        )
            

    app.state.support_summaries=points
    app.state.vectorstore = vectorstore
    app.state.embedding_model = embedding_model 
    app.state.client = client 
    app.state.extract_text_func = extract_text 
    app.state.extract_text = "" 
    app.state.chain_resumer = chain_resumer 
    app.state.chain_traduction_titre = chain_traduction_titre
    app.state.chain_traduction_resume = chain_traduction_resume
    app.state.chain_resumer_general = chain_resumer_general 
    app.state.chain_titre_general = chain_titre_general 
    app.state.chain_resumer_support = chain_resumer_support 
    app.state.retrieved_contexts = []
    app.state.resumes_per_file = []
    app.state.summary_text = {"fr": "", "ar": ""}
    app.state.titles_per_file = ""
    app.state.chain_chat=chain_chat
    app.state.user_histories = {}  # <- Ajout ici
    app.state.upload_files={}
    app.state.resume_fr=""
    app.state.titre_fr=""

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

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(file_bytes)
                temp_file_path = temp_file.name

            text = app.state.extract_text_func(temp_file_path)
            app.state.extract_text=text

            if not text:
                results.append({"file_name": file_name, "error": "❌ Aucun texte extrait."})
                continue

            app.state.vectorstore.add_texts(
                [text],
                metadatas=[{"file_name": file_name, "file_type": file_type}]
            )

            app.state.uploaded_files_metadata.append({
                "file_name": file_name,
                "file_type": file_type
            })

            app.state.retrieved_contexts.append({
             "contenu":text,
             "file_name":file_name,
             "file_type":file_type

            })

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

    # ✅ Un seul return ici, après traitement de tous les fichiers
    return JSONResponse(content={
        "user_id": user_id,
        "results": results
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
    ])

    context = app.state.retrieved_contexts

    # Fonction de génération en streaming
    def generate_stream():
        full_response = ""
        for chunk in app.state.chain_chat.stream({
            "context": context,
            "question": f"{chat_history_text}\nUser: {user_input}\nAssistant:"
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
    app.state.retrieved_contexts = []
    app.state.resumes_per_file = []
    app.state.titles_per_file = ""
    app.state.summary_text = {"fr": "", "ar": ""}
    app.state.upload_files={}
    app.state.resume_fr=""
    app.state.titre_fr=""
    
    return {"status": "reset complete"}


@app.get("/generate_summary_fr")
async def generate_summary_stream():
        
    uploaded_files=app.state.upload_files

    all_resumes = "\n\n".join(app.state.resumes_per_file)

    # Résumé (fusion ou direct)
    if len(uploaded_files) == 1:
        resume = app.state.resumes_per_file[0]
    else:
        resume = app.state.chain_resumer_general.invoke({
            "context": all_resumes,
            "language": "francais"
        })
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

    uploaded_files=app.state.upload_files
    if not uploaded_files:
        return JSONResponse(status_code=400, content={"error": "Aucun fichier reçu."})

    query = "Fais un résumé clair et structuré des informations disponibles."
    app.state.retrieved_contexts.clear()
    app.state.resumes_per_file.clear()


    resumes_temp = []
    # Extraction et résumé fichier par fichier
    for file in uploaded_files:
        context = retrieve_context_with_metadata_file(query, file_name=file.filename, length=len(uploaded_files))
        app.state.retrieved_contexts.append(context)

        resume_piece = ""
        resume_piece=app.state.chain_resumer.invoke({"context": context, "language": "francais"})
            
        resumes_temp.append(resume_piece)

    app.state.resumes_per_file = resumes_temp

    all_resumes = "\n\n".join(resumes_temp)

    def full_stream():
        complete_titre = ""
        for chunk in app.state.chain_titre_general.stream({"context": all_resumes, "language": "francais"}):
            complete_titre += chunk
            yield chunk
        app.state.titre_fr = complete_titre

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