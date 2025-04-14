
from langchain_core.prompts import ChatPromptTemplate

template_resumer = """  
                Ta tâche est de générer un **résumé** en respectant strictement les règles suivantes :  

                ### **Règles générales** :  
                - **Ne jamais ajouter d'informations extérieures au contexte fourni.**  
                - **Ne pas analyser ni interpréter les faits.** Fournis uniquement les informations essentielles.  
                - **Le résumé doit être direct et informatif, sans liste à puces.**  
                - **Respecte le style journalistique** : phrases structurées, neutres et précises.  
                - **Ne pas ajouter d’introduction ou de conclusion.**  
                - **Mentionner les chiffres et faits marquants sans reformulation inutile.**  

                ### **Règles spécifiques à respecter impérativement :**  

                1. **Reprendre les termes du contexte exactement comme ils apparaissent.**  
                - **Interdiction stricte de modifier ou reformuler les noms officiels.**  
                - **Exemple interdit :** "La ministre des Télécommunications" si le texte mentionne "le ministère".  

                2. **Ne pas introduire de causes ou justifications non mentionnées.**  
                - **Exemple interdit :** Dire que l’augmentation est due à un "programme de développement" si cela n'est pas explicitement écrit.  
                - **Exemple interdit :** Ajouter "directives du Président" si cela n’apparaît pas dans le texte source.  

                3. **Ne jamais ajouter d’explications techniques non présentes.**  
                - **Exemple interdit :** "L'innovation a amélioré la vitesse de téléchargement" si cela n'est pas dit.  

                4. **Respect strict des chiffres et des formulations du contexte.**  
                - **Ne pas changer "foyers connectés" en "accès internet"** si ce n'est pas la même unité.  
                - **Reprendre exactement les chiffres tels qu’ils apparaissent.**  

                ---

                ### **Contraintes sur le résumé** :  
                - **Longueur** : **Entre 9 et 146 mots** (≈ 80 mots en moyenne).  
                - **Caractères** : **Entre 59 et 927 caractères** (≈ 550 caractères en moyenne).  
                - **Nombre de phrases** : **1 à 3 phrases** en général (**max 8**).  
                - **Concision** : Clair, précis, sans analyse ni commentaire subjectif.  
                - **Obligation** : Conserver **tous les faits les dates et chiffres essentiels**.  

                ---

                ### **Structure logique obligatoire du résumé** :  
                Identifie d'abord ces informations si elles sont présentes :
                1. **Qui a fourni ou annoncé l’information** (ex. : un ministère, une entreprise, un responsable, un porte-parole, etc.)   
                2. **Quoi** s’est passé (événement principal)  
                3. **Où** cela s’est produit (si mentionné)  
                4. **Quand** cela a eu lieu (si mentionné)  
                5. **Comment** cela s’est déroulé (si mentionné)  
                6. **Pourquoi** cela a eu lieu (uniquement si précisé)  

                🟥 **Règle absolue de rédaction du résumé** :

                - **Toujours commencer par** :  
                > **[Qui] a annoncé**, **[Quoi]**, **[Quand]**, **[Où]**, **[Comment]**, **[Pourquoi]**  
              
                - ⛔️ Il est **interdit de commencer par l’événement lui-même**, même s’il est mentionné en premier dans le contexte.

                - ✅ **La première phrase du résumé doit impérativement commencer par la source de l'information**, suivie immédiatement de l’événement, sans reformulation.

                > 🟡 **Important** :  
                > - Le **"Qui"** correspond **à la source initiale de l’information** (ex. : "selon le ministère", "le PDG a déclaré", etc.),  
                > - Ce **n’est pas le journaliste**, ni "selon le rapport" sauf si c’est ce qui est explicitement mentionné.  
                > - Si certains éléments sont absents du contexte, **ne les invente jamais**.  

                ---

                **Maintenant, applique ces règles au contexte suivant :**  

                Contexte :  
                {context}  

                Résumé (strictement en {language}) :  
                """

