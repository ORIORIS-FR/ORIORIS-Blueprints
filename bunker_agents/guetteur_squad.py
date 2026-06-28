import os
import time
import json
import subprocess
import shutil

# Chemins
DOSSIER_RECEPTION = "/app/reception"
DOSSIER_QUARANTAINE = "/app/reception/erreurs"
FICHIER_HISTORIQUE = "/app/reception/cibles_traitees.txt"

# Initialisation des dossiers et fichiers de contrôle
os.makedirs(DOSSIER_QUARANTAINE, exist_ok=True)
if not os.path.exists(FICHIER_HISTORIQUE):
    open(FICHIER_HISTORIQUE, 'w').close()

print("👁️ Sniper en position : En attente de cibles inédites dans le Sas...")

while True:
    for fichier in os.listdir(DOSSIER_RECEPTION):
        if fichier.startswith("cible_") and fichier.endswith(".json"):
            chemin_fichier = os.path.join(DOSSIER_RECEPTION, fichier)
            cible_id = fichier.replace("cible_", "").replace(".json", "")
            
            # 1. Vérification dans l'historique
            with open(FICHIER_HISTORIQUE, 'r', encoding='utf-8') as f:
                cibles_connues = f.read().splitlines()
                
            if cible_id in cibles_connues:
                print(f"⏩ Déjà traité ({cible_id}). Nettoyage silencieux.")
                os.remove(chemin_fichier)
                continue
                
            # 2. Traitement d'une nouvelle cible
            try:
                with open(chemin_fichier, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                url = data.get("url", "")
                auteur = data.get("auteur", "Inconnu")
                titre = data.get("titre", "Sans titre")
                
                print(f"🎯 Nouvelle cible verrouillée : {titre}")
                
                # Déclenchement de la squad
                subprocess.run(["python", "/app/agent_veille/squad_forum.py", url, auteur, titre])
                
                # Inscription dans l'historique et suppression du JSON
                with open(FICHIER_HISTORIQUE, 'a', encoding='utf-8') as f:
                    f.write(f"{cible_id}\n")
                os.remove(chemin_fichier)
                print(f"🧹 Cible éliminée et archivée : {fichier}")
                
            except json.JSONDecodeError:
                print(f"❌ Fichier corrompu ({fichier}). Envoi en quarantaine.")
                shutil.move(chemin_fichier, os.path.join(DOSSIER_QUARANTAINE, fichier))
            except Exception as e:
                print(f"⚠️ Erreur tactique sur {fichier} : {e}. Envoi en quarantaine.")
                shutil.move(chemin_fichier, os.path.join(DOSSIER_QUARANTAINE, fichier))
                
    # Pause tactique (économie de ressources)
    time.sleep(10)
