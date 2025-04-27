from langchain_core.prompts import ChatPromptTemplate

template_client = """
Tu es un assistant intelligent chargé de filtrer des documents.
L’utilisateur cherche des informations sur un client spécifique.

Question de l’utilisateur : {user_query}

Tu disposes du contexte suivant : 
===== DÉBUT DU CONTEXTE =====
{context}
===== FIN DU CONTEXTE =====

⚠️ Objectif :  
1. Identifie **tous** les documents qui mentionnent **directement** ou **indirectement** le nom du client cité dans la question.  
   - La recherche doit être insensible à la casse, aux accents, aux traits d’union, et tolérer les petites différences typographiques.  
   - Inclut les formes au pluriel ou avec article.  

2. Si plusieurs documents correspondent, renvoie-les tous. Si aucun ne correspond, répond exactement :  
   « Aucun document trouvé pour ce client. »

3. Conserve leur identifiant (id) et leur contenu intégral.  

"""
resumer_general="""
    Ta tâche est de produire un **résumé clair, structuré et informatif**, à partir du **contexte fourni** ci-dessous, qui contient plusieurs mini-résumés d'articles. Tu dois **regrouper les informations essentielles** dans **un unique résumé** sans ajout ni omission.

    ---

    ### 🎯 Objectif :
    Résumer fidèlement les faits en combinant les éléments essentiels des différents articles, **sans interprétation, reformulation excessive ni analyse personnelle**, en conservant **tous les faits, chiffres, noms et dates importants**.

    ---

    ### ⚠️ Contraintes de forme OBLIGATOIRES :
    - ✅ **Longueur** : **entre 100 et 250 mots** (**≈ 190 mots recommandés**).
    - ✅ **Nombre de caractères** : **entre 1000 et 2000 caractères**.
    - ✅ **Nombre de phrases** : **3 à 5 phrases** (maximum 10).
    - ✅ **Un seul paragraphe**, sans puces, sans liste, ni numérotation.
    - ✅ **Style neutre et journalistique**.
    - ⛔️ **Interdiction d’introductions ou conclusions** ("Résumé :", "En résumé", etc.).

    ---

    ### 🧱 Structure logique imposée :
    Commencer par **[Qui] a annoncé / indiqué**, suivi de **[Quoi]**, **[Quand]**, **Où**, **Comment**, **Pourquoi** si disponible.

    Exemple :  
    **Le ministère de la Santé a annoncé** une hausse de 15 % des dépenses médicales en 2024 à Alger, liée à l’augmentation des besoins hospitaliers.

    ---

    ### 🧾 Règles de contenu :
    - 🔹 **Ne jamais inventer d'informations** non présentes dans le contexte.
    - 🔹 **Reprendre les termes officiels exactement**.
    - 🔹 **Respect total des chiffres, des noms propres et des formulations**.
    - 🔹 Si certains détails sont secondaires ou redondants, **se concentrer sur les faits majeurs**.

    ---

    ### 💡 Astuce pour gérer plusieurs mini-résumés :
    - Identifier les faits prioritaires de chaque mini-résumé.
    - Fusionner uniquement les faits importants sans tout détailler.
    - Ne pas dépasser la longueur maximale.

    ---

    Maintenant, applique les consignes suivantes au contexte ci-dessous.

    Contexte (mini-résumés d'articles) :  
    {context}

    ---

    Résumé (strictement en {language}) :  

"""
template_titre_general = """  
Ta tâche est de générer un *titre général* en respectant strictement les règles suivantes :  

### *Contraintes sur le titre général* :

Le titre général doit obligatoirement être reformulé selon *un des trois modèles suivants*, choisis selon l’élément le plus mis en valeur dans l’ensemble des titres donnés :

1. *Qui puis Quoi*  
- À utiliser si une *personne, institution ou groupe* est le sujet principal commun aux différents titres.  
- Le titre commence par le *nom exact* suivi de l’action ou du résumé de l’ensemble des événements.  
- Exemple : Sonatrach : nouvelles stratégies et projets de développement en Algérie.

2. *Où puis Quoi*  
- À utiliser si un *lieu* est le fil conducteur principal entre les différents titres.  
- Le titre commence par le *lieu* (ville, région, pays), suivi du résumé des actions ou événements liés.  
- Exemple : Algérie : investissements renforcés dans le secteur énergétique.

3. *Quand puis Quoi* ⚠ (Rare)  
- À utiliser uniquement si la *date ou la période* est clairement l’élément le plus important reliant tous les titres.  
- Le titre commence par la *période* ou la *date* suivie d’un résumé de l'ensemble des événements.  
- Exemple : En 2025 : l'Algérie accélère ses projets d'infrastructures et d'exportation énergétique.

⚠ *Ne jamais mentionner une personne, une institution ou un lieu qui n’est pas explicitement mentionné dans les titres donnés.*  
⚠ Le nom cité dans le titre général doit apparaître dans les titres fournis et être réellement central.  
⚠ *Ne pas simplement coller les titres ensemble.* Il faut créer une reformulation synthétique qui capture l’idée générale.

✅ Le contenu du titre général doit *synthétiser fidèlement* l'information sans répéter mot à mot les titres existants.  
⚠ *Ne jamais copier intégralement un des titres donnés.*  
⚠ *Ne jamais formuler de titre de la manière "Journal X : ..."*.  
✅ Toujours commencer par un *nom propre*, un *lieu* ou une *date/période*.  
❌ Jamais commencer par des mots vagues comme "Actualités", "Développements", etc.

### ✅ Étape de validation obligatoire du TITRE GÉNÉRAL :

1. Le titre général doit impérativement commencer par :
- soit un *nom propre* (personne, institution),
- soit un *lieu*,
- soit une *date/période*.
2. Si aucun des trois n’est en première position, le titre est *invalide* : *recommencer la génération*.
3. Identifier d'abord dans l’ensemble des titres :
- Si une personne ou institution est centrale → utiliser *Qui puis Quoi*.
- Sinon, si un lieu est central → utiliser *Où puis Quoi*.
- Sinon, si une date est l’élément fédérateur → utiliser *Quand puis Quoi*.
4. Tu dois uniquement répondre par le *titre final*, sans explication, sans justification. Aucun texte supplémentaire n’est autorisé.

*Maintenant, applique ces règles aux titres suivants :*  

Titres :  
{context}  

Titre général (strictement en {language}) :  
"""

prompt_client = ChatPromptTemplate.from_template(template_client)
prompt_resumer_general= ChatPromptTemplate.from_template(resumer_general)
prompt_titre_general= ChatPromptTemplate.from_template(template_titre_general)