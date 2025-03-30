# neural_battler/src/ai/training/environment.py
import numpy as np
import random
from ...game.world.tissue import Tissue
from ...game.entities.immune_cell import ImmuneCell
from ...game.entities.pathogen import Pathogen
from ..models import ImmuneCellAgent  # Import simplifié


class TrainingEnvironment:
    def __init__(self, width=800, height=600, max_steps=1000):
        self.width = width
        self.height = height
        self.max_steps = max_steps
        self.current_step = 0
        self.tissue = None
        self.immune_cell = None
        self.default_speed = 1.0

        # Créer une seule instance de l'agent qui sera réutilisée
        self.helper_agent = ImmuneCellAgent(23, 9)

        self.reset()

    def reset(self):
        """
        Réinitialise l'environnement pour un nouvel épisode
        """
        self.current_step = 0
        self.tissue = Tissue(self.width, self.height)

        # Placer le lymphocyte au centre
        self.immune_cell = self.tissue.add_immune_cell(self.width / 2, self.height / 2, "t_cell")

        # Ajouter quelques pathogènes aléatoirement
        for _ in range(5):
            x = random.uniform(50, self.width - 50)
            y = random.uniform(50, self.height - 50)
            self.tissue.add_pathogen(x, y, "bacteria")

        # État initial
        state = self._get_state()
        return state

    def _get_state(self):
        """
        Récupère l'état actuel pour l'agent
        """
        # Utiliser l'instance réutilisable au lieu d'en créer une nouvelle
        return self.helper_agent.get_state(self.immune_cell, self.tissue.pathogens, self.width, self.height)

    def step(self, action):
        """
        Effectue une action et retourne le nouvel état, la récompense, et si l'épisode est terminé
        """
        # Utiliser l'instance réutilisable
        dx, dy = self.helper_agent.action_to_movement(action, self.default_speed)

        # Sauvegarder l'état précédent
        prev_health = self.immune_cell.health
        prev_num_pathogens = len(self.tissue.pathogens)

        # Appliquer le mouvement
        new_x = self.immune_cell.x + dx
        new_y = self.immune_cell.y + dy

        # Vérifier que la nouvelle position est valide
        if self.tissue.is_valid_position(new_x, new_y):
            self.immune_cell.x = new_x
            self.immune_cell.y = new_y

        # Mettre à jour l'environnement
        self.tissue.update()
        self.current_step += 1

        # Après avoir mis à jour l'environnement avec tissue.update()
        self.tissue.update()
        self.current_step += 1

        # Ajouter cette nouvelle logique de spawn près des murs
        if self._is_near_wall() and random.random() < 0.1:  # 10% de chance par pas de temps
            # Spawn un pathogène près du mur le plus proche
            wall_spawn_pos = self._get_nearest_wall_position()
            self.tissue.add_pathogen(wall_spawn_pos[0], wall_spawn_pos[1], "bacteria")

        # Calculer la récompense
        reward = self._calculate_reward(prev_health, prev_num_pathogens)

        # Vérifier si l'épisode est terminé
        done = self.immune_cell.is_dead() or self.current_step >= self.max_steps

        # Si tous les pathogènes sont éliminés, ajouter un bonus et en générer de nouveaux
        if len(self.tissue.pathogens) == 0:
            reward += 10.0  # Bonus pour avoir éliminé tous les pathogènes
            for _ in range(random.randint(3, 7)):
                x = random.uniform(50, self.width - 50)
                y = random.uniform(50, self.height - 50)
                self.tissue.add_pathogen(x, y, "bacteria")

        # Obtenir le nouvel état
        next_state = self._get_state()

        return next_state, reward, done

    def _is_near_wall(self):
        """Vérifie si le lymphocyte est proche d'un mur"""
        margin = 50  # Distance considérée comme "proche"
        return (self.immune_cell.x < margin or
                self.immune_cell.x > self.width - margin or
                self.immune_cell.y < margin or
                self.immune_cell.y > self.height - margin)

    def _get_nearest_wall_position(self):
        """Détermine les coordonnées pour spawner un pathogène près du mur le plus proche"""
        # Calculer les distances aux murs
        dist_left = self.immune_cell.x
        dist_right = self.width - self.immune_cell.x
        dist_top = self.immune_cell.y
        dist_bottom = self.height - self.immune_cell.y

        # Trouver le mur le plus proche
        min_dist = min(dist_left, dist_right, dist_top, dist_bottom)

        # Ajouter un peu de variation aléatoire
        variation = 30

        # Générer la position en fonction du mur le plus proche
        if min_dist == dist_left:
            # Près du mur gauche
            return (random.randint(0, 20),
                    self.immune_cell.y + random.randint(-variation, variation))
        elif min_dist == dist_right:
            # Près du mur droit
            return (random.randint(self.width - 20, self.width),
                    self.immune_cell.y + random.randint(-variation, variation))
        elif min_dist == dist_top:
            # Près du mur supérieur
            return (self.immune_cell.x + random.randint(-variation, variation),
                    random.randint(0, 20))
        else:
            # Près du mur inférieur
            return (self.immune_cell.x + random.randint(-variation, variation),
                    random.randint(self.height - 20, self.height))


    def _calculate_reward(self, prev_health, prev_num_pathogens):
        """
        Calcule la récompense en fonction des changements d'état
        """
        reward = 0.0

        # Récompense de survie
        reward += 0.1  # Petite récompense pour chaque pas de temps survécu

        # Pénalité pour perte de santé
        health_diff = self.immune_cell.health - prev_health
        reward += health_diff * 0.05  # Pénalité pour chaque point de vie perdu

        # Récompense pour la distance aux pathogènes (fuite)
        min_distance = float('inf')
        for pathogen in self.tissue.pathogens:
            dx = pathogen.x - self.immune_cell.x
            dy = pathogen.y - self.immune_cell.y
            distance = np.sqrt(dx ** 2 + dy ** 2)
            min_distance = min(min_distance, distance)

        # Récompenser le maintien d'une distance de sécurité
        safe_distance = 100  # Distance considérée comme "sûre"
        if min_distance < float('inf'):
            if min_distance > safe_distance:
                reward += 0.2  # Récompense pour maintenir la distance
            else:
                # Récompense proportionnelle à la distance (plus c'est proche, plus la pénalité est grande)
                reward += 0.2 * (min_distance / safe_distance)

        # Grande pénalité si le lymphocyte meurt
        if self.immune_cell.is_dead():
            reward -= 10.0

        wall_penalty = self._calculate_wall_penalty()
        reward -= wall_penalty

        return reward

    def _calculate_wall_penalty(self):
        """Calcule une pénalité pour la proximité aux bords"""
        # Distance aux quatre murs
        dist_left = self.immune_cell.x
        dist_right = self.width - self.immune_cell.x
        dist_top = self.immune_cell.y
        dist_bottom = self.height - self.immune_cell.y

        # Trouver la distance minimale à un mur
        min_dist = min(dist_left, dist_right, dist_top, dist_bottom)

        # Zone sûre (pas de pénalité)
        safe_margin = 100

        if min_dist < safe_margin:
            # Pénalité augmente exponentiellement plus on s'approche du mur
            # La formule peut être ajustée selon la sensibilité désirée
            return 0.5 * ((safe_margin - min_dist) / safe_margin) ** 2

        return 0.0

    def _calculate_center_reward(self):
        """Récompense pour rester près du centre"""
        center_x = self.width / 2
        center_y = self.height / 2

        # Distance au centre
        dx = self.immune_cell.x - center_x
        dy = self.immune_cell.y - center_y
        distance = np.sqrt(dx ** 2 + dy ** 2)

        # Rayon de la zone centrale considérée comme optimale
        optimal_radius = self.width / 4

        if distance < optimal_radius:
            return 0.1  # Récompense constante dans la zone optimale
        else:
            # Récompense diminue avec la distance
            return 0.1 * (optimal_radius / distance)


    def render(self):
        """
        Version simplifiée du rendu (pour le débogage)
        """
        print(f"Step: {self.current_step}, Health: {self.immune_cell.health}, Pathogens: {len(self.tissue.pathogens)}")