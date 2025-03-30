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


# Importations directes des modules au lieu d'utiliser des imports relatifs
def import_training():
    """Import all training-related functions directly"""
    from src.ai.models.immune_cell_model import ImmuneCellAgent
    from src.ai.training.environment import TrainingEnvironment

    # Function to train an immune cell
    def train_immune_cell(episodes=1000, batch_size=64, save_interval=100, model_path=None):
        print("Starting training...")

        # State size: position (2) + 5 pathogens (5*4=20) + health (1) = 23
        state_size = 23
        # Action size: 8 directions + stationary = 9
        action_size = 9

        # Create environment and agent
        env = TrainingEnvironment()
        agent = ImmuneCellAgent(state_size, action_size)

        # Load existing model if specified
        if model_path and os.path.exists(model_path):
            print(f"Loading model: {model_path}")
            agent.load(model_path)

        # Training parameters
        epsilon = 1.0  # Initial exploration rate
        epsilon_min = 0.01  # Minimum exploration rate
        epsilon_decay = 0.995  # Exploration rate decay

        # Performance tracking
        episode_rewards = []
        episode_lengths = []
        losses = []

        # Main training loop
        for episode in range(episodes):
            if episode % 10 == 0:
                print(f"Episode {episode}/{episodes}")

            state = env.reset()
            total_reward = 0
            episode_loss = []

            # Decay exploration rate
            epsilon = max(epsilon_min, epsilon * epsilon_decay)

            done = False
            while not done:
                # Select action
                action = agent.select_action(state, epsilon)

                # Execute action
                next_state, reward, done = env.step(action)

                # Store experience
                agent.store_experience(state, action, reward, next_state, done)

                # Train agent
                if len(agent.memory) > batch_size:
                    loss = agent.train(batch_size)
                    if loss is not None:
                        episode_loss.append(loss)

                # Update for next iteration
                state = next_state
                total_reward += reward

                if done:
                    break

            # Record metrics
            episode_rewards.append(total_reward)
            episode_lengths.append(env.current_step)
            if episode_loss:
                losses.append(np.mean(episode_loss))

            # Save model periodically
            if (episode + 1) % save_interval == 0:
                save_dir = os.path.join("data", "neural_networks")
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, f"immune_cell_model_ep{episode + 1}.pt")
                agent.save(save_path)
                print(f"\nModel saved: {save_path}")

                # Display current metrics
                print(f"Episode {episode + 1}/{episodes}, Average reward: {np.mean(episode_rewards[-100:]):.2f}")

        # Save final model
        final_path = os.path.join("data", "neural_networks", "immune_cell_model_final.pt")
        agent.save(final_path)
        print(f"Final model saved: {final_path}")

        try:
            import matplotlib.pyplot as plt
            # Plot performance graphs
            plt.figure(figsize=(15, 5))

            plt.subplot(1, 3, 1)
            plt.plot(episode_rewards)
            plt.title('Rewards per Episode')
            plt.xlabel('Episode')
            plt.ylabel('Total Reward')

            plt.subplot(1, 3, 2)
            plt.plot(episode_lengths)
            plt.title('Episode Duration')
            plt.xlabel('Episode')
            plt.ylabel('Number of Steps')

            plt.subplot(1, 3, 3)
            plt.plot(losses)
            plt.title('Average Loss per Episode')
            plt.xlabel('Episode')
            plt.ylabel('Loss')

            # Save the graph
            plt.tight_layout()
            os.makedirs("data/stats", exist_ok=True)
            plt.savefig("data/stats/training_performance.png")
            plt.close()
        except:
            print("Could not create performance plots (matplotlib may be missing)")

        return agent, final_path

    # Function to evaluate a model
    def evaluate_model(model_path, num_episodes=50, max_steps=1000, render=False):
        from src.ai.inference.immune_cell_controller import ImmuneCellController

        print(f"Evaluating model: {model_path}")
        # Create environment and controller
        env = TrainingEnvironment(max_steps=max_steps)
        controller = ImmuneCellController(model_path)

        # Tracking metrics
        episode_rewards = []
        episode_lengths = []
        survival_times = []
        pathogen_counts = []

        # Evaluation loop
        for episode in range(num_episodes):
            if episode % 10 == 0:
                print(f"Evaluation episode {episode}/{num_episodes}")

            state = env.reset()
            total_reward = 0

            done = False
            while not done:
                # Get action from controller
                action = controller.get_action(
                    env.immune_cell,
                    env.tissue.pathogens,
                    env.width,
                    env.height
                )

                # Execute action
                next_state, reward, done = env.step(action)

                # Update for next iteration
                state = next_state
                total_reward += reward

                # Display current state if requested
                if render:
                    env.render()

                if done:
                    break

            # Record metrics
            episode_rewards.append(total_reward)
            episode_lengths.append(env.current_step)
            survival_times.append(env.current_step / 60)  # Convert to seconds (at 60 FPS)
            pathogen_counts.append(len(env.tissue.pathogens))

        # Calculate statistics
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

        # Print results
        print("\nEvaluation Results:")
        print(f"Average survival time: {results['avg_survival_time']:.2f} seconds")
        print(f"Max survival time: {results['max_survival_time']:.2f} seconds")
        print(f"Average reward: {results['avg_reward']:.2f}")
        print(f"Average pathogen count at end: {results['avg_pathogen_count']:.2f}")

        return results

    # Function to run batch training
    def run_batch_training(config):
        """Run multiple training sessions with different parameters"""
        # Create results directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = os.path.join("data", "batch_results", f"batch_{timestamp}")
        os.makedirs(results_dir, exist_ok=True)

        # Save configuration
        with open(os.path.join(results_dir, "config.json"), 'w') as f:
            json.dump(config, f, indent=4)

        results = []

        # Run training sessions
        for session_id in range(config["num_sessions"]):
            print(f"\n=== Training Session {session_id + 1}/{config['num_sessions']} ===")

            # Session parameters
            session_config = {
                "session_id": session_id,
                "episodes": config["episodes"],
                "batch_size": config["batch_size"],
                "save_interval": config["save_interval"],
                "model_path": config.get("base_model_path", None)
            }

            # Start training
            start_time = time.time()
            agent, model_path = train_immune_cell(
                episodes=session_config["episodes"],
                batch_size=session_config["batch_size"],
                save_interval=session_config["save_interval"],
                model_path=session_config["model_path"]
            )
            end_time = time.time()

            # Calculate metrics
            training_time = end_time - start_time

            # Create directory for this session
            session_dir = os.path.join(results_dir, f"session_{session_id}")
            os.makedirs(session_dir, exist_ok=True)

            # Copy final model to session directory
            import shutil
            session_model_path = os.path.join(session_dir, "immune_cell_model_final.pt")
            shutil.copy(model_path, session_model_path)

            # Save session results
            session_results = {
                "session_id": session_id,
                "training_time": training_time,
                "model_path": session_model_path,
                "config": session_config
            }

            results.append(session_results)

            # Save intermediate results
            with open(os.path.join(results_dir, "results.json"), 'w') as f:
                json.dump(results, f, indent=4)

        print(f"\n=== Batch training completed ===")
        print(f"Results saved to: {results_dir}")
        return results

    # Function to run parallel training
    def run_parallel_training(config, num_processes):
        """Run training sessions in parallel"""
        # Divide sessions among processes
        sessions_per_process = config["num_sessions"] // num_processes
        remainder = config["num_sessions"] % num_processes

        # Create sub-configurations for each process
        sub_configs = []
        for i in range(num_processes):
            num_sessions = sessions_per_process + (1 if i < remainder else 0)
            if num_sessions > 0:
                sub_config = config.copy()
                sub_config["num_sessions"] = num_sessions
                sub_configs.append(sub_config)

        # Create and start processes
        processes = []
        for sub_config in sub_configs:
            p = multiprocessing.Process(target=run_batch_training, args=(sub_config,))
            processes.append(p)
            p.start()

        # Wait for all processes to finish
        for p in processes:
            p.join()

    return train_immune_cell, evaluate_model, run_batch_training, run_parallel_training


# Import training functions
train_immune_cell, evaluate_model, run_batch_training, run_parallel_training = import_training()


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
            model_path=args.model
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