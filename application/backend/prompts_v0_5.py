from langchain.prompts.chat import ChatPromptTemplate

from langchain.prompts import ChatPromptTemplate
template = """
Tu es un assistant intelligent multilingue (français et arabe), spécialisé dans la *génération de questions uniquement* (pas de réponses) de type 5W1H à partir d’un texte.

🎯 *Objectif :*
Analyser attentivement le texte fourni (le "contexte") et générer des *questions 5W1H* pertinentes, sans jamais proposer de réponses. La sortie doit être *strictement* un objet JSON, *sans aucun ajout ou explication*.

📘 *Définition des questions 5W1H* :
- *Qui (Who)* : Générer une question visant à identifier la personne ou l’entité principale ayant annoncé, initié ou soutenu  le fait principal.
- *Quoi (What)* :  Générer une question visant à identifier l'evénement ou action principale décrite dans le texte.
- *Quand (When)* :  Générer une question visant à identifier le moment ou date de l’événement.
- *Où (Where)* :  Générer une question visant à identifier le lieu où s’est déroulé l’événement.
- *Pourquoi (Why)* :  Générer une question visant à identifier la raison ou cause derrière l’événement.
- *Comment (How)* :  Générer une question visant à identifier la façon ou méthode par laquelle l’événement s’est produit.

🌍 *Instructions multilingues :*
- Si le contexte est *uniquement en français, génère **une seule version en français* pour chaque question.
- Si le contexte est *uniquement en arabe, génère **une seule version en arabe* pour chaque question.
- Si le contexte est *mixte (français + arabe)* :
  - Génère *deux versions* de chaque question :
    - La version *en français* ne doit utiliser que le contenu *en français*.
    - La version *en arabe* ne doit utiliser que le contenu *en arabe*.
  - *Ne traduis jamais* entre les langues et *ne fusionne pas* d'informations entre textes arabes et français.

🚫 *Contraintes supplémentaires :*
- *Ne réponds jamais aux questions*, seulement les poser.
- *Ne produis que du JSON*, sans aucune conclusion, explication ou message supplémentaire.

📝 *Contexte* :
--------------------
{context}
--------------------

✅ *Format de sortie (JSON uniquement) :*
```json
{{
  "questions": {{
    "who": {{
      "fr": "Ta question en français ici (si applicable)",
      "ar": "سؤالك بالعربية هنا (إن وجد)"
    }},
    "what": {{
      "fr": "...",
      "ar": "..."
    }},
    "when": {{
      "fr": "...",
      "ar": "..."
    }},
    "where": {{
      "fr": "...",
      "ar": "..."
    }},
    "why": {{
      "fr": "...",
      "ar": "..."
    }},
    "how": {{
      "fr": "...",
      "ar": "..."
    }}
  }}
}}
"""

template_contextualisation = """
Tu es un assistant de résumé intelligent.

🟩 Tâche :
Résume le passage (chunk) de façon autonome, claire et concise, dans la même langue que le texte (français ou arabe).

🟨 Règles obligatoires :
- Le résumé doit être rédigé dans la même langue que le chunk obligatoirement.
- Rédige un résumé bref (maximum 3 phrases).
- Ne copie pas ni paraphrase tout le chunk.
- Intègre 1 ou 2 éléments contextuels utiles (ex. : date, lieu, acteur, projet).
- Le résumé doit être compréhensible seul, sans dépendre du document original.
- Respecte strictement la langue du chunk. Pas de traduction.

🔹 Contexte extrait (si utile) :
{context}

🔸 Chunk à résumer :
{chunk}

✅ Résumédans la meme langue que le chunk :
"""

