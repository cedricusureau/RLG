#!/usr/bin/env python
import sys
import os
from pathlib import Path

# Configuration des chemins d'importation
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Changer le répertoire de travail à la racine du projet
os.chdir(root_dir)

import argparse
import torch
import numpy as np
import time
from datetime import datetime
import json
import multiprocessing

# Importer directement les fonctions d'entraînement au lieu de les redéfinir
from src.ai.training.train import train_immune_cell
from src.ai.training.evaluate import evaluate_model
from src.ai.training.batch_training import run_batch_training, run_parallel_training

def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description="Neural Battler Training Utility")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Parser for 'train' command
    train_parser = subparsers.add_parser("train", help="Train a model")
    train_parser.add_argument("--episodes", type=int, default=1000, help="Number of training episodes")
    train_parser.add_argument("--batch-size", type=int, default=64, help="Batch size for training")
    train_parser.add_argument("--save-interval", type=int, default=100, help="Interval for saving the model")
    train_parser.add_argument("--model", type=str, default=None, help="Path to an existing model to continue training")

    # Parser for 'batch' command
    batch_parser = subparsers.add_parser("batch", help="Run batch training")
    batch_parser.add_argument("--sessions", type=int, default=2, help="Number of training sessions")
    batch_parser.add_argument("--episodes", type=int, default=500, help="Number of episodes per session")
    batch_parser.add_argument("--batch-size", type=int, default=64, help="Batch size for training")
    batch_parser.add_argument("--save-interval", type=int, default=100, help="Interval for saving the model")
    batch_parser.add_argument("--base-model", type=str, default=None, help="Base model for all sessions")
    batch_parser.add_argument("--parallel", type=int, default=1, help="Number of parallel processes")

    # Parser for 'evaluate' command
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate a model")
    eval_parser.add_argument("--model", type=str, required=True, help="Path to the model to evaluate")
    eval_parser.add_argument("--episodes", type=int, default=50, help="Number of evaluation episodes")
    eval_parser.add_argument("--steps", type=int, default=1000, help="Maximum number of steps per episode")

    # Parse arguments
    args = parser.parse_args()

    # Execute appropriate command
    if args.command == "train":
        print("=== Training Mode ===")
        print(f"Episodes: {args.episodes}")
        print(f"Batch size: {args.batch_size}")
        print(f"Save interval: {args.save_interval}")
        if args.model:
            print(f"Continuing from model: {args.model}")

        agent, model_path = train_immune_cell(
            episodes=args.episodes,
            batch_size=args.batch_size,
            save_interval=args.save_interval,
            model_path=args.model,
        )

        print(f"Training complete! Model saved to: {model_path}")

    elif args.command == "batch":
        print("=== Batch Training Mode ===")
        config = {
            "num_sessions": args.sessions,
            "episodes": args.episodes,
            "batch_size": args.batch_size,
            "save_interval": args.save_interval,
            "base_model_path": args.base_model
        }

        if args.parallel > 1:
            print(f"Running in parallel with {args.parallel} processes")
            run_parallel_training(config, args.parallel)
        else:
            print("Running sequentially")
            run_batch_training(config)

    elif args.command == "evaluate":
        print("=== Evaluation Mode ===")
        print(f"Model: {args.model}")
        print(f"Episodes: {args.episodes}")
        print(f"Max steps: {args.steps}")

        if not os.path.exists(args.model):
            print(f"Error: Model file '{args.model}' does not exist.")
            return

        results = evaluate_model(args.model, args.episodes, args.steps)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()