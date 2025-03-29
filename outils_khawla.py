import numpy as np
import cv2
import numpy as np
from pdf2image import convert_from_path
from groq import Groq
from constants import *
import pytesseract
from langdetect import detect_langs  
import re
from langchain_qdrant import Qdrant
from constants import *
import platform


pytesseract.pytesseract.tesseract_cmd = PATH_tesseract

client_groq = Groq(api_key=GROQ_API_KEY)

def preprocess_image(image):
    """Améliorer la lisibilité en appliquant un seuillage et un filtre de netteté."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convertir en niveaux de gris
    gray = cv2.GaussianBlur(gray, (3, 3), 0)  # Réduction du bruit
    gray = cv2.medianBlur(gray, 3)  # Filtrage médian
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # Seuillage Otsu
    return binary

def detect_language_from_pdf(pdf_path):
    """Extrait 25% du haut de la première page pour détecter la langue."""
  # ✅ Étape 1 : Convertir le PDF en images haute résolution
    if platform.system() == "Windows":
         poppler_path = PATH_poppler
    else:
         poppler_path = None  # Sur Streamlit Cloud, pas besoin de spécifier

    images=convert_from_path(pdf_path, poppler_path=poppler_path, dpi=400)


    # On prend uniquement la première page
    image = np.array(images[0])
    height, width, _ = image.shape
    
    # On garde uniquement 25% du haut de l'image
    cropped_image = image[:height // 4, :]
    
    # Conversion en format OpenCV
    open_cv_image = cv2.cvtColor(cropped_image, cv2.COLOR_RGB2BGR)
    
    # Prétraitement
    processed_img = preprocess_image(open_cv_image)
    
    # Sauvegarde temporaire
    temp_path = "temp_crop.jpg"
    cv2.imwrite(temp_path, processed_img)

    try:
        # OCR avec Tesseract
        text_tesseract = pytesseract.image_to_string(temp_path, lang="fra+ara").strip()
    finally:
        os.remove(temp_path)  # Supprimer l’image temporaire

    langs_detected = detect_langs(text_tesseract)
    for lang in langs_detected:
              if lang.lang == "fr" and lang.prob > 0.6:
                  return "fr"
              elif lang.lang == "ar" and lang.prob > 0.6:
                  return "ar"
          
          # Par défaut, si la probabilité est faible, on choisit "fr"
    return "fr"

def extract_text_from_pdf(pdf_path, lang):
    """Extrait le texte d'un PDF en effectuant une reconnaissance optique (OCR)."""
    extracted_text = []

    # ✅ Étape 1 : Convertir le PDF en images haute résolution
    if platform.system() == "Windows":
         poppler_path = PATH_poppler
    else:
         poppler_path = None  # Sur Streamlit Cloud, pas besoin de spécifier

    images=convert_from_path(pdf_path, poppler_path=poppler_path, dpi=400)

    for i, image in enumerate(images):
        # Convertir PIL en OpenCV
        open_cv_image = np.array(image)
        open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)

        # ✅ Appliquer le prétraitement pour améliorer l'OCR
        processed_img = preprocess_image(open_cv_image)

        # Sauvegarder l'image temporairement
        temp_path = f"temp_page_{i}.jpg"
        cv2.imwrite(temp_path, processed_img)

        try:
            if lang == "fr":
                text_tesseract = pytesseract.image_to_string(temp_path, lang="fra+ara")
            elif lang == "ar":
                text_tesseract = pytesseract.image_to_string(temp_path, lang="ara+fra")
            else:
                raise ValueError("Langue non supportée. Utilisez 'fr' pour le français ou 'ar' pour l'arabe.")

            extracted_text.append(text_tesseract.strip())

        finally:
            # Supprimer l'image temporaire après traitement
            if os.path.exists(temp_path):
                os.remove(temp_path)

    return "\n\n".join(extracted_text).strip()

def extract_text_from_audio_video(pdf_path):
  with open(pdf_path, "rb") as file:
      transcription = client_groq.audio.transcriptions.create(
        file=(pdf_path, file.read()),
        model=WHISPER,
        response_format="verbose_json",
      )
      return transcription.text