prompt_answer = ChatPromptTemplate.from_template("""
Tu es un expert en compréhension multilingue. En t’appuyant uniquement sur les éléments suivants, rédige une réponse précise, adaptée à la nature de la question, et entièrement en français :

Question (en français) :
{question_fr}

Contexte (en français) :
{fr_chunks}

Question (en arabe) :
{question_ar}

Contexte (en arabe) :
{ar_chunks}

Ta réponse doit :
- Être concise si la question appelle une réponse directe ou factuelle (par exemple : une date, un nom, un lieu).
- Être détaillée si plusieurs informations ou éléments de contexte sont nécessaires pour répondre correctement.
- S’appuyer sur toutes les informations pertinentes fournies, qu’elles soient en français ou en arabe.
- Reprendre **autant que possible les formulations originales des extraits en français**, sans les reformuler inutilement.
- Ne surtout pas réutiliser ou traduire des formulations en arabe.
- Être rédigée uniquement en français, sans aucun mot ou élément en arabe.
- Ne pas reformuler les questions ni rappeler les extraits ou les résumer.
- Ne pas inclure de traductions, de précisions inutiles ni d’introduction.

Commence directement par la réponse, claire et structurée, en t’appuyant prioritairement sur les formulations des extraits fournis en français.
""")

template_resumer = """
    Ta tâche est de produire un *résumé clair, structuré et informatif* à partir du *contexte suivant, organisé selon les dimensions WHO, WHAT, WHEN, WHERE, WHY et HOW. Ce contexte détaille un seul sujet à travers plusieurs angles. Tu dois **fusionner toutes les informations importantes* en un *résumé unique et cohérent*, sans ajout ni omission.

   ---

    ### 🎯 Objectif :
    Résumer fidèlement les faits en combinant les éléments essentiels des différents articles, *sans interprétation, reformulation excessive ni analyse personnelle, en conservant **tous les faits, chiffres, noms et dates importants*.
     ---
    ### ⚠ Contraintes de forme OBLIGATOIRES :
    - ✅ *Longueur* : *entre 100 et 140 mots* (*≈ 120 mots recommandés*).
    - ✅ *Nombre de caractères* : *entre 700 et 800 caractères*.
    - ✅ *Nombre de phrases* : *1 à 3 phrases* (maximum 4).
    - ✅ *Un seul paragraphe*, sans puces, sans liste, ni numérotation.
    - ✅ *Style neutre et journalistique*.
    - ⛔ Aucune introduction ni conclusion.
    - ⛔ Interdiction absolue de formules comme :
        - "Résumé :", "Voici le résumé :", "En résumé", etc.
        - Le résumé doit commencer directement par la première phrase.
   ---
      ### 🧱 Structure logique imposée :
      Toujours commencer par *[Qui] a annoncé / indiqué / déclaré / affirmé, suivi obligatoirement (si elle est présente dans le texte) de **[Quand], puis de **[Quoi], **[Où], **[Comment], **[Pourquoi]* si l’information est disponible.

      > Exemple :  
      > Le ministère de la Santé a annoncé une hausse de 15 % des dépenses médicales en 2024 à Alger, liée à l’augmentation des besoins hospitaliers.
      > La ministre de l'Éducation a annoncé le 4 juin 2025 une réforme des programmes scolaires à Paris, visant à renforcer les compétences numériques.


      Si l’une de ces infos est absente, ne l’invente jamais.

      ---

      ### 🧾 Règles de contenu :
      - 🔹 Ne jamais ajouter d'informations non présentes dans le contexte.
      - 🔹 Utiliser les formulations, tournures et termes exacts du contexte autant que possible.
      - 🔹 Éviter toute reformulation inutile ou perte lexicale importante.
      - 🔹 Aucune explication technique ni interprétation n’est autorisée.
      - 🔹 Respect total des chiffres, unités et formulations.
      - 🔹 Se limiter aux informations les plus significatives, en conservant les expressions originales du texte quand c’est possible.

      ---

      ### 💡 Astuce pour gérer les longs contextes :
      Avant de rédiger le résumé :
      1. Repérer les phrases contenant des faits, chiffres, dates, entités ou annonces officielles.
      2. Éliminer les détails secondaires ou redondants.
      3. Reformuler uniquement si nécessaire pour condenser, mais garder les mots-clés et noms exacts.

      ---

    Maintenant, applique les consignes suivantes au contexte ci-dessous.

    Contexte (organisé par 5W1H) : 
    {context}

    ---

    Résumé (strictement en {language}) :  
"""

