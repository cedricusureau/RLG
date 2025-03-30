# neural_battler/train_headless.py
import argparse
import os
from neural_battler.src.ai.training import train_immune_cell, evaluate_model, run_batch_training
from neural_battler.src.helper.architecture import check_and_document_architecture


def main():
    # Vérifier et documenter l'architecture du projet
    check_and_document_architecture()

    # Créer le parseur d'arguments
    parser = argparse.ArgumentParser(description="Entraînement de lymphocytes sans interface graphique")
    subparsers = parser.add_subparsers(dest="command", help="Commande à exécuter")

    # Parseur pour la commande 'train'
    train_parser = subparsers.add_parser("train", help="Entraîner un modèle")
    train_parser.add_argument("--episodes", type=int, default=1000, help="Nombre d'épisodes d'entraînement")
    train_parser.add_argument("--batch-size", type=int, default=64, help="Taille du batch pour l'entraînement")
    train_parser.add_argument("--save-interval", type=int, default=100, help="Intervalle de sauvegarde du modèle")
    train_parser.add_argument("--model", type=str, default=None, help="Chemin vers un modèle existant à continuer")

    # Parseur pour la commande 'batch'
    batch_parser = subparsers.add_parser("batch", help="Exécuter un entraînement en lot")
    batch_parser.add_argument("--sessions", type=int, default=5, help="Nombre de sessions d'entraînement")
    batch_parser.add_argument("--episodes", type=int, default=500, help="Nombre d'épisodes par session")
    batch_parser.add_argument("--batch-size", type=int, default=64, help="Taille du batch pour l'entraînement")
    batch_parser.add_argument("--save-interval", type=int, default=100, help="Intervalle de sauvegarde du modèle")
    batch_parser.add_argument("--base-model", type=str, default=None, help="Modèle de base pour toutes les sessions")
    batch_parser.add_argument("--parallel", type=int, default=1, help="Nombre de processus parallèles")

    # Parseur pour la commande 'evaluate'
    eval_parser = subparsers.add_parser("evaluate", help="Évaluer un modèle")
    eval_parser.add_argument("--model", type=str, required=True, help="Chemin vers le modèle à évaluer")
    eval_parser.add_argument("--episodes", type=int, default=50, help="Nombre d'épisodes d'évaluation")
    eval_parser.add_argument("--steps", type=int, default=1000, help="Nombre maximum de pas par épisode")

    # Analyser les arguments
    args = parser.parse_args()

    # Exécuter la commande appropriée
    if args.command == "train":
        print("=== Mode entraînement ===")
        print(f"Episodes: {args.episodes}")
        print(f"Batch size: {args.batch_size}")
        print(f"Save interval: {args.save_interval}")
        if args.model:
            print(f"Modèle à poursuivre: {args.model}")

        agent, model_path = train_immune_cell(
            episodes=args.episodes,
            batch_size=args.batch_size,
            save_interval=args.save_interval,
            model_path=args.model
        )

        print(f"Entraînement terminé! Modèle sauvegardé: {model_path}")

    elif args.command == "batch":
        print("=== Mode entraînement en lot ===")
        config = {
            "num_sessions": args.sessions,
            "episodes": args.episodes,
            "batch_size": args.batch_size,
            "save_interval": args.save_interval,
            "base_model_path": args.base_model
        }

        from neural_battler.src.ai.training.batch_training import run_batch_training, run_parallel_training

        if args.parallel > 1:
            print(f"Exécution en parallèle avec {args.parallel} processus")
            run_parallel_training(config, args.parallel)
        else:
            print("Exécution séquentielle")
            run_batch_training(config)

    elif args.command == "evaluate":
        print("=== Mode évaluation ===")
        print(f"Modèle: {args.model}")
        print(f"Episodes: {args.episodes}")
        print(f"Pas max: {args.steps}")

        if not os.path.exists(args.model):
            print(f"Erreur: Le fichier modèle '{args.model}' n'existe pas.")
            return

        results = evaluate_model(args.model, args.episodes, args.steps)

        print("\nRésultats de l'évaluation:")
        print(f"Temps de survie moyen: {results['avg_survival_time']:.2f} secondes")
        print(f"Temps de survie max: {results['max_survival_time']:.2f} secondes")
        print(f"Récompense moyenne: {results['avg_reward']:.2f}")
        print(f"Nombre moyen de pathogènes en fin d'épisode: {results['avg_pathogen_count']:.2f}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()