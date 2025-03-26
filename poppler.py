from pdf2image import pdfinfo_from_path
import os

pdf_path="pfe_summarization/data/ECHOUROUKELYAOUMI131020241a.pdf"
if not os.path.exists(pdf_path):
    print("❌ Le fichier n'existe pas ! Vérifie le chemin.")
else:
    print("✅ Le fichier existe.")
try:
    info = pdfinfo_from_path(pdf_path, poppler_path="C:\Users\DELL\poppler-24.08.0\Library\bin")
    print("✅ PDF lisible, nombre de pages :", info["Pages"])
except Exception as e:
    print("❌ Erreur Poppler :", e)
