from outils import *
from qdrant_client import QdrantClient
from langchain_groq import ChatGroq
from qdrant_client.models import VectorParams, Distance
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain.chains import RetrievalQA
from constants import *
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# Connexion à Qdrant avec les variables chargées
client = QdrantClient("https://48a76f37-3da8-46da-a372-9c8f7cf6ca6d.us-west-2-0.aws.cloud.qdrant.io"
, api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.JDB8zdeJoArApKIDN-v3XZdpzXEp6BbE41jBwAWqtt0")

# Modèles Groq
llm1 = ChatGroq(groq_api_key="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", model_name="llama3-8b-8192")
llm2 = ChatGroq(groq_api_key="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", model_name="deepseek-r1-distill-qwen-32b")


# Charger le modèle d'embeddings
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# Récupérer la dimension du modèle
vector_size = embedding_model.client.get_sentence_embedding_dimension()

if not client.collection_exists("my_collection"):
   client.create_collection(
      collection_name="my_collection",
      vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
   )

# Ajouter les documents à Qdrant
vectorstore = Qdrant(
    client=client,
    collection_name="my_collection",
    embeddings=embedding_model,
)

info = client.get_collection("my_collection")
print(f"📊 Nombre de vecteurs enregistrés : {info.points_count}")


def process_and_store_file(file_path,lang):
    """Extrait le texte d'un fichier et l'ajoute dans Qdrant."""
    extractedText = extract_text(file_path,lang)  # Ta fonction d'extraction
    print(extractedText)

    if extractedText:
        vectorstore.add_texts([extractedText])
        print(f"📥 Texte extrait et stocké depuis {file_path} ✅")
    else:
        print(f"⚠️ Aucun texte extrait depuis {file_path} ❌")


retriever = vectorstore.as_retriever()

#qa_chain_1 = RetrievalQA.from_chain_type(llm=llm1, retriever=retriever, return_source_documents=True)
qa_chain_2 = RetrievalQA.from_chain_type(llm=llm2, retriever=retriever, return_source_documents=True)


# Exemple d'ajout de fichier
#files=["/content/ECHOUROUKELYAOUMI131020241a.pdf","/content/ELDJAZAIRELDJADIDA131020241a.pdf","/content/RadioOuargla141020241a.mp3","/content/Eliktisadia131020241a.mp4"]

files=["CHAINE1010920241a.mp3"]
langue="ar"
"""for file in files:
    process_and_store_file(file,langue)
    print("file proccessed")
"""

template_resumer = """  
Ta tâche est de générer un **titre et un résumé** en respectant strictement les règles suivantes :  

### **Règles générales** :  
- **Ne jamais ajouter d'informations extérieures au contexte fourni.**  
- **Ne pas analyser ni interpréter les faits.** Fournis uniquement les informations essentielles.  
- **Le résumé doit être direct et informatif, sans liste à puces.**  
- **Respecte le style journalistique** : phrases structurées, neutres et précises.  
- **Ne pas ajouter d’introduction ou de conclusion.**  
- **Mentionner les chiffres et faits marquants sans reformulation inutile.**  

### **Règles spécifiques à respecter impérativement :**  

1. **Le titre doit être court, factuel et basé uniquement sur le contexte.**  
   - **Éviter toute redondance ou ajout de termes inutiles.**  

2. **Reprendre les termes du contexte exactement comme ils apparaissent.**  
   - **Interdiction stricte de modifier ou reformuler les noms officiels.**  
   - **Exemple interdit :** "La ministre des Télécommunications" si le texte mentionne "le ministère".  

3. **Ne pas introduire de causes ou justifications non mentionnées.**  
   - **Exemple interdit :** Dire que l’augmentation est due à un "programme de développement" si cela n'est pas explicitement écrit.  
   - **Exemple interdit :** Ajouter "directives du Président" si cela n’apparaît pas dans le texte source.  

4. **Ne jamais ajouter d’explications techniques non présentes.**  
   - **Exemple interdit :** "L'innovation a amélioré la vitesse de téléchargement" si cela n'est pas dit.  

5. **Respect strict des chiffres et des formulations du contexte.**  
   - **Ne pas changer "foyers connectés" en "accès internet"** si ce n'est pas la même unité.  
   - **Reprendre exactement les chiffres tels qu’ils apparaissent.**  

---

### **Contraintes sur le titre** :  
- **Longueur** : **Entre 4 et 32 mots** (≈ 12 mots en moyenne).  
- **Caractères** : **Entre 28 et 220 caractères** (≈ 74 caractères en moyenne).  
- **Structure** : **1 phrase unique**, claire et informative.  
- **Interdiction** : Pas de reformulation excessive ni d'ajout d'interprétation.  

### **Contraintes sur le résumé** :  
- **Longueur** : **Entre 9 et 146 mots** (≈ 55 mots en moyenne).  
- **Caractères** : **Entre 59 et 927 caractères** (≈ 353 caractères en moyenne).  
- **Nombre de phrases** : **1 à 3 phrases** en général (**max 13**).  
- **Concision** : Clair, précis, sans analyse ni commentaire subjectif.  
- **Obligation** : Conserver **tous les faits et chiffres essentiels**.  

### **Éléments à couvrir implicitement** :  
- **Ce qui s'est passé**  
- **Qui est impliqué**  
- **Quand, où et pourquoi cela a eu lieu**  
- **Comment cela s'est déroulé**  

---

**Maintenant, applique ces règles au contexte suivant :**  

Contexte :  
{context}  

Résumé (strictement en {language}) :  
"""  

template_chat = """
Tu es un assistant intelligent qui répond de manière naturelle et précise aux questions en utilisant exclusivement les informations fournies.

### Instructions :
1. Fournis une **réponse fluide et complète**, formulée comme un humain le ferait.
2. Commence la réponse en **introduisant l'information de manière naturelle** (exemple en arabe : "وفقاً لما كشفت عنه الوزارة، ..." ou en français : "D'après les données officielles, ...").
3. Respecte la langue spécifiée par l’utilisateur : {language}.
4. Ne mentionne **ni le contexte, ni la source, ni "selon le contexte"**.
5. Si aucune réponse claire ne peut être donnée, dis simplement : "Je ne dispose pas d'assez d'informations pour répondre."

### Langue requise : {language}

### Contexte :
{context}

### Question :
{question}

### Réponse ({language}) :
"""


prompt_resumer = ChatPromptTemplate.from_template(template_resumer)
prompt_chat = ChatPromptTemplate.from_template(template_chat)
chain_resumer = (
    {
        "context": itemgetter("context"),
        "language": itemgetter("language"),
    }
    | prompt_resumer
    | llm1
    | StrOutputParser()
)
chain_chat = (
    {
        "context": itemgetter("context"),
        "question": itemgetter("question"),
        "language": itemgetter("language"),
    }
    | prompt_chat
    | llm1
    | StrOutputParser()
)
# Demander le mode à l'utilisateur
mode = input("Voulez-vous un résumé (1) ou poser une question (2) ? ").strip()
if mode == "1":
    query = "Fais un résumé clair et structuré des informations disponibles dans les sources."

    retrieved_docs = retriever.invoke(query)

    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    result = chain_resumer.invoke({"context": context, "language":"francais"})

    print("\n📝 Résumé généré :")
    print(result)
elif mode == "2":
    query = "Combien de foyers en Algérie sont connectés à l’Internet fixe ?"
    
    retrieved_docs = retriever.invoke(query)
    context = "\n\n".join([doc.page_content for doc in retrieved_docs])

    result = chain_chat.invoke({"context": context,"question": query, "language": "arabe"})

    print("\n🤖 Réponse du LLM :")
    print(result)



"""print("\n📚 Documents utilisés :")
for doc in retrieved_docs:
    print(doc.page_content)
"""
"""
# resume de mediamarketing :

Le nombre de foyers connectés au réseau internet très haut débit en fibre optique jusqu'au domicile
 (FTTH) a dépassé le seuil de 1,5 million, a annoncé samedi 12 octobre 2024, le ministère de
   la Poste et des Télécommunications dans un communiqué. ""Cette évolution quantitative
     s'accompagne d'une amélioration qualitative de la vitesse de débit disponible pour les 
     abonnés"", relève le communiqué, soulignant qu'Algérie Télécom a lancé des offres 
     promotionnelles pour ceux souhaitant bénéficier de débits élevés allant jusqu'à 1 
     Gigabit/seconde sur demande"". Le nombre total de foyers connectés au réseau internet fixe, est passé de 3,5 millions au début de l'année 2020 à 5,8 millions en octobre 2024."
"""