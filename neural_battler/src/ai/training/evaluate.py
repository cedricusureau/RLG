# neural_battler/src/ai/training/evaluate.py
import os
import json
import argparse
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
from .environment import TrainingEnvironment
from ..inference.immune_cell_controller import ImmuneCellController

def evaluate_model(model_path, num_episodes=50, max_steps=30000, render=False):
    """
    Évalue un modèle entraîné sur plusieurs épisodes
    """
    # Créer l'environnement et le contrôleur
    env = TrainingEnvironment(max_steps=max_steps)
    controller = ImmuneCellController(model_path)

    # Suivi des métriques
    episode_rewards = []
    episode_lengths = []
    survival_times = []
    pathogen_counts = []

    # Boucle d'évaluation
    for episode in tqdm(range(num_episodes), desc="Évaluation"):
        state = env.reset()
        total_reward = 0
        pathogen_killed = 0

        done = False
        while not done:
            # Obtenir l'action du contrôleur
            action = controller.get_action(
                env.immune_cell,
                env.tissue.pathogens,
                env.width,
                env.height
            )

            # Exécuter l'action
            next_state, reward, done = env.step(action)

            # Mise à jour pour la prochaine itération
            state = next_state
            total_reward += reward

            # Compter les pathogènes tués
            current_pathogen_count = len(env.tissue.pathogens)

            # Afficher l'état actuel si demandé
            if render:
                env.render()

            if done:
                break

        # Enregistrer les métriques
        episode_rewards.append(total_reward)
        episode_lengths.append(env.current_step)
        survival_times.append(env.current_step / 60)  # Conversion en secondes (à 60 FPS)
        pathogen_counts.append(len(env.tissue.pathogens))

    # Calculer les statistiques
    results = {
        "model_path": model_path,
        "num_episodes": num_episodes,
        "avg_reward": float(np.mean(episode_rewards)),
        "std_reward": float(np.std(episode_rewards)),
        "avg_survival_time": float(np.mean(survival_times)),
        "std_survival_time": float(np.std(survival_times)),
        "avg_episode_length": float(np.mean(episode_lengths)),
        "std_episode_length": float(np.std(episode_lengths)),
        "avg_pathogen_count": float(np.mean(pathogen_counts)),
        "std_pathogen_count": float(np.std(pathogen_counts)),
        "max_survival_time": float(np.max(survival_times)),
        "min_survival_time": float(np.min(survival_times)),
    }

    return results


def evaluate_multiple_models(model_paths, num_episodes=30, max_steps=1000):
    """
    Évalue plusieurs modèles et compare leurs performances
    """
    all_results = {}

    for model_path in model_paths:
        print(f"\nÉvaluation du modèle: {model_path}")
        model_name = os.path.basename(model_path)
        results = evaluate_model(model_path, num_episodes, max_steps)
        all_results[model_name] = results

    # Sauvegarder les résultats
    os.makedirs("data/evaluations", exist_ok=True)
    timestamp = os.path.basename(os.path.dirname(model_paths[0])) if len(model_paths) > 0 else "custom"
    results_path = os.path.join("data/evaluations", f"eval_{timestamp}.json")

    with open(results_path, 'w') as f:
        json.dump(all_results, f, indent=4)

    print(f"\nRésultats d'évaluation sauvegardés dans: {results_path}")

    # Créer des graphiques comparatifs
    create_comparison_plots(all_results, timestamp)

    return all_results


def create_comparison_plots(results, timestamp):
    """
    Crée des graphiques comparatifs pour les modèles évalués
    """
    model_names = list(results.keys())
    metrics = [
        ("avg_survival_time", "Temps de survie moyen (s)"),
        ("avg_reward", "Récompense moyenne"),
        ("avg_pathogen_count", "Nombre moyen de pathogènes en fin d'épisode")
    ]

    # Créer un graphique pour chaque métrique
    for metric_key, metric_label in metrics:
        plt.figure(figsize=(10, 6))

        # Extraire les valeurs et écarts-types
        values = [results[model][metric_key] for model in model_names]
        stds = [results[model][f"std_{metric_key.split('_')[1]}"] for model in model_names]

        # Créer le graphique à barres avec barres d'erreur
        bars = plt.bar(model_names, values, yerr=stds, capsize=5)

        # Ajouter les labels et titres
        plt.title(f"Comparaison de modèles - {metric_label}")
        plt.xlabel("Modèle")
        plt.ylabel(metric_label)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        # Ajouter les valeurs au-dessus des barres
        for bar, value in zip(bars, values):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                f"{value:.2f}",
                ha='center', va='bottom'
            )

        # Sauvegarder le graphique
        os.makedirs("data/evaluations/plots", exist_ok=True)
        plot_path = os.path.join("data/evaluations/plots", f"{metric_key}_{timestamp}.png")
        plt.savefig(plot_path)
        plt.close()

        print(f"Graphique sauvegardé: {plot_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Évaluation de modèles de lymphocyte")
    parser.add_argument("--models", nargs='+', help="Chemins vers les modèles à évaluer")
    parser.add_argument("--dir", type=str, help="Dossier contenant les modèles à évaluer", default="data/neural_networks")
    parser.add_argument("--episodes", type=int, default=30, help="Nombre d'épisodes d'évaluation")
    parser.add_argument("--steps", type=int, default=1000, help="Nombre maximum de pas par épisode")
    parser.add_argument("--render", action="store_true", help="Afficher le rendu de l'évaluation")

    args = parser.parse_args()

    # Collecter les chemins des modèles
    model_paths = []

    if args.models:
        model_paths.extend(args.models)

    if args.dir and os.path.isdir(args.dir):
        for filename in os.listdir(args.dir):
            if filename.endswith(".pt"):
                model_paths.append(os.path.join(args.dir, filename))

    if not model_paths:
        print("Erreur: Aucun modèle spécifié!")
        parser.print_help()
        exit(1)

    print(f"Évaluation de {len(model_paths)} modèles...")

    if len(model_paths) == 1 and args.render:
        # Évaluation détaillée d'un seul modèle avec rendu
        results = evaluate_model(model_paths[0], args.episodes, args.steps, args.render)
        print("\nRésultats:")
        for key, value in results.items():
            if isinstance(value, float):
                print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")
    else:
        # Évaluation comparative de plusieurs modèles
        evaluate_multiple_models(model_paths, args.episodes, args.steps)