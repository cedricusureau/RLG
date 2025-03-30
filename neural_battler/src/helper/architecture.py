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
    # Trouver le chemin racine du projet
    current_file = Path(__file__).resolve()
    root_dir = current_file.parent
    while not (root_dir / "README.md").exists() and root_dir != root_dir.parent:
        root_dir = root_dir.parent

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
            # Ignorer certains dossiers
            dirnames[:] = [d for d in dirnames if d not in ['__pycache__', '.git', 'venv', '.venv']]

            # Calculer le niveau d'indentation
            rel_path = os.path.relpath(dirpath, root_dir)
            depth = 0 if rel_path == '.' else rel_path.count(os.sep) + 1
            indent = '    ' * depth

            # Écrire le nom du dossier (sauf pour la racine)
            if depth > 0:
                f.write(f"{indent[:-4]}├── {os.path.basename(dirpath)}/\n")

            # Trier les fichiers
            sorted_files = sorted(filenames)

            # Écrire les fichiers dans ce dossier
            for i, filename in enumerate(sorted_files):
                is_last_file = (i == len(sorted_files) - 1)
                prefix = "└── " if is_last_file and len(dirnames) == 0 else "├── "
                f.write(f"{indent}{prefix}{filename}\n")

        f.write("```\n\n")

        # Analyser les problèmes d'import potentiels
        f.write("## Analyse des imports\n\n")
        f.write("### Problèmes d'import potentiels\n\n")

        # Parcourir tous les fichiers Python
        import_issues = []
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.endswith(".py"):
                    file_path = os.path.join(dirpath, filename)
                    with open(file_path, 'r', encoding='utf-8') as py_file:
                        try:
                            content = py_file.read()
                            # Chercher les imports problématiques
                            if "from src." in content:
                                rel_file_path = os.path.relpath(file_path, root_dir)
                                line_number = 1
                                for line_no, line in enumerate(content.split('\n'), 1):
                                    if "from src." in line:
                                        line_number = line_no
                                        fixed_import = line.replace("from src.", "from ")
                                        import_issues.append((rel_file_path, line_number, line, fixed_import))
                        except UnicodeDecodeError:
                            # Ignorer les fichiers qui ne sont pas en texte
                            pass

        if import_issues:
            for file_path, line_number, original_line, fixed_import in import_issues:
                f.write(f"- Dans `{file_path}` (ligne {line_number}): `{original_line}`\n")
                f.write(f"  - Suggestion: `{fixed_import}`\n")
        else:
            f.write("- Aucun problème d'import détecté\n")

    print(f"Architecture documentée dans {architecture_file}")
    return architecture_file