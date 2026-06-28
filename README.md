# 🛡️ ORIORIS Blueprints : Veille Agentique Automatisée (Bunker IA)

![Version](https://img.shields.io/badge/Version-1.0.0-blue)
![Stack](https://img.shields.io/badge/Stack-n8n%20%7C%20CrewAI%20%7C%20Docker-success)
![Status](https://img.shields.io/badge/Status-Production_Ready-brightgreen)

> *Infrastructure de veille agentique basée sur une architecture modulaire et locale : Détection (n8n), Raisonnement (CrewAI/LangGraph) et Persistance (Qdrant/Obsidian). Ce projet industrialise la capture et la résolution de problèmes techniques issus de forums communautaires.*

---

## 🎯 Le Cas d'Usage : "Squad Forum"

Monitorer des forums techniques (ex: communauté n8n) génère une surcharge cognitive massive. Ce système automatise la boucle de **Détection -> Analyse -> Résolution -> Documentation** directement dans un "Digital Garden" local (Obsidian).

### 🏗️ Architecture du Flux (VSL)

```mermaid
graph TD
    %% --- Flux de Veille ---
    subgraph Forum [Forum Community n8n]
        A[n8n Forum] -->|Scan horaire| B(Schedule Trigger)
    end

    subgraph Acquisition [Pipeline Acquisition]
        B -->|HTTP Request| C[n8n_discourse_squad]
        C -->|Split & Filter| D{Detection Error/Bug}
        D -->|Nouveau| E[Dépôt cible_XXX.json]
    end

    %% --- Flux d'Intelligence ---
    subgraph Bunker [Bunker IA - Agentic Core]
        E -->|Guetteur| F(Agent Guetteur_Squad)
        F -->|Lecture| G{Comparaison<br>cibles_traitées.txt}
        G -->|Inédit| H[Traitement Agentique]
    end

    subgraph Squad [Escouade CrewAI]
        H --> I[Expert Veilleur Technique]
        I -->|Recherche SearXNG| J[Recherche contextuelle]
        J --> K[Architecte Senior]
        K -->|Rédaction| L[Note Obsidian<br>00_INBOX]
    end

    %% --- Rangement ---
    L -->|Archivage| M[cibles_traitées.txt]

    %% --- Styles ---
    style Forum fill:#f39c12,stroke:#fff,color:#fff
    style Bunker fill:#2c3e50,stroke:#f1c40f,color:#fff
    style Squad fill:#2980b9,stroke:#fff,color:#fff
    style L fill:#8e44ad,stroke:#fff,color:#fff
    style G fill:#c0392b,stroke:#fff,color:#fff
```
---
📂 Anatomie du Dépôt
L'architecture est segmentée pour garantir une isolation stricte entre l'acquisition (n8n) et l'exécution cognitive (Python).

```Plaintext
ORIORIS-Blueprints/
├── README.md                              # Ce document
├── n8n_workflows/
│   └── acquisition_discourse_forum.json   # Workflow d'acquisition sanitisé
└── bunker_agents/
    ├── squad_forum.py                     # L'escouade CrewAI (Éclaireur & Mécano)
    ├── guetteur_squad.py                  # Démon de surveillance des fichiers
    ├── agent.py                           # Cerbère d'audit d'infrastructure (LangGraph)
    ├── Dockerfile                         # Conteneurisation de l'agent
    └── requirements.txt                   # Dépendances (langchain, crewai, litellm)
```    
---    

🚀 Déploiement & Configuration
Ce système est conçu pour tourner dans un environnement Docker sécurisé, derrière un routeur LLM (LiteLLM).

```Bash
# Routage LLM (LiteLLM Local recommandé)
LITELLM_API_BASE="http://litellm_bunker:4000/v1"
LITELLM_API_KEY="votre_cle_api_securisee"
# Télémétrie
CREWAI_TELEMETRY_OPT_OUT=true
PYTHONUNBUFFERED=1
```
```Bash
cd bunker_agents
docker build -t orioris_agent_veille .
docker run -d \
  -v ./reception:/app/reception \
  -v ./obsidian:/obsidian_vault \
  --env-file .env \
  orioris_agent_veille
 ``` 
📚 Références & Standards de l'Industrie
Ce système a été conçu en s'intégrant aux standards de l'ingénierie IA 2026 :

Intégration Agentique : Inspiré de **[n8n-nodes-langchain(n8n)](https://docs.n8n.io/build/integrate-ai)**.

State Machines : Utilisation de LangGraph pour l'agent d'audit **[LangGraph (LangChain)](https://github.com/langchain-ai/langgraph)** .

Orchestration Multi-Agents : Routage via CrewAI connecté en natif à LiteLLM **[CrewAI(CrewAI)](https://github.com/crewAIInc/crewAI)**.
