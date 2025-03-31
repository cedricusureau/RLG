# neural_battler/run.py
import sys
import os
from pathlib import Path
from src.helper.architecture import check_and_document_architecture

# Ajouter le chemin racine au PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

print(f"Répertoire courant: {os.getcwd()}")
print(f"Répertoire du script: {root_dir}")

# Construire le chemin absolu vers le modèle
model_path = os.path.join(root_dir, "data", "neural_networks", "immune_cell_model_run_20250331_153029_ep180.pt")
print(f"Chemin du modèle à utiliser: {model_path}")
print(f"Le modèle existe: {os.path.exists(model_path)}")

# Maintenant importer main
from src.main import main

if __name__ == "__main__":
    check_and_document_architecture()

    # On ignore complètement les arguments et on utilise directement le chemin absolu
    if os.path.exists(model_path):
        print(f"Lancement avec le modèle: {model_path}")
        main(model_path)
    else:
        print("Modèle introuvable, lancement en mode manuel")
        main()