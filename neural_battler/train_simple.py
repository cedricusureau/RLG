# Créez un fichier train_simple.py dans le répertoire racine
import sys
import os
from pathlib import Path

# Assurez-vous que le répertoire racine est dans le PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Import direct de la fonction d'entraînement
from ai.training.train import train_immune_cell

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Entraînement d'un agent de lymphocyte")
    parser.add_argument("--episodes", type=int, default=250, help="Nombre d'épisodes d'entraînement")
    parser.add_argument("--batch-size", type=int, default=64, help="Taille du batch")
    parser.add_argument("--save-interval", type=int, default=10, help="Intervalle de sauvegarde")
    parser.add_argument("--model", type=str, default=None, help="Chemin vers un modèle existant")

    args = parser.parse_args()

    print("Démarrage de l'entraînement avec paramètres personnalisés...")
    print(f"Episodes: {args.episodes}")
    print(f"Taille du batch: {args.batch_size}")
    print(f"Intervalle de sauvegarde: {args.save_interval}")

    # Changement du répertoire de travail
    os.chdir(root_dir)

    # Lancement de l'entraînement
    train_immune_cell(
        episodes=args.episodes,
        batch_size=args.batch_size,
        save_interval=args.save_interval,
        model_path=args.model
    )