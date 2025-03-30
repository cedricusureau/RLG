import os
import sys
from pathlib import Path


def create_directory(path):
    try:
        os.makedirs(path, exist_ok=True)
        print(f"Dossier créé: {path}")
    except Exception as e:
        print(f"Erreur lors de la création du dossier {path}: {e}")


def create_file(path, content=""):
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fichier créé: {path}")
    except Exception as e:
        print(f"Erreur lors de la création du fichier {path}: {e}")


def create_project_structure():
    # Nom du projet
    project_name = "neural_battler"

    # Création du dossier principal
    base_dir = Path(project_name)
    create_directory(base_dir)

    # Création des sous-dossiers principaux
    subdirs = [
        "src",  # Code source principal
        "src/game",  # Logique du jeu
        "src/game/entities",  # Classes des entités (personnages, objets)
        "src/game/systems",  # Systèmes (combat, mouvement, etc.)
        "src/game/world",  # Génération et gestion du monde
        "src/rendering",  # Rendu graphique (Pygame)
        "src/ai",  # Intelligence artificielle
        "src/ai/models",  # Modèles de réseaux neuronaux
        "src/ai/training",  # Scripts d'entraînement
        "src/ai/inference",  # Scripts d'inférence pour utiliser les modèles entraînés
        "src/utils",  # Utilitaires et fonctions helpers
        "assets",  # Ressources graphiques et sonores
        "assets/sprites",  # Images pour les personnages et objets
        "assets/audio",  # Sons et musiques
        "assets/fonts",  # Polices d'écriture
        "configs",  # Fichiers de configuration
        "data",  # Données de jeu (statistiques, paramètres)
        "data/neural_networks",  # Réseaux de neurones sauvegardés
        "tests",  # Tests unitaires et d'intégration
        "docs",  # Documentation
    ]

    for subdir in subdirs:
        create_directory(base_dir / subdir)

    # Création des fichiers de base
    files = [
        ("src/__init__.py", ""),
        ("src/game/__init__.py", ""),
        ("src/game/entities/__init__.py", ""),
        ("src/game/systems/__init__.py", ""),
        ("src/game/world/__init__.py", ""),
        ("src/rendering/__init__.py", ""),
        ("src/ai/__init__.py", ""),
        ("src/ai/models/__init__.py", ""),
        ("src/ai/training/__init__.py", ""),
        ("src/ai/inference/__init__.py", ""),
        ("src/utils/__init__.py", ""),
        (".gitignore",
         "__pycache__/\n*.py[cod]\n*$py.class\n*.so\n.Python\nenv/\nbuild/\ndevelop-eggs/\ndist/\ndownloads/\neggs/\n.eggs/\nlib/\nlib64/\nparts/\nsdist/\nvar/\nwheels/\n*.egg-info/\n.installed.cfg\n*.egg\n.env\n.venv\nvenv/\nENV/\n.idea/\n.vscode/\n*.swp\n*.swo\n"),
    ]

    for file_path, content in files:
        create_file(base_dir / file_path, content)

    # Création du README.md avec description du projet
    readme_content = create_readme_content()
    create_file(base_dir / "README.md", readme_content)

    print(f"\nStructure du projet '{project_name}' créée avec succès!")
    print(f"Pour commencer, naviguez vers le dossier: cd {project_name}")
    print("Installez les dépendances: pip install -r requirements.txt")
    print("Lancez le jeu: python src/main.py")


def create_readme_content():
    return """# Neural Battler

Un jeu qui combine des éléments de Vampire Survivor et d'auto-battler (type TFT), où chaque personnage est contrôlé par son propre réseau de neurones.

## Concept du jeu

Dans Neural Battler, les joueurs assemblent une équipe de personnages, chacun équipé d'un réseau neuronal spécifique qui dicte son comportement. Par exemple, un tank pourrait avoir un RNN orienté protection des alliés, tandis qu'un DPS pourrait avoir un réseau optimisé pour maximiser les dégâts.

### Caractéristiques principales

- **Gameplay en temps réel** inspiré de Vampire Survivor
- **Système de composition d'équipe** similaire aux auto-battlers
- **Réseaux de neurones personnalisables** pour chaque personnage
- **Mode entraînement** pour développer des RNN spécialisés via Reinforcement Learning (RL)
- **Partage communautaire** des réseaux neuronaux entraînés

## Architecture du projet

```
neural_battler/
├── src/                    # Code source
│   ├── game/               # Logique du jeu
│   │   ├── entities/       # Personnages, objets, etc.
│   │   ├── systems/        # Combat, mouvement, etc.
│   │   └── world/          # Génération et gestion du monde
│   ├── rendering/          # Rendu graphique (Pygame)
│   ├── ai/                 # Intelligence artificielle
│   │   ├── models/         # Modèles de réseaux neuronaux
│   │   ├── training/       # Scripts d'entraînement
│   │   └── inference/      # Utilisation des modèles entraînés
│   └── utils/              # Utilitaires
├── assets/                 # Ressources graphiques et sonores
├── configs/                # Fichiers de configuration
├── data/                   # Données de jeu et réseaux sauvegardés
│   └── neural_networks/    # Réseaux pré-entraînés
├── tests/                  # Tests unitaires et d'intégration
└── docs/                   # Documentation
```

## Plan de développement

### Phase 1 : Prototype et environnement d'entraînement
- Créer un jeu simplifié fonctionnel (déplacements, règles de base)
- Développer un mode simulation sans interface graphique pour l'entraînement
- Implémenter les fonctions de récompense pour le Reinforcement Learning
- Entraîner des réseaux sur des objectifs simples (survie, protection, attaque)

### Phase 2 : Compétition et partage
- Interface pour charger des modèles RNN entraînés
- Mode compétitif pour confronter différents modèles
- Système de partage communautaire des réseaux

## Installation

1. Cloner le dépôt
2. Installer les dépendances: `pip install -r requirements.txt`
3. Lancer le jeu: `python src/main.py`

## Technologies utilisées

- **Pygame** : Moteur de rendu et boucle de jeu
- **PyTorch** : Framework pour les réseaux de neurones
- **Numpy/Pandas** : Traitement de données et analyse

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une Issue ou proposer une Pull Request pour améliorer le projet.
"""


if __name__ == "__main__":
    create_project_structure()