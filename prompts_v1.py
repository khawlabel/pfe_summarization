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

prompt_client = ChatPromptTemplate.from_template(template_client)