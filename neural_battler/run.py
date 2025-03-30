# neural_battler/run.py
import sys
from pathlib import Path

# Ajouter le chemin racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

# Maintenant importer main
from src.main import main

if __name__ == "__main__":
    import sys
    # Passez les arguments de ligne de commande à la fonction main
    if len(sys.argv) > 1:
        import argparse
        parser = argparse.ArgumentParser(description="Neural Battler")
        parser.add_argument("--model", type=str, default=None,
                          help="Chemin vers le modèle d'IA à utiliser (facultatif)")
        args = parser.parse_args()
        main(args.model)
    else:
        main()