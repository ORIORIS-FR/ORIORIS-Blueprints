import os
import time
import hashlib
import asyncio
import docker # <-- NOUVEAU: Pour lire le socket Docker
from datetime import datetime, timedelta

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import MemorySaver 
from langchain_core.tools import tool # <-- NOUVEAU: Pour créer l'outil Docker
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

# ==========================================
# 1. INITIALISATION DU CERVEAU (LLM)
# ==========================================
llm = ChatOpenAI(
    model="bunker-auto", 
    base_url="http://litellm_bunker:4000",
    api_key="sk-fucking-hole", 
    max_retries=2
)

# ==========================================
# 2. L'OUTIL DE SURVEILLANCE DOCKER (Capteur direct)
# ==========================================
@tool
def lire_logs_docker(nom_conteneur: str, lignes: int = 30) -> str:
    """
    Lit les dernières lignes de logs d'un conteneur Docker spécifique.
    Indispensable pour diagnostiquer une erreur système ou un crash.
    """
    try:
        # Se connecte au socket /var/run/docker.sock mappé dans le compose
        client = docker.from_env()
        conteneur = client.containers.get(nom_conteneur)
        logs = conteneur.logs(tail=lignes, stdout=True, stderr=True).decode("utf-8")
        return f"Logs de {nom_conteneur}:\n{logs}"
    except docker.errors.NotFound:
        return f"Erreur : Conteneur '{nom_conteneur}' introuvable. Vérifie le nom."
    except Exception as e:
        return f"Erreur système lors de la lecture du socket : {e}"

# ==========================================
# 2.B L'OUTIL DE RADAR GLOBAL
# ==========================================
@tool
def statut_infrastructure_docker() -> str:
    """
    Retourne l'état de santé actuel de tous les conteneurs Docker du Bunker (running, exited, restarting).
    À utiliser en premier pour savoir quels conteneurs nécessitent une inspection des logs.
    """
    try:
        client = docker.from_env()
        conteneurs = client.containers.list(all=True) # all=True permet de voir ceux qui ont crashé
        statuts = [f"- {c.name}: {c.status}" for c in conteneurs]
        return "État actuel de la flotte Docker:\n" + "\n".join(statuts)
    except Exception as e:
        return f"Erreur critique du radar système : {e}"

