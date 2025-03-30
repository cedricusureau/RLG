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

        # Documenter les problèmes d'import potentiels
        f.write("## Analyse des imports\n\n")
        python_files = []
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.endswith('.py'):
                    python_files.append(os.path.join(dirpath, filename))

        import_issues = []
        for py_file in python_files:
            with open(py_file, 'r', encoding='utf-8') as file:
                try:
                    content = file.read()
                    rel_path = os.path.relpath(py_file, root_dir)
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.strip().startswith('from src.') or line.strip().startswith('import src.'):
                            import_issues.append((rel_path, i + 1, line.strip()))
                except:
                    pass

        if import_issues:
            f.write("### Problèmes d'import potentiels\n\n")
            for file, line, import_stmt in import_issues:
                f.write(f"- Dans `{file}` (ligne {line}): `{import_stmt}`\n")
                # Suggestion de correction
                corrected = import_stmt.replace('src.', '')
                f.write(f"  - Suggestion: `{corrected}`\n")
        else:
            f.write("Aucun problème d'import détecté.\n")

    print(f"Architecture documentée dans {architecture_file}")
    return architecture_file