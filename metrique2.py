import sys
sys.path.append("./BARTScore")  # adapter si nécessaire

from bart_score import BARTScorer

# Initialise le modèle
bart_scorer = BARTScorer(device="cpu", checkpoint='facebook/bart-large-cnn')

# Texte source
# Tes données : les documents sources et le résumé généré
context = """
\n\n\nFIBRE OPTIQUE FTTH\n\nPlus de 1,5 millions de foyers connectés\n\nCONFORMÉMENT aux directives du Président de la République Abdelmadjid Tebboune visant à généraliser la 
technologie, notamment la numérisation totale, le nombre de foyers connectés à la fibre optique jusqu’au domicile (FTTH) a franchi la barre de 1,5 million au début du mois d’octobre 2024. C’est ce qu’a indiqué, hier, un communiqué du ministère de la Poste et des Télécommunications. « Conformément à l’objectif de numérisation globale et en application des directives de Monsieur le Président de la République concernant la généralisation de la technologie de la fibre optique, la mise en œuvre du plan d’action a permis d’atteindre 1,5 million de foyers connectés au réseau de fibre optique jusqu’au domicile (FTTH) », précise le ministère. Cette évolution traduit une croissance exponentielle de l’accès à cette technologie FTTH. Le pays est passé de 53 000 foyers raccordés en 2020 à un million en novembre 2023, avant de dépasser le seuil de 1,5 million en 2024. Ces abonnés sont répartis à travers les 58 wilayas, ce qui reflète une couverture étendue et équilibrée. En parallèle de cette augmentation, l’amélioration de la qualité de service est au cœur des préoccupations. « Algérie Télécom propose désormais des offres attractives avec des débits allant jusqu’à 1 gigabit par seconde, permettant aux usagers de profiter d’une expérience Internet optimale. Cette 
technologie garantit une connexion rapide et fiable, sans interférence, en utilisant des câbles en fibre optique sur l’ensemble du parcours, du nœud de connexion au domicile de l’abonné », a souligné la même source. Selon Algérie Télécom, le programme de déploiement de la fibre optique reste en cours et vise notamment la connexion des nouveaux quartiers et pôles urbains encore non desservis. Il inclut également la modernisation des infrastructures existantes, avec une migration progressive des abonnés de l’ancienne technologie xDSL vers le réseau FTTH, offrant ainsi à ces derniers une connexion à très haut débit. Cette dynamique s’inscrit dans un effort global d’expansion du réseau Internet fixe en Algérie. « Depuis 2020, le nombre total de foyers connectés est passé de 3,5 millions à 5,8 millions en octobre 2024. Cette évolution constitue un levier important pour soutenir la 
transformation numérique du pays et favoriser l’accès aux services digitaux pour tous les citoyens », a conclu la même source.']
["Le ministère de la Poste et des Télécommunications a annoncé que plus de 1,5 million de foyers sont connectés à la fibre optique jusqu'au domicile (FTTH) au début du mois d'octobre 2024. Cette évolution traduit une croissance exponentielle de l'accès à cette technologie FTTH, qui est en train de généraliser la numérisation totale en Algérie. Les abonnés sont répartis à travers les 58 wilayas, ce qui reflète une couverture étendue et équilibrée."""
  # Texte source utilisé dans la génération
generated_summary = """
 Le ministère de la Poste et des Télécommunications a annoncé que plus de 1,5 million de foyers sont connectés à la fibre optique jusqu'au domicile (FTTH) au début du mois d'octobre 2024. Cette évolution traduit une croissance exponentielle de l'accès à cette technologie FTTH, qui est en train de généraliser la numérisation totale en Algérie. Les abonnés sont répartis à travers les 58 wilayas, ce qui reflète une couverture étendue et équilibrée.
   """  # Résumé généré par le LLM

# Évalue si le résumé est plausible en fonction du contexte
score = bart_scorer.score([context], [generated_summary])
print("BARTScore (source → résumé):", score[0])


