import os
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import requests

# ==========================================
# 1. LE CONTRAT STRICT (Pydantic)
# ==========================================
# On force le LLM à formuler correctement sa requête.
class SearxngSearchInput(BaseModel):
    query: str = Field(..., description="La requête de recherche (mots-clés techniques, pas de phrases longues).")
    categories: str = Field(
        default="it,cyber", 
        description="Les catégories ciblées. Utilise 'it,cyber' pour le code, 'forums' pour les discussions, ou 'science' pour les papiers."
    )

# ==========================================
# 2. L'OUTIL NATIF CREWAI
# ==========================================
class BunkerSearchTool(BaseTool):
    name: str = "recherche_bunker_searxng"
    # La description est LUE PAR LE LLM. C'est son mode d'emploi.
    description: str = (
        "Le radar tactique du Bunker. Outil de recherche web SOUVERAIN. "
        "À utiliser OBLIGATOIREMENT pour vérifier les standards actuels (post-2023), "
        "le code, la documentation technique ou les CVE. "
        "Pénètre les documentations (GitHub, StackOverflow) sans censure SEO."
    )
    args_schema: type[BaseModel] = SearxngSearchInput

    def _run(self, query: str, categories: str = "it,cyber") -> str:
        # 🔌 Connexion dynamique : lit la variable d'environnement ou utilise la valeur locale par défaut
        base_url = os.getenv("SEARXNG_BASE_URL", "http://searxng_bunker:8080")
        url = f"{base_url}/search"
        
        params = {
            "q": query,
            "format": "json",
            "categories": categories,
            "safesearch": 0 # Aucun filtre moral, on veut la donnée brute
        }
        
        try:
            # Exécution de la frappe avec un timeout de sécurité
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            results = data.get("results", [])
            if not results:
                return f"⚠️ Le radar n'a rien trouvé pour les mots-clés : '{query}'"
            
            # Formatage de la réponse pour une ingestion parfaite par le LLM
            formatted_results = []
            # On limite aux 8 meilleurs résultats pour économiser les tokens (Focus !)
            for res in results[:8]: 
                titre = res.get("title", "Sans titre")
                lien = res.get("url", "")
                extrait = res.get("content", "Pas d'extrait disponible.")
                
                # Structure Markdown propre
                formatted_results.append(f"**[{titre}]**\n🔗 URL: {lien}\n📄 Extrait: {extrait}\n---")
                
            return "\n".join(formatted_results)
            
        except requests.exceptions.RequestException as e:
            return f"❌ Erreur réseau de connexion à SearXNG : {str(e)}"
        except Exception as e:
            return f"❌ Erreur interne de l'outil de recherche : {str(e)}"
