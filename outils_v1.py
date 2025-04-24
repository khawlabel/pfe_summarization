import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import fitz  # PyMuPDF


def nettoyer_texte_brut(texte):
    # Supprimer les dates françaises en début de texte (ex : 22 avril 2023)
    texte = re.sub(r'^(?:\s*|\n)*(\d{1,2}\s(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s\d{4})(?:\s*|\n)+', '', texte, flags=re.IGNORECASE)

    # Supprimer les dates françaises à la fin du texte
    texte = re.sub(r'(\n|\s)+(\d{1,2}\s(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s\d{4})(\s*|\n)*$', '', texte, flags=re.IGNORECASE)



    # 1. Supprimer noms de journaux, dates, mentions légales, etc.
    texte = re.sub(r"HORIZONS.*?\n", "", texte, flags=re.IGNORECASE)
    texte = re.sub(r"\b(Mercredi|Jeudi|Vendredi|Samedi|Dimanche|Lundi|Mardi)\s\d{1,2}\s\w+\s\d{4}", "", texte)
    texte = re.sub(r"REDACTION.*?\n", "", texte)
    texte = re.sub(r"[0-9]+\s*,?", "", texte)


    # Supprimer les numéros de page et entêtes/bas de page
    texte = re.sub(r'tenu de la page\s*\d+\s*---?', '', texte, flags=re.IGNORECASE)
    texte = re.sub(r'\bPage\s*\d+\b', '', texte, flags=re.IGNORECASE)

    # Supprimer les adresses et numéros de téléphone, fax
    texte = re.sub(r'\d{2}(?:[\s\.\-]?\d{2}){2,}', '', texte)
    texte = re.sub(r'(rue|avenue|cité|bt|logts|nouvelle ville|ville|bureau|fax|email|mail|n°)\s[^.\n]+', '', texte, flags=re.IGNORECASE)


    # Supprimer les liens, emails, numéros de téléphone
    texte = re.sub(r'https?://\S+|www\.\S+', '', texte)  # Liens web
    texte = re.sub(r'[\w\.-]+@[\w\.-]+', '', texte)  # Emails
    # Suppression des liens (URLs)
    texte = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', texte)

    texte = re.sub(r'\(?0\d{2,3}\)?[\s\-\.]?\d{2}[\s\-\.]?\d{2}[\s\-\.]?\d{2}', '', texte)  # Téléphones

    # Supprimer les mentions de contact ou publication
    texte = re.sub(r'\b(tél|fax|e-?mail|courriel|contact|impression|diffusion|redaction|administration|tirage|publication|abonnement)\b.*?:.*', '', texte, flags=re.IGNORECASE)


    # Supprimer certaines ponctuations ou symboles inutiles
    texte = re.sub(r'[•■●♦■□◆◇]', '', texte)
    texte = re.sub(r'[■\*\_\=\[\]\{\}\(\)]', '', texte)

    # Supprimer les signatures ou entêtes d'auteurs
    texte = re.sub(r'\bn\s+[A-Z][a-z]+\s+[A-Z]\.', '', texte)


    # Suppression des balises inutiles
    texte = re.sub(r'<[^>]+>', '', texte)

    # Supprimer les phrases liées à l’origine de l’article
    texte = re.sub(r'Entretien réalisé par.*', '', texte, flags=re.IGNORECASE)

    # Nettoyer les espaces multiples et lignes vides
    texte = re.sub(r'\n{2,}', '\n', texte)
    texte = re.sub(r'[ \t]{2,}', ' ', texte)
    # Nettoyage final
    texte = texte.strip()

    return texte


