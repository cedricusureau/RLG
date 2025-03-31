# neural_battler/src/ai/models/immune_cell_model.py
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


class ImmuneCellNetwork(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(ImmuneCellNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)  # Actions: directions de mouvement


class ImmuneCellAgent:
    def __init__(self, state_size, action_size=10, hidden_size=64, learning_rate=0.001):
        """
        Initialiser avec 10 actions:
        0-7: 8 directions de mouvement
        8: ne pas bouger
        9: utiliser capacité spéciale (sans bouger)
        """

        self.state_size = state_size
        self.action_size = action_size

        # Réseau de neurones principal
        self.policy_network = ImmuneCellNetwork(state_size, hidden_size, action_size)

        # Optimiseur
        self.optimizer = torch.optim.Adam(self.policy_network.parameters(), lr=learning_rate)

        # Mémoire pour stocker les expériences
        self.memory = []
        self.gamma = 0.99  # Facteur de remise pour les récompenses futures

    def get_state(self, immune_cell, pathogens, tissue_width, tissue_height):
        """
        Convertit l'état du jeu en entrée pour le réseau de neurones
        """
        # Position normalisée du lymphocyte (entre 0 et 1)
        cell_pos = [immune_cell.x / tissue_width, immune_cell.y / tissue_height]

        # Informations sur les pathogènes proches (au maximum 5 les plus proches)
        pathogen_info = []

        if pathogens:
            # Calculer distances à tous les pathogènes
            distances = []
            for pathogen in pathogens:
                dx = pathogen.x - immune_cell.x
                dy = pathogen.y - immune_cell.y
                distance = np.sqrt(dx ** 2 + dy ** 2)
                distances.append((distance, dx / tissue_width, dy / tissue_height,
                                  pathogen.health / pathogen.max_health))

            # Trier par distance
            distances.sort(key=lambda x: x[0])

            # Prendre les 5 plus proches (ou moins s'il y en a moins)
            for i in range(min(5, len(distances))):
                dist, dx, dy, health_ratio = distances[i]
                # Normaliser la distance
                norm_dist = dist / np.sqrt(tissue_width ** 2 + tissue_height ** 2)
                pathogen_info.extend([norm_dist, dx, dy, health_ratio])

            # Remplir avec des zéros si moins de 5 pathogènes
            padding = 5 - min(5, len(distances))
            pathogen_info.extend([0.0] * (padding * 4))
        else:
            # Aucun pathogène, remplir avec des zéros
            pathogen_info = [0.0] * 20  # 5 pathogènes * 4 informations

        # Position normalisée du lymphocyte (entre 0 et 1)
        cell_pos = [immune_cell.x / tissue_width, immune_cell.y / tissue_height]

        # NOUVEAU: Informations sur la distance aux murs (normalisation entre 0 et 1)
        # Plus la valeur est proche de 0, plus le mur est proche
        wall_distances = [
            immune_cell.x / tissue_width,  # Distance au mur gauche (normalisée)
            (tissue_width - immune_cell.x) / tissue_width,  # Distance au mur droit (normalisée)
            immune_cell.y / tissue_height,  # Distance au mur haut (normalisée)
            (tissue_height - immune_cell.y) / tissue_height  # Distance au mur bas (normalisée)
        ]

        # Informations sur les pathogènes proches (au maximum 5 les plus proches)
        pathogen_info = []

        # Santé relative du lymphocyte et état de la capacité spéciale
        health_info = [immune_cell.health / immune_cell.max_health]
        special_ready = [1.0 if immune_cell.special_ready else 0.0]

        # Combinaison de toutes les informations
        state = cell_pos + wall_distances + pathogen_info + health_info + special_ready
        return torch.FloatTensor(state)

    def select_action(self, state, epsilon=0.1):
        """
        Sélectionne une action selon la politique epsilon-greedy
        """
        if np.random.random() < epsilon:
            # Exploration: action aléatoire
            return torch.randint(0, self.action_size, (1,)).item()
        else:
            # Exploitation: meilleure action selon le réseau
            with torch.no_grad():
                q_values = self.policy_network(state)
                return torch.argmax(q_values).item()

    def action_to_movement(self, action, speed=1.0):
        """
        Convertit l'action (indice) en mouvement (dx, dy)
        Actions: 0=haut, 1=droite, 2=bas, 3=gauche, 4=haut-droite, 5=bas-droite,
                 6=bas-gauche, 7=haut-gauche, 8=immobile
        """
        movements = [
            (0, -1),  # haut
            (1, 0),  # droite
            (0, 1),  # bas
            (-1, 0),  # gauche
            (0.7, -0.7),  # haut-droite
            (0.7, 0.7),  # bas-droite
            (-0.7, 0.7),  # bas-gauche
            (-0.7, -0.7),  # haut-gauche
            (0, 0),
            (0,0 )
        ]

        dx, dy = movements[action]
        return dx * speed, dy * speed

    def store_experience(self, state, action, reward, next_state, done):
        """
        Stocke une expérience dans la mémoire
        """
        self.memory.append((state, action, reward, next_state, done))

        # Limiter la taille de la mémoire
        if len(self.memory) > 10000:
            self.memory.pop(0)

    def train(self, batch_size=64):
        """
        Entraîne le réseau sur un mini-batch d'expériences
        """
        if len(self.memory) < batch_size:
            return

        # Échantillonner un mini-batch
        batch = np.random.choice(len(self.memory), batch_size, replace=False)
        states, actions, rewards, next_states, dones = zip(*[self.memory[i] for i in batch])

        # Convertir en tenseurs
        states = torch.stack(states)
        actions = torch.LongTensor(actions).unsqueeze(1)
        rewards = torch.FloatTensor(rewards).unsqueeze(1)
        next_states = torch.stack(next_states)
        dones = torch.FloatTensor(dones).unsqueeze(1)

        # Calculer les valeurs Q courantes
        current_q_values = self.policy_network(states).gather(1, actions)

        # Calculer les valeurs Q cibles (sans gradient)
        with torch.no_grad():
            next_q_values = self.policy_network(next_states).max(1)[0].unsqueeze(1)

        # Calculer les valeurs Q cibles avec l'équation de Bellman
        target_q_values = rewards + self.gamma * next_q_values * (1 - dones)

        # Calculer la perte
        loss = F.smooth_l1_loss(current_q_values, target_q_values)

        # Mettre à jour le réseau
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return loss.item()

    def save(self, path):
        """
        Sauvegarde le modèle
        """
        torch.save({
            'policy_network': self.policy_network.state_dict(),
            'optimizer': self.optimizer.state_dict(),
        }, path)

    def load(self, path):
        """
        Charge le modèle
        """
        checkpoint = torch.load(path)
        self.policy_network.load_state_dict(checkpoint['policy_network'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])