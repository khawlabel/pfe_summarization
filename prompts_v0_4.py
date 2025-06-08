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
Ta tâche est de produire un résumé clair, structuré et informatif, à partir du *contexte fourni* ci-dessous. Tu dois respecter scrupuleusement toutes les consignes, notamment la **longueur maximale, sans ajout ni omission, et en conservant au maximum le vocabulaire du texte d’origine.

---

### 🎯 Objectif :
Résumer fidèlement le contenu, sans interprétation, reformulation excessive ni analyse personnelle, en conservant **tous les faits, chiffres, noms, formulations et dates essentiels.

---

### ⚠ Contraintes de forme OBLIGATOIRES :
- ✅ Longueur : entre 9 et 146 mots (≈ 80 mots recommandés).
- ✅ Nombre de caractères : entre 59 et 927 caractères.
- ✅ Nombre de phrases : 1 à 3 phrases (maximum 8).
- ✅ Un seul paragraphe, sans puces, sans liste, ni numérotation.
- ✅ Style neutre, journalistique et factuel.
- ⛔ Aucune introduction ni conclusion.
- ⛔ Interdiction absolue de formules comme :
    - "Résumé :", "Voici le résumé :", "En résumé", etc.
    - Le résumé doit commencer directement par la première phrase.

---

### 🧱 Structure logique imposée :
Toujours commencer par **[Qui] a annoncé / indiqué / déclaré / affirmé**, suivi obligatoirement (si elle est présente dans le texte) de **[Quand]**, puis de **[Quoi]**, **[Où]**, **[Comment]**, **[Pourquoi]** si l’information est disponible.

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

template_support = """
🧠 RÔLE : Expert en rédaction de résumés institutionnels.
📌 LANGUE : Toujours répondre en **français**, sans exception.
🎯 MISSION : Reprendre EXCLUSIVEMENT le contenu du RÉSUMÉ BRUT et le reformuler dans le style des RÉSUMÉS DE SUPPORT, **sans ajouter, inventer ou ôter la moindre information**.

---  
## RÉSUMÉ BRUT (source unique – contenu OBLIGATOIRE)  
{summary}  

---  
## EXEMPLES DE STYLE (contenu STRICTEMENT INTERDIT)  
{support_summary_1}
{support_summary_2}
{support_summary_3}


---  
🔒 CONSIGNES FERMES :  
1. **ZÉRO INTRODUCTION** : commence *directement* par la reformulation, sans phrase d’accroche (ex. « Voici le résumé… »).
2. **Interdit** : tout contenu factuel, terme ou chiffre issu des exemples de support.  
3. **Interdit** : ajouter ou omettre des informations du résumé brut.  
4. **Style uniquement** : guider ton, structure, niveau de langue, fluidité.  
5. Reformulation **intégrale** du texte brut, en paragraphes compacts.  
6. **Pas** de titres, puces, introduc­tions, commentaires, justifications ni rappel des consignes.  

✅ LIVRABLE : 1 texte unique, fluide et professionnel, fidèle au brut mais calqué stylistiquement sur les supports.

🛑 Toute violation (invention, omission, copie) sera considérée comme incorrecte.

✍️ FOURNIS **SEULEMENT** le texte final, sans autre élément. 
  
"""

prompt_resumer = ChatPromptTemplate.from_template(template_resumer)
prompt_traduction = ChatPromptTemplate.from_template(template_traduction)
prompt_resumer_general= ChatPromptTemplate.from_template(resumer_general)
prompt_titre_general= ChatPromptTemplate.from_template(template_titre_general)
prompt_support= ChatPromptTemplate.from_template(template_support)