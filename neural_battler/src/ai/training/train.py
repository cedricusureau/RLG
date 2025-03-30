# neural_battler/src/ai/training/train.py
import os
import torch
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import argparse
from ..models import ImmuneCellAgent
from .environment import TrainingEnvironment  # Import direct depuis le module
from datetime import datetime

def train_immune_cell(episodes=1000, batch_size=64, save_interval=100, model_path=None):
    """
    Entraîne un agent de lymphocyte par reinforcement learning
    """
    # Taille de l'état: position (2) + 5 pathogènes (5*4=20) + santé (1) = 24
    state_size = 24
    # Taille de l'action: 8 directions + immobile = 9
    action_size = 10

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_id = f"run_{timestamp}"

    # Créer l'environnement et l'agent
    env = TrainingEnvironment()
    agent = ImmuneCellAgent(state_size, action_size)

    # Charger un modèle existant si spécifié
    if model_path and os.path.exists(model_path):
        print(f"Chargement du modèle: {model_path}")
        agent.load(model_path)

    # Paramètres d'entraînement
    epsilon = 1.0  # Taux d'exploration initial
    epsilon_min = 0.01  # Taux d'exploration minimal
    epsilon_decay = 0.995  # Taux de décroissance de l'exploration

    # Suivi des performances
    episode_rewards = []
    episode_lengths = []
    losses = []

    # Boucle d'entraînement principale
    for episode in tqdm(range(episodes), desc="Entraînement"):
        state = env.reset()
        total_reward = 0
        episode_loss = []

        # Décroissance du taux d'exploration
        epsilon = max(epsilon_min, epsilon * epsilon_decay)

        done = False
        while not done:
            # Sélectionner une action
            action = agent.select_action(state, epsilon)

            # Exécuter l'action
            next_state, reward, done = env.step(action)

            # Stocker l'expérience
            agent.store_experience(state, action, reward, next_state, done)

            # Entraîner l'agent
            if len(agent.memory) > batch_size:
                loss = agent.train(batch_size)
                if loss is not None:
                    episode_loss.append(loss)

            # Mise à jour pour la prochaine itération
            state = next_state
            total_reward += reward

            if done:
                break

        # Enregistrer les métriques
        episode_rewards.append(total_reward)
        episode_lengths.append(env.current_step)
        if episode_loss:
            losses.append(np.mean(episode_loss))

        # Sauvegarder le modèle périodiquement
        if (episode + 1) % save_interval == 0:
            save_dir = os.path.join("data", "neural_networks")
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, f"immune_cell_model_{run_id}_ep{episode + 1}.pt")
            agent.save(save_path)
            print(f"\nModèle sauvegardé: {save_path}")

            # Afficher les métriques actuelles
            print(f"Épisode {episode + 1}/{episodes}, Récompense moyenne: {np.mean(episode_rewards[-100:]):.2f}")

    # Sauvegarder le modèle final
    final_path = os.path.join("data", "neural_networks", f"immune_cell_model_{run_id}_final.pt")
    agent.save(final_path)
    print(f"Modèle final sauvegardé: {final_path}")

    # Tracer les graphiques de performance
    plt.figure(figsize=(15, 5))

    plt.subplot(1, 3, 1)
    plt.plot(episode_rewards)
    plt.title('Récompenses par épisode')
    plt.xlabel('Épisode')
    plt.ylabel('Récompense totale')

    plt.subplot(1, 3, 2)
    plt.plot(episode_lengths)
    plt.title('Durée des épisodes')
    plt.xlabel('Épisode')
    plt.ylabel('Nombre de pas')

    plt.subplot(1, 3, 3)
    plt.plot(losses)
    plt.title('Perte moyenne par épisode')
    plt.xlabel('Épisode')
    plt.ylabel('Perte')

    # Sauvegarder le graphique
    plt.tight_layout()
    os.makedirs("data/stats", exist_ok=True)
    plt.savefig(f"data/stats/training_performance_{run_id}.png")
    plt.close()

    return agent, final_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entraînement d'un agent de lymphocyte par RL")
    parser.add_argument("--episodes", type=int, default=1000, help="Nombre d'épisodes d'entraînement")
    parser.add_argument("--batch-size", type=int, default=64, help="Taille du batch pour l'entraînement")
    parser.add_argument("--save-interval", type=int, default=100, help="Intervalle de sauvegarde du modèle")
    parser.add_argument("--model", type=str, default=None, help="Chemin vers un modèle existant à poursuivre")

    args = parser.parse_args()

    print("Démarrage de l'entraînement...")
    print(f"Épisodes: {args.episodes}")
    print(f"Taille du batch: {args.batch_size}")
    print(f"Intervalle de sauvegarde: {args.save_interval}")

    agent, model_path = train_immune_cell(
        episodes=args.episodes,
        batch_size=args.batch_size,
        save_interval=args.save_interval,
        model_path=args.model
    )

    print(f"Entraînement terminé! Modèle sauvegardé: {model_path}")