template_titre = """  
                    Ta tâche est de générer un *titre* en respectant strictement les règles suivantes :  

                    ### *Contraintes sur le titre* :

                    Le titre doit obligatoirement être reformulé selon *un des trois modèles suivants*, choisis selon l’élément le plus mis en valeur dans le contexte :

                    1. *Qui puis Quoi*  
                    - À utiliser si le sujet principal est une *personne, institution ou groupe*.  
                    - Le titre commence par le *nom exact* suivi de l’action ou l’événement.  
                    - Exemple : Tebboune : "L'Algérie est autosuffisante en électricité et dispose d'un excédent de 12 000 mégawatts".

                    2. *Où puis Quoi*  
                    - À utiliser si le *lieu* est central dans le contexte.  
                    - Le titre commence par le lieu (ex. nom de ville, région), suivi de l’événement.  
                    - Exemple : Oran : Mobilis ouvre un centre de services.

                    3. *Quand puis Quoi* ⚠ (Rare, à utiliser uniquement si le temps est l’élément principal)  
                    - À utiliser si la *date ou la période* est fortement mise en avant, plus que les personnes ou lieux.  
                    - Le titre commence par cette date/période suivie de l’événement.  
                    - Exemple : En janvier 2025 : Belgacem khawla a publier un article scientifique sur AI  
                    - ❗*Attention : Ce modèle est rarement utilisé. Ne le choisir **que si* la date est manifestement l’information la plus importante.

                    ⚠ *Ne jamais mentionner un nom, une personne ou une institution qui n’est pas explicitement mentionnée dans le contexte.*  
                    ⚠ Le nom cité dans le titre doit *non seulement apparaître dans le texte, mais il doit aussi être **clairement l'auteur ou responsable de l'action*.  
                    ❌ *Interdiction stricte* de commencer un titre par "Tebboune :", sauf si le texte dit explicitement que *Tebboune lui-même a fait cette déclaration ou pris cette action*.  
                    ✅ Si c'est un ministère ou une institution qui agit ou parle, le titre doit commencer par ce ministère, cette institution ou ce lieu.
                    ⚠ Si le titre généré ne commence PAS par un nom propre, un lieu ou une date, alors il est invalide. Recommence avec l’un des trois modèles : Qui puis Quoi, Où puis Quoi, Quand puis Quoi. 
                    ⚠ *Ne pas copier ni reformuler partiellement le titre d’origine.*  
                    ⚠ *Il est interdit de simplement insérer un nom ou un lieu devant le titre d’origine.*  
                    ✅ Le contenu du titre doit être *reconstruit* à partir des faits essentiels du texte.
                    ⚠ *Ne jamais formuler un titre de cette manière* : "Akhbar El Youm : [événement]". Le titre doit débuter par un *nom propre, un **lieu, ou une **date/période*.  
                    ❌ Ne jamais utiliser un mot vague ou générique comme "Hydrocarbures" ou "Énergie" comme nom propre.  
                    ✅ Utiliser *le nom exact de l’institution* mentionnée dans le texte (ex. "Ministère de l’Énergie et des Mines", "SONATRACH", etc.)
                    ❌ Interdiction d’utiliser des formulations floues comme “en mai prochain”, “dans les jours à venir”, “bientôt”, etc.  
                    ✅ Utiliser une date *précise, ou bien une **formulation neutre* comme : “en mai 2025” si la date est connue, sinon reformuler sans la mention temporelle.

                    ### ✅ Étape de validation obligatoire du TITRE :

                    1. Le titre doit impérativement commencer par :
                    - soit un *nom propre* (personne ou institution),
                    - soit un *lieu*,
                    - soit une *date ou période*.
                    2. Si aucun des trois n’est en première position, le titre est *invalide* : *recommencer la génération*.
                    3. Identifier d'abord dans le contexte :
                    - Si une personne ou institution est responsable de l’action → utiliser *Qui puis Quoi*.
                    - Sinon, si un lieu est central → utiliser *Où puis Quoi*.
                    - Sinon, si une date domine → utiliser *Quand puis Quoi*.
                    4. ⚠ Si "Nadia mohammadi" est cité comme responsable de l’annonce, le titre doit commencer par son nom : *"Nadia mohammadi : ..."*
                    3. ⚠ Tu dois uniquement répondre par le *titre final*, sans explication, sans justification. Pas d'introduction du type "Voici le titre :". Seulement la phrase du titre. Pas plus.

                    *Maintenant, applique ces règles au contexte suivant :*  

                    Contexte :  
                    {context}  

                    Titre (strictement en {language}) :  
"""

