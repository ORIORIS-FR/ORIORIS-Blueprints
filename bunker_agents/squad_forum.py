import os
import sys
import re
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from crewai_tools import ScrapeWebsiteTool
from outils.searxng_tool import BunkerSearchTool

# ==========================================
# 🔌 CONNEXION AU BUNKER (ROUTAGE NATIF 2026)
# ==========================================
# On force l'API interne de CrewAI à taper sur le proxy LiteLLM via l'environnement.
os.environ["OPENAI_API_BASE"] = os.getenv("LITELLM_API_BASE", "http://litellm_bunker:4000/v1")
os.environ["OPENAI_API_KEY"] = os.getenv("LITELLM_API_KEY", "VOTRE_CLE_API_ICI")

# ==========================================
# 🛠️ L'ARSENAL (Accès Internet)
# ==========================================
# Donne la capacité à l'IA d'aller lire le contenu d'un lien (forum, doc)
scrape_tool = ScrapeWebsiteTool()
recherche_poussee = BunkerSearchTool()

# ==========================================
# 🤖 DÉFINITION DE L'ARMÉE
# ==========================================
eclaireur = Agent(
    role="Expert Veilleur Technique",
    goal="Analyser le problème depuis l'URL fournie ou le texte, et extraire la contrainte technique exacte.",
    backstory="Tu es un analyste système implacable. Tu n'inventes rien. Tu utilises tes outils pour lire la documentation ou les forums web afin de trouver la racine du blocage.",
    verbose=True,
    allow_delegation=False,
    tools=[scrape_tool, recherche_poussee],
    llm="openai/bunker-auto" 
)

mecano = Agent(
    role="Architecte d'Automatisation Senior",
    goal="Générer la solution technique n8n (code JS ou JSON) basée sur l'analyse de l'Éclaireur.",
    backstory="Tu es un développeur Docker et n8n d'élite. TA RÈGLE ABSOLUE: Ta base de connaissances interne s'arrête en 2023. Tu as l'INTERDICTION de proposer du code JS ou JSON sans avoir PRÉALABLEMENT exécuté l'outil 'recherche_bunker_searxng' pour vérifier les standards actuels de l'année 2026. Ton code doit être parfait, indenté et directement copiable.",    verbose=True,
    allow_delegation=False,
    tools=[recherche_poussee],
    llm="openai/bunker-code"
)
# ==========================================
# 🎯 DÉFINITION DE LA MISSION (Traçabilité Totale)
# ==========================================
# n8n va maintenant envoyer 3 arguments : URL, Auteur, Titre
if len(sys.argv) > 3:
    cible = sys.argv[1]
    auteur = sys.argv[2]
    titre_probleme = sys.argv[3]
else:
    cible = "https://community.n8n.io/t/test"
    auteur = "Utilisateur_Test"
    titre_probleme = "Test de routage local"

print(f"📡 Cible verrouillée : {titre_probleme} (par {auteur})")

# ... [Tes Tasks et ton Crew ne changent pas] ...

tache_analyse = Task(
    description=f"Voici la cible : '{cible}'. S'il s'agit d'une URL, utilise ton outil de scraping pour lire le contenu de la page. Analyse l'erreur technique décrite par l'utilisateur.",
    expected_output="Un diagnostic clair en 3 points identifiant la cause du blocage.",
    agent=eclaireur
)

tache_solution = Task(
    description="À partir du diagnostic, rédige la solution technique définitive. Fournis le code JavaScript (Node) ou la structure JSON du nœud n8n.",
    expected_output="Un bloc de code propre avec une explication technique stricte.",
    agent=mecano
)

# ==========================================
# 🎩 DÉPLOIEMENT
# ==========================================
squad = Crew(
    agents=[eclaireur, mecano],
    tasks=[tache_analyse, tache_solution],
    process=Process.sequential
)
# ==========================================
# 📦 FORMATAGE ET LIVRAISON (Le Sas Obsidian)
# ==========================================
print("🛡️ Lancement de l'assaut...")
resultat = squad.kickoff()

# 1. Nettoyage du titre pour créer un nom de fichier Windows valide
titre_propre = re.sub(r'[\\/*?:"<>|]', "", titre_probleme).replace(" ", "_")[:40]
date_du_jour = datetime.now().strftime("%Y%m%d_%H%M")
nom_fichier = f"{date_du_jour}_{auteur}_{titre_propre}.md"

# 2. Le Sas de réception (INBOX)
dossier_inbox = "/obsidian_vault/00_INBOX"
os.makedirs(dossier_inbox, exist_ok=True)
chemin_sortie = os.path.join(dossier_inbox, nom_fichier)

# 3. Création des propriétés Obsidian (Frontmatter)
frontmatter = f"""---
titre_original: "{titre_probleme}"
auteur: "{auteur}"
source: "{cible}"
date_capture: {datetime.now().strftime("%Y-%m-%d %H:%M")}
statut: a_valider
tags:
  - n8n/resolution
  - IA/squad
---

# Analyse et Solution : {titre_probleme}
*Problème soumis par **{auteur}** sur le forum n8n.*

---

"""

# 4. Écriture du fichier final
with open(chemin_sortie, "w", encoding="utf-8") as f:
    f.write(frontmatter + resultat.raw)
    
print(f"🎯 Colis livré dans le Sas : {nom_fichier}")
