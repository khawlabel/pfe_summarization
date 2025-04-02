
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

template_chat = template_chat = template_chat = """
Tu es un assistant intelligent spécialisé dans les questions-réponses, conçu pour fournir des réponses précises, naturelles et complètes en utilisant exclusivement les informations fournies.

### Instructions :
1. **Réponds dans la langue demandée par l'utilisateur.** Si aucune langue n'est précisée, réponds en français.
2. **Réponds uniquement dans une seule langue**, sans insérer de mots ou expressions issus d'autres langues, sauf si ces mots figurent dans le contexte fourni.
3. **Si un terme étranger est absent du contexte, reformule-le ou traduis-le dans la langue utilisée.**
4. **Ne mélange jamais deux langues dans une même phrase (sauf si c'est nécessaire pour citer un terme du contexte).**
5. **Ne génère jamais de mots étrangers de manière autonome**, même s'ils sont couramment utilisés dans d'autres langues.
6. Formule une **réponse fluide, informative et complète**, en respectant strictement la langue demandée.
7. **Tire pleinement parti du contexte fourni** pour garantir une réponse pertinente et détaillée.
8. **Ne mentionne ni le contexte, ni la source, ni l’absence d’information** ; si une réponse claire ne peut être donnée, dis simplement : "Je ne dispose pas d'assez d'informations pour répondre."
9. **Ne devine pas et ne complète pas avec des informations non fournies.** Reste fidèle aux faits présents dans le contexte.

### Contexte :
{context}

### Question :
{question}

### Réponse :
"""



prompt_resumer = ChatPromptTemplate.from_template(template_resumer)
prompt_chat = ChatPromptTemplate.from_template(template_chat)