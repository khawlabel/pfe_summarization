
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

template_resumer_general = """
Ta tâche est de produire un **titre général unique** et un **résumé global structuré** à partir du **contexte ci-dessous**, composé de **plusieurs mini-résumés d’articles distincts** avec leurs titres.

🎯 Tu dois regrouper les **informations essentielles issues de *tous les articles*** dans :
1. **Un seul titre global** synthétisant le contenu dans son ensemble.
2. **Un seul résumé cohérent**, combinant tous les faits majeurs des différents mini-résumés, sans se concentrer uniquement sur un seul d’entre eux.

⛔ Tu ne dois **en aucun cas te limiter à un seul article**, même s’il est plus long ou plus détaillé que les autres.

---

### 📝 Pour le titre :
- ✅ Construire un **nouveau titre unique** à partir des **titres et contenus combinés**.
- ✅ Le titre **doit refléter l’ensemble des sujets abordés**, pas seulement un thème géographique ou technique.
- ✅ Style **informatif, concis**, sans majuscules superflues ni ponctuation inutile.
- ✅ Ne pas reprendre un titre existant s’il ne reflète pas tous les éléments.
- ✅ **Longueur** : 4 à 32 mots (≈ 12 mots recommandé).
- ✅ **Caractères** : 28 à 220 caractères.
- ✅ **Structure** : 1 seule phrase.

---

### ⚠ Contraintes de forme obligatoires pour le résumé :
- ✅ Entre **100 et 250 mots** (~190 mots recommandé).
- ✅ **1000 à 2000 caractères**.
- ✅ **3 à 5 phrases**, max 10.
- ✅ **Un seul paragraphe**.
- ✅ Style **neutre, journalistique, factuel**.
- ⛔ Ne jamais utiliser “Résumé :”, “En résumé” ou toute forme introductive.
- ❌ Si les limites sont dépassées ou non atteintes, **réécris la sortie** pour qu’elle soit conforme.
- 🚫 Aucune tolérance n’est acceptée en dehors des plages définies.

---

### 🧾 Règles de contenu :
- 🔹 N’ajoute aucune information non présente.
- 🔹 Utilise les formulations officielles.
- 🔹 Respecte tous les noms propres, chiffres, institutions, lieux, faits.
- 🔹 Évite toute redondance ou paraphrase inutile.
- 🔹 Ne garde que les faits significatifs, fusionne les éléments similaires.

---

### 💡 Aide à la fusion :
- 🧩 Identifie **les sujets clés** de chaque mini-résumé.
- 🧠 **Synthétise-les** de manière fluide et cohérente dans un texte unique.
- 🛑 **Ne traite pas un seul article comme le sujet principal**, même s’il est long ou détaillé.

---

Contexte (plusieurs mini-résumés d'articles) :  
{context}

---

⚠ Tu dois estimer la longueur (nombre de mots et de caractères) avant d'afficher le résultat final, et adapter ton résumé si nécessaire.

---

**Titre (strictement en {language})** :  

**Résumé (strictement en {language})** :  
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