def clean_text_extracted_from_pdf(file_path, lang):
    """Extrait et corrige le texte en fonction de la langue."""
    text = extract_text_from_pdf(file_path, lang)
    if lang == "fr":
        completion = client_groq.chat.completions.create(
            model=LLM_correction,
             messages=[
                {
                  "role": "system",
                  "content": """Tu es un assistant spécialisé dans la correction et l'amélioration des textes extraits via OCR en français et en arabe.

                  - **Ne reformule pas le texte.** Garde toutes les phrases et paragraphes dans le même ordre.
                  - **Corrige uniquement** les fautes d'orthographe, de grammaire et de typographie.
                  - **Supprime** les éléments non pertinents, tels que :
                    - Les dates de publication (ex : "Publié le :", "Le :").
                    - Les liens et URL (ex : "https://", "www.", ".dz").
                    - Les noms de journaux et identifiants techniques(ex : "OUEST TRIBUNE","ALGERIE CONFLUENCES").
                    - Les en-têtes et Les mots isolés et signatures (ex : "Par Rédaction", "©24H Algérie","MEDIAMARKETING").
                    - Les numéros de page et balises inutiles (ex : "1/1").
                  - **Ne modifie pas le style d'écriture ni le ton du texte.**
                  - **La sortie doit être strictement fidèle au texte original, sans reformulation ni résumé.**
                  - **Présente directement le texte corrigé, sans introduction ni indication comme "Voici le texte corrigé".**"""
                },
                {
                    "role": "user",
                    "content": text

                }
            ],
            temperature=0.2,
            max_tokens=2048,
            top_p=0.95,
            stream=True
        )

    elif lang == "ar":
        completion = client_groq.chat.completions.create(
            model=LLM_correction,
              messages=[
                {
                "role": "system",
                "content": """أنت مساعد متخصص في تصحيح النصوص العربية المستخرجة من التعرف الضوئي على الحروف (OCR).
                - **لا تعيد صياغة النص.** احتفظ بجميع الجمل بنفس ترتيبها وصيغتها الأصلية.
                - **قم فقط بتصحيح الأخطاء الإملائية والنحوية والتنسيقية.**
                - **احذف العناصر غير الضرورية** مثل:
                  - التواريخ، الروابط، أسماء الصحف.
                  - أرقام الصفحات، الرموز غير المفهومة، والأجزاء غير المقروءة.
                - **قدم النص مباشرة دون أي مقدمة أو عبارات مثل "إليك النص المصحح".**
                - **لا تستخدم أي علامات خاصة مثل " ** " أو تقسيم النص بفواصل ظاهرة.**
                - **يجب أن يكون النص النهائي واضحاً، منسقاً، وخالياً من الأخطاء، مع الحفاظ على دقة وأمانة المعلومات.**"""
              },
                      {
                    "role": "user",
                    "content": text

                }
            ],
            temperature=0.2,
            max_tokens=2048,
            top_p=0.95,
            stream=True
        )

    else:
        raise ValueError("Langue non supportée. Utilisez 'fr' pour le français ou 'ar' pour l'arabe.")

    # ✅ Lire la réponse progressivement sans erreur
    response_text = ""
    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta.content:
            response_text += chunk.choices[0].delta.content

    # ✅ Supprimer les parties <think>...</think> pour l'arabe
    #if lang == "ar":
    response_text = re.sub(r"<think>.*?</think>", "", response_text, flags=re.DOTALL)

    return response_text  # ✅ Retourne le texte corrigé

def extract_text(file_path):
    """Détecte le type de fichier et applique la bonne extraction."""
    file_path_ = str(file_path).lower()

    if file_path_.endswith(".pdf"):
        detected_lang = detect_language_from_pdf(file_path)
        return extract_text_from_pdf(file_path,detected_lang)

    elif file_path_.endswith((".mp3", ".wav", ".ogg", ".flac", ".m4a",".mp4", ".avi", ".mov", ".mkv")):
        return extract_text_from_audio_video(file_path)

    else:
        raise ValueError("Format non supporté")
