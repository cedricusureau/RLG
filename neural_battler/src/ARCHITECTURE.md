# Architecture du projet Neural Battler

*Document généré automatiquement le 30/03/2025 à 13:02:45*

## Structure des fichiers

```
├── ARCHITECTURE.md
├── __init__.py
├── main.py
├── main_ai.py
├── ai/
    ├── __init__.py
    ├── inference/
        ├── __init__.py
        └── immune_cell_controller.py
    ├── models/
        ├── __init__.py
        └── immune_cell_model.py
    ├── training/
        ├── __init__.py
        ├── batch_training.py
        ├── environment.py
        ├── evaluate.py
        └── train.py
├── game/
    ├── __init__.py
    ├── entities/
        ├── __init__.py
        ├── ai_immune_cell.py
        ├── immune_cell.py
        └── pathogen.py
    ├── systems/
        └── __init__.py
    ├── world/
        ├── __init__.py
        └── tissue.py
├── helper/
    └── architecture.py
├── rendering/
    └── __init__.py
├── utils/
    └── __init__.py
```

## Analyse des imports

Aucun problème d'import détecté.
