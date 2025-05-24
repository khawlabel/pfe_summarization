FROM python:3.12

# Installer Tesseract (avec fra et ara) + Poppler + dépendances
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-fra \
    tesseract-ocr-ara \
    poppler-utils \
    gcc \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Définir le dossier de travail
WORKDIR /app

# Copier les dépendances Python
COPY requirements.txt .

# Installer les bibliothèques Python
RUN pip install -r requirements.txt

# Copier le reste de l'application
COPY . .

# Exposer le port (ex: FastAPI)
EXPOSE 8000

# Commande de démarrage (à adapter selon ton fichier)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
