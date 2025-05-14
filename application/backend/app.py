import os
import sqlite3
from datetime import datetime, timedelta

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
# Charger les variables d'environnement
load_dotenv()

# ================= Configuration =================
SECRET_KEY ="mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DB_PATH ="users.db"

app = FastAPI()

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

# =============== Fonctions utilitaires ===============
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

def validate_password(password: str):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Mot de passe : min. 8 caractères.")
    if not any(c.isupper() for c in password):
        raise HTTPException(status_code=400, detail="Mot de passe : min. une majuscule.")
    if not any(c.islower() for c in password):
        raise HTTPException(status_code=400, detail="Mot de passe : min. une minuscule.")
    if not any(c in "!@#$%^&*(),.?\":{}|<>" for c in password):
        raise HTTPException(status_code=400, detail="Mot de passe : min. un caractère spécial.")


# ==================== Routes =======================
def send_verification_email(email: str, token: str):
    import uuid
    sender_email = "belgacemkhawla32@gmail.com"
    receiver_email = email
    password = "pqcv fuom idxh oaog"

    # IMPORTANT : Utiliser un lien valide
    verification_link = f"https://ton-domaine.com/verify-email/{token}"

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
       <a href="{verification_link}" style="padding:10px 20px;background-color:#1a73e8;color:white;text-decoration:none;border-radius:5px;">Cliquez ici pour vérifier votre adresse email</a><br><br>
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
            print("Email envoyé avec succès!")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {e}")
        raise HTTPException(status_code=500, detail="Échec de l'envoi de l'email.")

# ==================== Route d'enregistrement ====================

@app.on_event("startup")
async def start():
    client, embedding_model, vectorstore = await asyncio.to_thread(init_qdrant)
    app.state.vectorstore = vectorstore
    app.state.embedding_model = embedding_model 
    app.state.client = client 
    app.state.extract_text_func = extract_text 
    
@app.post("/upload_and_store_file")
async def upload_and_store_file(
    file: UploadFile = File(...),
    user_id: Optional[str] = Form(None)
):
    print(file.filename)
    suffix = os.path.splitext(file.filename)[1]
    file_type = suffix.lstrip(".")

    file_bytes = await file.read()  # ⚠️ important : await

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(file_bytes)
        temp_file_path = temp_file.name

    try:
        # Extraction avec la fonction stockée au démarrage
        text = app.state.extract_text_func(temp_file_path)

        if not text:
            return JSONResponse(content={"error": "❌ Aucun texte extrait."}, status_code=400)

        # Ajouter au vectorstore
        app.state.vectorstore.add_texts(
            [text],
            metadatas=[{"file_name": file.filename, "file_type": file_type}]
        )

        if user_id is None:
            user_id = uuid.uuid4().hex

        return JSONResponse(content={
            "message": f"✅ Fichier '{file.filename}' traité et stocké.",
            "user_id": user_id
        })

    except ValueError as e:
        return JSONResponse(content={"error": f"⚠ Erreur d'extraction : {str(e)}"}, status_code=400)

    except Exception as e:
        return JSONResponse(content={"error": f"❌ Erreur serveur : {str(e)}"}, status_code=500)

    finally:
        os.remove(temp_file_path)

@app.post("/register")
def register(request: RegisterRequest):
    validate_password(request.password)

    if request.role not in ("admin", "user"):
        raise HTTPException(status_code=400, detail="Rôle invalide. Doit être 'admin' ou 'user'.")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (request.email,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email déjà utilisé.")

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
    return {"message": "Utilisateur créé. Vérifiez votre boîte mail pour activer votre compte."}

# ==================== Route de vérification ====================

@app.get("/verify-email/{token}")
def verify_email(token: str):
    try:
        email = serializer.loads(token, salt="email-confirm", max_age=3600)  # 1 heure
    except Exception:
        raise HTTPException(status_code=400, detail="Lien invalide ou expiré.")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_verified = 1 WHERE email = ?", (email,))
    conn.commit()
    conn.close()

    return {"message": "Email vérifié avec succès."}

@app.post("/login")
def login(request: LoginRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, firstname, lastname, email, password, role, bloc, is_verified FROM users WHERE email = ?
    ''', (request.email,))
    user = cursor.fetchone()

    # Vérification si l'utilisateur existe et si le mot de passe est correct
    if not user or not verify_password(request.password, user[4]):
        conn.close()
        raise HTTPException(status_code=400, detail="Email ou mot de passe incorrect.")

    # Vérification si le compte est bloqué
    if user[6]:  # bloc == True
        conn.close()
        raise HTTPException(status_code=403, detail="Compte bloqué. Contactez un admin.")

    # Vérification si l'email est validé
    if not user[7]:  # is_verified == False
        conn.close()
        raise HTTPException(status_code=400, detail="Email non vérifié. Veuillez vérifier votre boîte mail.")

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