# ==========================================
# 3. LA BOUCLE PRINCIPALE (Le Cœur Asynchrone)
# ==========================================
async def main_loop():
    print("🔌 Connexion à l'armurerie n8n (Protocole MCP)...")
    
    # Configuration du client MCP (SearXNG via n8n)
    client_mcp = MultiServerMCPClient({
        "n8n_searxng": {
            "url": "http://n8n:5678/mcp/d498e040-fb00-4526-9771-9b0e35ed0db3",
            "transport": "sse"
        }
    })
        
    # On récupère les outils distants (MCP) et on y ajoute notre outil local Docker
    outils_mcp = await client_mcp.get_tools()
    outils_totaux = outils_mcp + [lire_logs_docker, statut_infrastructure_docker]
    
    # 🧠 Activation du disque dur cognitif (PostgreSQL)
    DB_URI = "postgresql://n8n_user:n8n_password@db_bunker:5432/n8n_database"
    
    # ⚠️ DÉBUT DU BLOC DE CONNEXION ⚠️
    async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:
        # Initialisation automatique des tables LangGraph dans Postgres
        await checkpointer.setup()
        
        # Injection de la mémoire dans l'agent
        agent = create_agent(llm, outils_totaux, checkpointer=checkpointer)
        
        # Paramétrage du cycle (MAINTENANT À L'INTÉRIEUR DU BLOC)
        INTERVALLE_JOURS = 3
        last_audit_time = datetime.now() - timedelta(days=INTERVALLE_JOURS)
        print("🛡️ Sniper en position. Mode Audit avec mémoire activé.")

        while True:
            jours_ecoules = (datetime.now() - last_audit_time).days
            trigger_temps = jours_ecoules >= INTERVALLE_JOURS

            if trigger_temps:
                print(f"⏳ Cycle écoulé. Lancement de l'audit...")
                last_audit_time = datetime.now()
                
                # Lecture des configs en direct pour avoir la version la plus fraîche
                try:
                    with open("/bunker_root/docker-compose.yml", "r") as f:
                        infra = f.read()
                    with open("/bunker_root/litellm_config/litellm-config.yaml", "r") as f:
                        config = f.read()
                    with open("/bunker_root/searxng_config/settings.yml", "r") as f:
                        searxng_conf = f.read()
                except Exception as e:
                    print(f"❌ Erreur de lecture des configs : {e}")
                    await asyncio.sleep(60) # Pause courte avant retry
                    continue
                    
                prompt = f"""
                Tu es l'architecte IA et le veilleur technologique autonome du système 'Bunker IA'.
                Voici l'infrastructure Docker actuelle : {infra}
                Voici la configuration de routage LiteLLM : {config}
                Voici les paramètres SearXNG : {searxng_conf}
                
                Mission :
                1. SÉCURITÉ & INFRA : Utilise SearXNG pour vérifier les failles récentes (CVE) sur nos images. 
                2. DIAGNOSTIC : 
                  - Utilise d'abord l'outil 'statut_infrastructure_docker' pour scanner l'ensemble du Bunker. 
                  - Si un conteneur a le statut 'exited', 'restarting' ou 'dead', utilise immédiatement l'outil 'lire_logs_docker' pour extraire ses erreurs. 
                  - Si tout est 'running', tu peux quand même inspecter les logs des conteneurs qui gèrent le flux d'informations critiques (litellm_bunker, agent_veille_bunker, n8n_bunker) pour t'assurer qu'il n'y a pas d'erreurs silencieuses.
                3. MARCHÉ LLM : Cherche les meilleures offres API gratuites (Free Tiers) disponibles ce mois-ci et propose des mises à jour concrètes pour le litellm-config.yaml.
                
                RÈGLES ABSOLUES : 
                - Ne rédige pas de rapport si rien n'a changé de manière significative depuis ta dernière vérification.
                - Cite toujours tes sources web.
                """
                
                # 🔒 LE VERROU DE MÉMOIRE (Thread ID persistant)
                config_execution = {"configurable": {"thread_id": "audit_routine_infrastructure"}}
                final_text = ""
                
                try:
                    # Exécution de l'agent avec la mémoire
                    async for chunk in agent.astream({"messages": [HumanMessage(content=prompt)]}, config=config_execution):
                        if "agent" in chunk:
                            msg = chunk["agent"]["messages"][-1]
                            if msg.tool_calls:
                                for tool_call in msg.tool_calls:
                                    print(f"🔎 Bobby exécute : '{tool_call['name']}' avec les arguments '{tool_call['args']}'")
                            if msg.content:
                                final_text = msg.content
                    
                    # Sauvegarde si l'agent a produit du contenu pertinent
                    if final_text and len(final_text) > 100:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"/obsidian_vault/00_INBOX/Bobby/rapport_bobby_{timestamp}.md"
                        
                        with open(filename, "w", encoding="utf-8") as f:
                            f.write(final_text)
                        print(f"🎯 Rapport sauvegardé : {filename}")
                    else:
                        print("🛑 Agent silencieux : Aucune nouveauté critique détectée. Rapport annulé.")
                        
                except Exception as e:
                    print(f"❌ Erreur tactique lors de la frappe : {e}")

            # Utilisation de asyncio.sleep au lieu de time.sleep pour ne pas bloquer le processus
            print("⏳ Mode veille profonde pour 24h.")
            await asyncio.sleep(86400) 
    # ⚠️ FIN DU BLOC DE CONNEXION (on n'y arrive jamais en théorie grâce au while True) ⚠️

# ==========================================
# 4. POINT D'ENTRÉE DU SCRIPT
# ==========================================
if __name__ == "__main__":
    asyncio.run(main_loop())