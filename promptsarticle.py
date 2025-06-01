
from langchain_core.prompts import ChatPromptTemplate

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
                    - **Longueur** : **Entre 9 et 146 mots** (≈ 80 mots en moyenne).  
                    - **Caractères** : **Entre 59 et 927 caractères** (≈ 550 caractères en moyenne).  
                    - **Nombre de phrases** : **1 à 3 phrases** en général (**max 8**).  
                    - **Concision** : Clair, précis, sans analyse ni commentaire subjectif.  
                    - **Obligation** : Conserver **tous les faits les dates et chiffres essentiels**.  

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

template_resumer_general="""

Ta tâche est de produire un **titre et un résumé** structuré et informatif, à partir du **contexte fourni** ci-dessous, qui contient plusieurs mini-résumés d'articles avec leurs titres.  
Tu dois *regrouper les informations essentielles* dans *un unique titre et un unique résumé* sans ajout ni omission.

    ---

    ### 🎯 Objectif :
    Résumer fidèlement les faits en combinant les éléments essentiels des différents articles, *sans interprétation, reformulation excessive ni analyse personnelle, en conservant **tous les faits, chiffres, noms et dates importants*.

    ---

    ### ⚠ Contraintes de forme OBLIGATOIRES :
    - ✅ *Longueur* : *entre 100 et 250 mots* (*≈ 190 mots recommandés*).
    - ✅ *Nombre de caractères* : *entre 1000 et 2000 caractères*.
    - ✅ *Nombre de phrases* : *3 à 5 phrases* (maximum 10).
    - ✅ *Un seul paragraphe*, sans puces, sans liste, ni numérotation.
    - ✅ *Style neutre et journalistique*.
    - ⛔ *Interdiction d’introductions ou conclusions* ("Résumé :", "En résumé", etc.).

    ---

    ### 🧱 Structure logique imposée :
    Commencer par *[Qui] a annoncé / indiqué, suivi de **[Quoi], **[Quand], **Où, **Comment, **Pourquoi* si disponible.

    Exemple :  
    *Le ministère de la Santé a annoncé* une hausse de 15 % des dépenses médicales en 2024 à Alger, liée à l’augmentation des besoins hospitaliers.

    ---

    ### 🧾 Règles de contenu :
    - 🔹 *Ne jamais inventer d'informations* non présentes dans le contexte.
    - 🔹 *Reprendre les termes officiels exactement*.
    - 🔹 *Respect total des chiffres, des noms propres et des formulations*.
    - 🔹 Si certains détails sont secondaires ou redondants, *se concentrer sur les faits majeurs*.

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


template_chat = """
Tu es un assistant intelligent spécialisé dans les questions-réponses, conçu pour fournir des réponses précises, naturelles et complètes en utilisant exclusivement les informations fournies.

### Instructions :
1. **Réponds uniquement en {language}**, sans insérer de mots ou expressions issus d'autres langues, sauf si ces mots figurent dans le contexte fourni.
2. **Si un terme étranger est absent du contexte, reformule-le ou traduis-le dans la langue spécifiée ({language})**.
3. **Ne mélange jamais deux langues dans une même phrase (sauf si c'est nécessaire pour citer un terme du contexte)**.
4. **Ne génère jamais de mots étrangers de manière autonome**, même s'ils sont couramment utilisés dans d'autres langues.
5. Formule une **réponse fluide, informative et complète**, en respectant strictement la langue demandée.
6. **Tire pleinement parti du contexte fourni** pour garantir une réponse pertinente et détaillée.
7. **Ne mentionne ni le contexte, ni la source, ni l’absence d’information** ; si une réponse claire ne peut être donnée, dis simplement : "Je ne dispose pas d'assez d'informations pour répondre."
8. **Ne devine pas et ne complète pas avec des informations non fournies.** Reste fidèle aux faits présents dans le contexte.

### Langue requise : {language}

### Contexte :
{context}

### Question :
{question}

### Réponse ({language}) :
"""



prompt_resumer = ChatPromptTemplate.from_template(template_resumer)
prompt_resumer_general = ChatPromptTemplate.from_template(template_resumer_general)
prompt_chat = ChatPromptTemplate.from_template(template_chat)