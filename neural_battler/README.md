# Neural Battler

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
