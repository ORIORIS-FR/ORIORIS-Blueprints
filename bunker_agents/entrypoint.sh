#!/bin/bash
# Lance le guetteur en arrière-plan
python /app/guetteur_squad.py &

# Lance l'agent en premier plan (pour garder le conteneur vivant)
python /app/agent.py
