from langchain_core.prompts import ChatPromptTemplate

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
Ta tâche est de générer un *titre général* à partir des différents résumés fournis, en respectant strictement les règles suivantes :  

### *Contraintes sur le titre général* :

Le titre général doit obligatoirement être reformulé selon *un des trois modèles suivants*, choisis selon l’élément le plus mis en valeur dans l’ensemble des résumés donnés :

1. *Qui puis Quoi*  
- À utiliser si une *personne, institution ou groupe* est le sujet principal commun aux différents résumés.  
- Le titre commence par le *nom exact* suivi de l’action ou du résumé de l’ensemble des faits.  
- Exemple : Sonatrach : nouvelles stratégies et projets de développement en Algérie.

2. *Où puis Quoi*  
- À utiliser si un *lieu* est le fil conducteur principal entre les différents résumés.  
- Le titre commence par le *lieu* (ville, région, pays), suivi du résumé des faits ou dynamiques décrites.  
- Exemple : Algérie : investissements renforcés dans le secteur énergétique.

3. *Quand puis Quoi* ⚠ (Rare)  
- À utiliser uniquement si la *date ou la période* est clairement l’élément le plus important reliant tous les résumés.  
- Le titre commence par la *période* ou la *date*, suivie du résumé des événements ou dynamiques.  
- Exemple : En 2025 : l'Algérie accélère ses projets d'infrastructures et d'exportation énergétique.

⚠ *Ne jamais mentionner une personne, une institution ou un lieu qui n’est pas explicitement mentionné dans les résumés donnés.*  
⚠ Le nom cité dans le titre général doit apparaître dans les résumés fournis et être réellement central.  
⚠ *Ne pas simplement coller les résumés ensemble.* Il faut créer une reformulation synthétique qui capture l’idée dominante.

✅ Le contenu du titre général doit *synthétiser fidèlement* les informations, sans copier mot à mot les résumés existants.  
⚠ *Ne jamais reprendre intégralement un des résumés comme titre.*  
⚠ *Ne jamais formuler le titre de la manière "Résumé : ..." ou "Document : ..."*.  
✅ Toujours commencer par un *nom propre*, un *lieu* ou une *date/période*.  
❌ Ne jamais commencer par des mots vagues comme "Actualités", "Informations", etc.

### ✅ Étape de validation obligatoire du TITRE GÉNÉRAL :

1. Le titre général doit impérativement commencer par :
- soit un *nom propre* (personne, institution),
- soit un *lieu*,
- soit une *date/période*.
2. Si aucun des trois n’est en première position, le titre est *invalide* : *recommencer la génération*.
3. Identifier d'abord dans l’ensemble des résumés :
- Si une personne ou institution est centrale → utiliser *Qui puis Quoi*.
- Sinon, si un lieu est central → utiliser *Où puis Quoi*.
- Sinon, si une date est l’élément fédérateur → utiliser *Quand puis Quoi*.
4. Tu dois uniquement répondre par le *titre final*, sans explication, sans justification. Aucun texte supplémentaire n’est autorisé.

*Maintenant, applique ces règles aux résumés suivants :*  

Résumés :  
{context}  

Titre général (strictement en {language}) :  
"""


template_resumer = """
                Ta tâche est de produire un **résumé clair, structuré et informatif**, à partir du **contexte fourni** ci-dessous. Tu dois **respecter scrupuleusement toutes les consignes**, notamment la **longueur maximale**, sans ajout ni omission.

                ---

                ### 🎯 Objectif :
                Résumer fidèlement le contenu, **sans interprétation, reformulation excessive ni analyse personnelle**, en conservant **tous les faits, chiffres, noms et dates essentiels**.

                ---

                ### ⚠️ Contraintes de forme OBLIGATOIRES :
                - ✅ **Longueur** : **entre 9 et 146 mots** (**≈ 80 mots recommandés**).
                - ✅ **Nombre de caractères** : **entre 59 et 927 caractères**.
                - ✅ **Nombre de phrases** : **1 à 3 phrases** (maximum 8).
                - ✅ **Un seul paragraphe**, sans puces, sans liste, ni numérotation.
                - ✅ **Style neutre et journalistique**.
                - ⛔️ **Aucune introduction ni conclusion**.
                - ⛔️ **Interdiction absolue de formules comme** :
                    - "Résumé :", "Voici le résumé :", "En résumé", etc.
                    - Le résumé doit **commencer directement** par la première phrase.
                
                ---

                ### 🧱 Structure logique imposée :
                Commence toujours par **[Qui] a annoncé / indiqué**, suivi de **[Quoi]**, **[Quand]**, **[Où]**, **[Comment]**, **[Pourquoi]** si disponible.

                > Exemple :  
                > **Le ministère de la Santé a annoncé** une hausse de 15 % des dépenses médicales en 2024 à Alger, liée à l’augmentation des besoins hospitaliers.

                Si l’une de ces infos est absente, **ne l’invente jamais**.

                ---

                ### 🧾 Règles de contenu :
                - 🔹 **Ne jamais ajouter d'informations non présentes dans le contexte.**
                - 🔹 **Reprendre les termes du contexte exactement** : pas de reformulation des noms officiels.
                - 🔹 **Aucune explication technique ni interprétation** n’est autorisée.
                - 🔹 **Respect total des chiffres, unités et formulations.**
                - 🔹 Si le document est long, **ne résume que les faits essentiels et prioritaires**, **sans perdre l'information principale**.

                ---

                ### 💡 Astuce pour gérer les longs contextes :
                Avant de rédiger le résumé :
                1. **Identifie les phrases contenant des faits, chiffres, dates, entités ou annonces.**
                2. **Ignore les détails secondaires ou répétés.**
                3. **Ne conserve que l’essentiel pour rester dans la limite de mots.**

                ---

                Maintenant, applique les consignes suivantes au contexte ci-dessous.

                Contexte :  
                {context}

                ---

                Résumé (en {language}) :
                """


template_traduction =  """
    Vous êtes un traducteur professionnel. Votre tâche est de traduire le texte ci-dessous du français vers l'arabe. Voici les règles que vous devez suivre pour cette traduction :
    
    1. **Conservez la structure du texte intacte** : Le titre et le resume.
    2. **Ne modifiez pas l'ordre du texte** : Assurez-vous que l'ordre des phrases et des idées reste fidèle à l'original.
    3. **Effectuez uniquement la traduction linguistique** : Votre seul travail est de traduire le texte du français vers l'arabe, sans changer aucun autre aspect du contenu.
    4. **Veillez à la fluidité et la précision** de la traduction en arabe, en respectant les règles grammaticales et stylistiques de la langue cible.

    Voici le texte à traduire : 
    {resume_francais}
    """

prompt_resumer = ChatPromptTemplate.from_template(template_resumer)
prompt_traduction = ChatPromptTemplate.from_template(template_traduction)
prompt_resumer_general= ChatPromptTemplate.from_template(resumer_general)
prompt_titre_general= ChatPromptTemplate.from_template(template_titre_general)