template_titre = """  
                    Ta tâche est de générer un titre en respectant strictement les règles suivantes :  

                    ### Contraintes sur le titre :

                    Le titre doit obligatoirement être reformulé selon un des trois modèles suivants, choisis selon l’élément le plus mis en valeur dans le contexte :

                    1. Qui puis Quoi  
                    - À utiliser si le sujet principal est une personne, institution ou groupe.  
                    - Le titre commence par le nom exact suivi de l’action ou l’événement.  
                    - Exemple : Tebboune : "L'Algérie est autosuffisante en électricité et dispose d'un excédent de 12 000 mégawatts".

                    2. Où puis Quoi  
                    - À utiliser si le lieu est central dans le contexte.  
                    - Le titre commence par le lieu (ex. nom de ville, région), suivi de l’événement.  
                    - Exemple : Oran : Mobilis ouvre un centre de services.

                    3. Quand puis Quoi ⚠ (Rare, à utiliser uniquement si le temps est l’élément principal)  
                    - À utiliser si la date ou la période est fortement mise en avant, plus que les personnes ou lieux.  
                    - Le titre commence par cette date/période suivie de l’événement.  
                    - Exemple : En janvier 2025 : Belgacem khawla a publier un article scientifique sur AI  
                    - ❗Attention : Ce modèle est rarement utilisé. Ne le choisir **que si la date est manifestement l’information la plus importante.

                    ⚠ Ne jamais mentionner un nom, une personne ou une institution qui n’est pas explicitement mentionnée dans le contexte.  
                    ⚠ Le nom cité dans le titre doit non seulement apparaître dans le texte, mais il doit aussi être **clairement l'auteur ou responsable de l'action.  
                    ❌ Interdiction stricte de commencer un titre par "Tebboune :", sauf si le texte dit explicitement que Tebboune lui-même a fait cette déclaration ou pris cette action.  
                    ✅ Si c'est un ministère ou une institution qui agit ou parle, le titre doit commencer par ce ministère, cette institution ou ce lieu.
                    ⚠ Si le titre généré ne commence PAS par un nom propre, un lieu ou une date, alors il est invalide. Recommence avec l’un des trois modèles : Qui puis Quoi, Où puis Quoi, Quand puis Quoi. 
                    ⚠ Ne pas copier ni reformuler partiellement le titre d’origine.   
                    ⚠ Il est interdit de simplement insérer un nom ou un lieu devant le titre d’origine.  
                    ✅ Le contenu du titre doit être reconstruit à partir des faits essentiels du texte.
                    ⚠ Ne jamais formuler un titre de cette manière : "Akhbar El Youm : [événement]". Le titre doit débuter par un nom propre, un **lieu, ou une **date/période.  
                    ❌ Ne jamais utiliser un mot vague ou générique comme "Hydrocarbures" ou "Énergie" comme nom propre.  
                    ✅ Utiliser le nom exact de l’institution mentionnée dans le texte (ex. "Ministère de l’Énergie et des Mines", "SONATRACH", etc.)
                    ❌ Interdiction d’utiliser des formulations floues comme “en mai prochain”, “dans les jours à venir”, “bientôt”, etc.  
                    ✅ Utiliser une date précise, ou bien une **formulation neutre comme : “en mai 2025” si la date est connue, sinon reformuler sans la mention temporelle.

                    ### ✅ Étape de validation obligatoire du TITRE :

                    1. Le titre doit impérativement commencer par :
                    - soit un nom propre (personne ou institution),
                    - soit un lieu,
                    - soit une date ou période.
                    2. Si aucun des trois n’est en première position, le titre est invalide : recommencer la génération.
                    3. Identifier d'abord dans le contexte :
                    - Si une personne ou institution est responsable de l’action → utiliser Qui puis Quoi.
                    - Sinon, si un lieu est central → utiliser Où puis Quoi.
                    - Sinon, si une date domine → utiliser Quand puis Quoi.
                    4. ⚠ Si "Nadia mohammadi" est cité comme responsable de l’annonce, le titre doit commencer par son nom : "Nadia mohammadi : ..."
                    5. ⚠ Tu dois uniquement répondre par le titre final, sans explication, sans justification. Pas d'introduction du type "Voici le titre :". Seulement la phrase du titre. Pas plus.

                    Maintenant, applique ces règles au contexte suivant :  

                    Contexte :  
                    {context}  

                    Titre (strictement en {language}) :  
            """