template_chat = """
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

template_ameliore_ar = """
أنت مساعد ذكي ومتخصص في تحسين النصوص باللغة العربية الفصحى. مهمتك هي تحسين النص التالي ليصبح ملخصًا واضحًا، منسقًا، دقيقًا، ومكتوبًا باللغة العربية الفصحى فقط، دون أي تأثير من لغات أخرى.

### تعليمات محددة:
1. **ترجم جميع المصطلحات الأجنبية** (مثل "fibre optique"، "internet"، "membrane"، إلخ) إلى العربية الفصحى باستخدام المصطلحات الصحيحة المتعارف عليها في اللغة العربية.
2. **تجنب تمامًا** استخدام أي كلمات أو عبارات من اللغات الأجنبية مثل الإنجليزية أو الفرنسية داخل النص. يجب أن تكون جميع المصطلحات الأجنبية مترجمة بالكامل إلى اللغة العربية الفصحى.
3. **تحسين الأسلوب الكتابي** ليكون النص سلسًا، دقيقًا، ومناسبًا للقارئ العربي. يجب أن يكون النص خاليًا من التكرار غير الضروري أو الغموض.
4. **احرص على المحافظة على المعنى الأصلي** للنص، مع مراعاة الحفاظ على دقة المعلومات وعدم حذف أي جزء من النص الذي قد يؤدي إلى تغيير المعنى.
5. **تحسين عنوان النص** ليكون مختصرًا، معبرًا عن المحتوى بدقة، ويجب أن يتضمن جميع المعلومات المهمة دون اللجوء إلى عبارات طويلة أو معقدة.
6. **صياغة الفقرات بشكل منظم** مع التركيز على تقديم المعلومات الرئيسية أولًا، وتقديم التفاصيل بشكل مناسب وتدريجي. تأكد من أن كل فقرة متسقة مع الفقرة السابقة.
7. **استخدام علامات الترقيم المناسبة** مثل الفواصل (،) والنقاط (.) لتقسيم الجمل والأفكار بشكل يسهل قراءتها وفهمها.
8. **تأكد من أن النص مكتوب باللغة العربية الفصحى** فقط، مع تجنب أي لهجات محلية أو تعبيرات غير رسمية.
9. **التركيز على وضوح الفكرة الأساسية** مع تجنب الغموض أو الجمل الطويلة المعقدة.
10. **إذا كان النص يحتوي على قائمة أو معلومات تفصيلية**، قدمها بشكل واضح وبصيغة مفهومة دون استخدام عبارات معقدة.
11. **لا تضف أي ملاحظات**: التركيز فقط على تحسين النص كما هو.


### التعليمات الإضافية:
- يجب أن تحتفظ دائمًا بالهيكل التالي في النص المحسن:
    - **العنوان :** [إدخال العنوان المحسن هنا]
    - **الملخص :** [إدخال الملخص المحسن هنا]
- تأكد من أن العنوان يجب أن يكون مختصرًا، شاملاً وواضحًا.
- تأكد من أن الملخص يجب أن يكون دقيقًا، خاليًا من الأخطاء اللغوية، ومكتوبًا بلغة عربية فصحى، مع الاهتمام بتوضيح المعلومات بشكل مرتب وسلس.

### النص المراد تحسينه:
{texte_brut}

### المخرجات المطلوبة:
1. **العنوان :** يجب أن يكون مختصرًا، شاملاً وواضحًا.
2. **الملخص :** يجب أن يكون دقيقًا، خاليًا من الأخطاء اللغوية، ومكتوبًا بلغة عربية فصحى، مع الاهتمام بتوضيح المعلومات بشكل مرتب وسلس.
3. **التأكد من أن النص المحسن خالي تمامًا من أي كلمات أو مصطلحات أجنبية** أو غير فصيحة.
4. **لا تذكر أي معلومات إضافية غير واردة في النص الأصلي**، ولا تضف أي تفاصيل غير موجودة في السياق.

أعطني النص المحسن فقط.

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
prompt_titre = ChatPromptTemplate.from_template(template_titre)
prompt_chat = ChatPromptTemplate.from_template(template_chat)
prompt_ameliore_ar= ChatPromptTemplate.from_template(template_ameliore_ar)
prompt_traduction = ChatPromptTemplate.from_template(template_traduction)