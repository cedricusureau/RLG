import os
import sys
import importlib.util
from pathlib import Path
import time

def check_and_document_architecture():
    """
    Vérifie l'architecture du projet, crée un fichier de documentation
    et corrige les problèmes d'import si nécessaire.
    """
    # Trouver le chemin racine du projet (dossier parent du dossier src)
    current_file = Path(__file__).resolve()
    src_dir = current_file.parent
    root_dir = src_dir.parent

    # Ajouter le dossier racine au chemin de recherche Python
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))

    # Ouvrir le fichier d'architecture
    architecture_file = root_dir / "ARCHITECTURE.md"
    with open(architecture_file, 'w', encoding='utf-8') as f:
        f.write("# Architecture du projet Neural Battler\n\n")
        f.write("*Document généré automatiquement le " +

        time.strftime("%d/%m/%Y à %H:%M:%S") + "*\n\n")

        f.write("## Structure des fichiers\n\n```\n")

        # Parcourir récursivement le répertoire du projet
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Ignorer certains dossiers comme __pycache__, .git, etc.
            dirnames[:] = [d for d in dirnames if d not in ['__pycache__', '.git', 'venv', '.venv']]

            # Calculer le niveau d'indentation basé sur la profondeur du répertoire
            rel_path = os.path.relpath(dirpath, root_dir)
            depth = 0 if rel_path == '.' else rel_path.count(os.sep) + 1
            indent = '    ' * depth

            # Écrire le nom du dossier (sauf pour la racine)
            if depth > 0:
                f.write(f"{indent[:-4]}├── {os.path.basename(dirpath)}/\n")

            # Écrire les fichiers dans ce dossier
            for i, filename in enumerate(sorted(filenames)):
                if i == len(filenames) - 1 and len(dirnames) == 0:
                    f.write(f"{indent}└── {filename}\n")
                else:
                    f.write(f"{indent}├── {filename}\n")

        f.write("```\n\n")

    print(f"Architecture documentée dans {architecture_file}")
    return architecture_file