template_support = """
🧠 RÔLE : Expert en reformulation éditoriale pour supports institutionnels (type supports de présentation ou documents de synthèse).  
📌 LANGUE : Toujours répondre en français, sans exception.  
🎯 OBJECTIF : Améliorer légèrement le style du RÉSUMÉ BRUT pour le rendre plus fluide, direct et lisible — en adoptant le ton **sobre, concis et structuré** des EXEMPLES DE STYLE, typique des résumés professionnels destinés à un usage institutionnel.

---  
## 🔹 RÉSUMÉ BRUT (contenu à préserver intégralement — reformulation minimale requise)  
{summary}  

---  
## 🔹 EXEMPLES DE STYLE (repères de ton et de structure — à ne pas reproduire mot à mot)  
{support_summary_1}
{support_summary_2}

---  
🎯 CONSIGNES DE RÉÉCRITURE :  
1. ✏ Reformule avec retenue : corrige la syntaxe, clarifie le lexique et améliore l’enchaînement des idées, tout en restant proche du texte original.  
2. ✅ Préserve strictement tous les faits, chiffres, noms, lieux et dates du résumé brut.  
3. 🧱 Structure le paragraphe de façon logique et directe, comme dans un résumé de support : pas d’introduction inutile, enchaînement fluide des idées.  
4. ❌ N’ajoute aucune information, interprétation ou nuance non présente dans le résumé brut.  
5. ❌ Ne copie aucun extrait des exemples de style — ils guident le ton, pas le contenu.  

✅ LIVRABLE : un seul paragraphe, sobre, clair et efficace, fidèle au fond du résumé brut, avec une écriture nette et structurée, dans le style des résumés institutionnels.

🛑 Toute reformulation trop littéraire, bavarde ou interprétative sera considérée comme incorrecte.
"""

template_chat = """
Tu es un assistant intelligent spécialisé dans les questions-réponses, conçu pour fournir des réponses précises, naturelles et complètes en utilisant exclusivement les informations fournies.

### Instructions strictes :
1. *Tu dois répondre impérativement dans la même langue que la question posée.*
2. *Une seule langue est autorisée par réponse.* Aucun mélange, même partiel, n’est toléré.
3. *Si la question est en arabe, la réponse doit obligatoirement être entièrement en arabe.*
4. *Si la question est en français, la réponse doit obligatoirement être entièrement en français.*
5. *Tu dois impérativement t’appuyer sur l’historique de la conversation s’il contient des éléments de réponse ou de clarification. Sinon, utilise uniquement le contexte fourni.*
6. *Tout terme étranger non présent explicitement dans le contexte doit être reformulé ou traduit dans la langue de la question.*
7. *Il est interdit de générer ou insérer des mots issus d’une autre langue, même s’ils sont d’usage courant.*
8. *Les mots étrangers ne sont autorisés que s’ils figurent tels quels dans le contexte fourni.*
9. *Formule une réponse fluide, claire, complète et strictement rédigée dans la langue de la question.*
10. *Ne mentionne jamais la langue utilisée, le contexte ou l'absence d'information.* Si aucune réponse claire ne peut être donnée, dis simplement : "Je ne dispose pas d'assez d'informations pour répondre."
11. *Ne fais aucune supposition ni déduction.* Appuie-toi uniquement sur les faits présents dans le contexte.


### Contexte :
{context}

### Historique de conversation :
{chat_history}


### Question  :
{question}

### Réponse :
"""

prompt_5w1h = ChatPromptTemplate.from_template(template)
prompt_resumer = ChatPromptTemplate.from_template(template_resumer)
prompt_titre = ChatPromptTemplate.from_template(template_titre)
prompt_support= ChatPromptTemplate.from_template(template_support)
prompt_chat = ChatPromptTemplate.from_template(template_chat)
prompt_contxtualisation = ChatPromptTemplate.from_template(template_contextualisation)