def decouper_en_articles(text):
    """
    Cette fonction découpe un texte en articles où chaque article contient directement
    le titre (principal et/ou sous-titre) et son contenu respectif dans un même chunk.
    """

    # Nettoyage : réduire les sauts de ligne multiples et les espaces inutiles
    text = re.sub(r'\n{2,}', '\n', text.strip())

    # Trouver tous les titres principaux (en majuscules) et les sous-titres (en minuscules)
    titres_principaux = re.findall(r'(^|\n)([A-ZÉÈÀÂÎÙÇ\s]{5,})(?=\n)', text)

    # Liste pour stocker les articles (chunks)
    articles = []

    # Ajouter le premier article avec le titre principal et son contenu
    start = 0
    for i, (start_pos, title) in enumerate(titres_principaux):
        # Si c'est un titre principal (en majuscules)
        title = title.strip()

        # Trouver la position du titre dans le texte
        end = text.find(title, start)

        # Le contenu commence après le titre trouvé
        content_start = end + len(title)

        # Trouver la position du prochain titre principal ou sous-titre, ou la fin du texte
        next_title_pos = len(text)
        if i + 1 < len(titres_principaux):
            next_title_pos = text.find(titres_principaux[i + 1][1], content_start)

        # Extraire le contenu de l'article (qui peut inclure des majuscules)
        content = text[content_start:next_title_pos].strip()

        # Si le contenu commence par une majuscule, il peut être considéré comme du contenu
        if re.match(r'^[A-Z]', content) and len(content) < 200:
            if articles:
                articles[-1] = articles[-1] + "\n" + content
            else:
                # Si aucun article n'existe encore, créer un article avec le titre et le contenu
                articles.append(f"{title}\n{content}")
        else:
            article = f"{title}\n{content}"
            articles.append(article)


        start = next_title_pos  # Mettre à jour la position de départ pour le prochain titre

    return articles


def est_gras(ligne):
    """Considère comme 'gras' les lignes entièrement en majuscules."""
    return ligne.isupper()


def nettoyer_article(article):
    # Supprimer les coupures de mots (ex: rela-\ntion → relation)
    article = re.sub(r'(\w+)-\n(\w+)', r'\1\2', article)

    lignes = article.splitlines()
    lignes_nettoyees = []
    buffer = ""

    i = 0
    while i < len(lignes):
        ligne = lignes[i].strip()

        if not ligne:
            if buffer:
                lignes_nettoyees.append(buffer.strip())
                buffer = ""
            i += 1
            continue

        # Cas 1 : Une seule lettre majuscule → fusion sans espace
        if len(ligne) == 1 and ligne.isupper():
          if i + 1 < len(lignes):
              ligne_suivante = lignes[i + 1].lstrip()
              if buffer:
                  buffer += " " + ligne + ligne_suivante
              else:
                  buffer = ligne + ligne_suivante
              i += 2
              continue

        # Cas 2 : Deux caractères, genre «C → fusion sans espace
        if len(ligne) == 2 and not ligne[0].isalpha() and ligne[1].isalpha():
          if i + 1 < len(lignes):
              ligne_suivante = lignes[i + 1].lstrip()
              if buffer:
                  buffer += " " + ligne + ligne_suivante
              else:
                  buffer = ligne + ligne_suivante
              i += 2
              continue

        if est_gras(ligne):
            if buffer:
                lignes_nettoyees.append(buffer.strip())
                buffer = ""
            lignes_nettoyees.append(ligne)
        else:
            # Toujours fusionner avec un espace
            if buffer:
                buffer += " " + ligne
            else:
                buffer = ligne

        i += 1

    if buffer:
        lignes_nettoyees.append(buffer.strip())

    return "\n\n".join(lignes_nettoyees)

def extraire_articles_pdf(pdf_file, nettoyer_texte_brut, decouper_en_articles, nettoyer_article):
    """
    Lit un fichier PDF et retourne une liste de tous les articles nettoyés.
    
    Args:
        pdf_file: fichier PDF chargé (de type file-like)
        nettoyer_texte_brut: fonction pour nettoyer le texte brut
        decouper_en_articles: fonction pour découper en articles
        nettoyer_article: fonction pour nettoyer chaque article

    Returns:
        List[str]: Liste des articles nettoyés.
    """
    import tempfile

    tous_les_articles_nettoyes = []

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(pdf_file.read())
        doc = fitz.open(tmp_file.name)

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            texte_brut = page.get_text()
            texte_nettoye = nettoyer_texte_brut(texte_brut)
            articles_page = decouper_en_articles(texte_nettoye)

            for article in articles_page:
                nettoye = nettoyer_article(article)
                tous_les_articles_nettoyes.append(nettoye)

    return tous_les_articles_nettoyes


###################################     sauvegarder dans qdrant     #####################################################


def separer_articles(text):
    # Si 'text' est une liste, on la transforme en une seule chaîne
    if isinstance(text, list):
        text = "\n\n".join(text)
    id_compteur = 1
    # Séparer le texte par des sauts de ligne
    blocs = text.split('\n\n')  # sépare les blocs d'articles par des doubles sauts de ligne
    articles = []
    for bloc in blocs:
        contenu = bloc.strip()
        # Ajouter des articles avec un identifiant unique
        articles.append({"id":id_compteur , "contenu": contenu})
        id_compteur += 1  # Incrémenter l'ID
    return articles
