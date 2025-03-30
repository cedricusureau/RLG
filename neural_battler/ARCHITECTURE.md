# Architecture du projet Neural Battler

*Document généré automatiquement le 30/03/2025 à 19:22:09*

## Structure des fichiers

```
├── .gitignore
├── ARCHITECTURE.md
├── README.md
├── __init__.py
├── requirements.txt
├── run.py
├── train_all.py
├── assets/
    ├── audio/
    ├── fonts/
    ├── sprites/
├── configs/
    └── game_config.json
├── data/
    ├── neural_networks/
        ├── immune_cell_model_ep100.pt
        ├── immune_cell_model_ep200.pt
        ├── immune_cell_model_ep300.pt
        ├── immune_cell_model_ep400.pt
        ├── immune_cell_model_run_20250330_185106_ep100.pt
        ├── immune_cell_model_run_20250330_185106_ep200.pt
        ├── immune_cell_model_run_20250330_185106_ep300.pt
        ├── immune_cell_model_run_20250330_185106_ep400.pt
        ├── immune_cell_model_run_20250330_185106_ep500.pt
        ├── immune_cell_model_run_20250330_185106_final.pt
        ├── immune_cell_model_run_20250330_190000_ep100.pt
        ├── immune_cell_model_run_20250330_190000_ep200.pt
        ├── immune_cell_model_run_20250330_190000_ep300.pt
        ├── immune_cell_model_run_20250330_190000_ep400.pt
        ├── immune_cell_model_run_20250330_190000_ep500.pt
        └── immune_cell_model_run_20250330_190000_final.pt
    ├── stats/
        ├── training_performance.png
        ├── training_performance_run_20250330_185106.png
        └── training_performance_run_20250330_190000.png
├── docs/
├── src/
    ├── __init__.py
    ├── main.py
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
├── tests/
```

## Analyse des imports

### Problèmes d'import potentiels

- Dans `run.py` (ligne 5): `from src.helper.architecture import check_and_document_architecture`
  - Suggestion: `from helper.architecture import check_and_document_architecture`
- Dans `run.py` (ligne 20): `from src.main import main`
  - Suggestion: `from main import main`
- Dans `train_all.py` (ligne 22): `from src.ai.training.train import train_immune_cell`
  - Suggestion: `from ai.training.train import train_immune_cell`
- Dans `train_all.py` (ligne 23): `from src.ai.training.evaluate import evaluate_model`
  - Suggestion: `from ai.training.evaluate import evaluate_model`
- Dans `train_all.py` (ligne 24): `from src.ai.training.batch_training import run_batch_training, run_parallel_training`
  - Suggestion: `from ai.training.batch_training import run_batch_training, run_parallel_training`
- Dans `src\helper\architecture.py` (ligne 71): `                            if "from src." in content:`
  - Suggestion: `                            if "from " in content:`
- Dans `src\helper\architecture.py` (ligne 75): `                                    if "from src." in line:`
  - Suggestion: `                                    if "from " in line:`
- Dans `src\helper\architecture.py` (ligne 77): `                                        fixed_import = line.replace("from src.", "from ")`
  - Suggestion: `                                        fixed_import = line.replace("from ", "from ")`
