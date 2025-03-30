# neural_battler/src/ai/training/batch_training.py
import os
import numpy as np
import argparse
import multiprocessing
import time
import json
from datetime import datetime
from neural_battler.src.ai.training.train import train_immune_cell


def run_batch_training(config):
    """
    Exécute plusieurs sessions d'entraînement avec différents paramètres
    """
    # Créer le dossier des résultats
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = os.path.join("data", "batch_results", f"batch_{timestamp}")
    os.makedirs(results_dir, exist_ok=True)

    # Sauvegarder la configuration
    with open(os.path.join(results_dir, "config.json"), 'w') as f:
        json.dump(config, f, indent=4)

    results = []

    # Exécuter les sessions d'entraînement
    for session_id in range(config["num_sessions"]):
        print(f"\n=== Session d'entraînement {session_id + 1}/{config['num_sessions']} ===")

        # Paramètres de cette session
        session_config = {
            "session_id": session_id,
            "episodes": config["episodes"],
            "batch_size": config["batch_size"],
            "save_interval": config["save_interval"],
            "model_path": config.get("base_model_path", None)
        }

        # Démarrer l'entraînement
        start_time = time.time()
        agent, model_path = train_immune_cell(
            episodes=session_config["episodes"],
            batch_size=session_config["batch_size"],
            save_interval=session_config["save_interval"],
            model_path=session_config["model_path"]
        )
        end_time = time.time()

        # Calculer les métriques
        training_time = end_time - start_time

        # Créer le dossier pour cette session
        session_dir = os.path.join(results_dir, f"session_{session_id}")
        os.makedirs(session_dir, exist_ok=True)

        # Copier le modèle final dans le dossier de la session
        import shutil
        session_model_path = os.path.join(session_dir, "immune_cell_model_final.pt")
        shutil.copy(model_path, session_model_path)

        # Sauvegarder les résultats de la session
        session_results = {
            "session_id": session_id,
            "training_time": training_time,
            "model_path": session_model_path,
            "config": session_config
        }

        results.append(session_results)

        # Sauvegarder les résultats intermédiaires
        with open(os.path.join(results_dir, "results.json"), 'w') as f:
            json.dump(results, f, indent=4)

    print(f"\n=== Entraînement en lot terminé ===")
    print(f"Résultats sauvegardés dans: {results_dir}")
    return results


def run_parallel_training(config, num_processes):
    """
    Exécute des sessions d'entraînement en parallèle
    """
    # Diviser les sessions entre les processus
    sessions_per_process = config["num_sessions"] // num_processes
    remainder = config["num_sessions"] % num_processes

    # Créer des sous-configurations pour chaque processus
    sub_configs = []
    for i in range(num_processes):
        num_sessions = sessions_per_process + (1 if i < remainder else 0)
        if num_sessions > 0:
            sub_config = config.copy()
            sub_config["num_sessions"] = num_sessions
            sub_configs.append(sub_config)

    # Créer et démarrer les processus
    processes = []
    for sub_config in sub_configs:
        p = multiprocessing.Process(target=run_batch_training, args=(sub_config,))
        processes.append(p)
        p.start()

    # Attendre que tous les processus se terminent
    for p in processes:
        p.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entraînement en lot de modèles de lymphocyte")
    parser.add_argument("--sessions", type=int, default=5, help="Nombre de sessions d'entraînement")
    parser.add_argument("--episodes", type=int, default=500, help="Nombre d'épisodes par session")
    parser.add_argument("--batch-size", type=int, default=64, help="Taille du batch pour l'entraînement")
    parser.add_argument("--save-interval", type=int, default=100, help="Intervalle de sauvegarde du modèle")
    parser.add_argument("--base-model", type=str, default=None, help="Modèle de base pour toutes les sessions")
    parser.add_argument("--parallel", type=int, default=1, help="Nombre de processus parallèles")

    args = parser.parse_args()

    config = {
        "num_sessions": args.sessions,
        "episodes": args.episodes,
        "batch_size": args.batch_size,
        "save_interval": args.save_interval,
        "base_model_path": args.base_model
    }

    print("Configuration de l'entraînement en lot:")
    print(f"- Sessions: {args.sessions}")
    print(f"- Épisodes par session: {args.episodes}")
    print(f"- Processus parallèles: {args.parallel}")

    if args.parallel > 1:
        run_parallel_training(config, args.parallel)
    else:
        run_batch_training(config)