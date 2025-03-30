#!/usr/bin/env python
import os
import sys
from pathlib import Path


# Trouver tous les fichiers __init__.py
def fix_imports():
    # Obtenir le chemin racine du projet
    root_dir = Path(__file__).parent

    # Parcourir tous les fichiers .py
    for path in root_dir.glob('**/*.py'):
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Chercher les imports problématiques
        if 'neural_battler.src' in content:
            print(f"Fixing imports in {path}")
            # Remplacer les imports absolus par des imports relatifs
            new_content = content.replace('from ', 'from ')
            new_content = new_content.replace('import ', 'import ')

            # Écrire le contenu modifié
            with open(path, 'w', encoding='utf-8') as file:
                file.write(new_content)


if __name__ == "__main__":
    fix_imports()
    print("Import fixing complete. You may need to adjust some imports manually.")