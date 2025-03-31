import numpy as np
import random

from sympy.physics.units import action

from ...game.world.tissue import Tissue
from ..models import ImmuneCellAgent


class TrainingEnvironment:
    """Environnement d'entraînement pour un agent lymphocyte par renforcement"""

    def __init__(self, width=800, height=600, max_steps=3000):
        self.width = width
        self.height = height
        self.max_steps = max_steps
        self.current_step = 0
        self.tissue = None
        self.immune_cell = None
        self.default_speed = 1.0
        self.wall_stuck_counter = 0
        self.helper_agent = ImmuneCellAgent(28, 10)
        self.center_x = width / 2
        self.center_y = height / 2
        self.reset()

    def reset(self):
        """Réinitialise l'environnement pour un nouvel épisode"""
        self.current_step = 0
        self.wall_stuck_counter = 0
        self.tissue = Tissue(self.width, self.height)

        # Placer le lymphocyte au centre
        self.immune_cell = self.tissue.add_immune_cell(self.center_x, self.center_y, "t_cell")

        self.prev_special_ready = True if hasattr(self.immune_cell, 'special_ready') else False

        # Position précédente pour calculer les mouvements
        self.prev_pos_x = self.center_x
        self.prev_pos_y = self.center_y

        # Ajouter quelques pathogènes aléatoirement
        for _ in range(5):
            self._spawn_random_pathogen()

        return self._get_state()

    def _get_state(self):
        """Récupère l'état actuel pour l'agent"""
        return self.helper_agent.get_state(
            self.immune_cell,
            self.tissue.pathogens,
            self.width,
            self.height
        )

    def step(self, action):
        """Effectue une action et retourne le nouvel état, la récompense, et si l'épisode est terminé"""
        # Obtenir le vecteur de mouvement
        dx, dy = self.helper_agent.action_to_movement(action, self.default_speed)

        # Sauvegarder l'état précédent
        prev_health = self.immune_cell.health
        prev_num_pathogens = len(self.tissue.pathogens)
        prev_pos_x, prev_pos_y = self.immune_cell.x, self.immune_cell.y

        # Appliquer le mouvement
        new_x = self.immune_cell.x + dx
        new_y = self.immune_cell.y + dy

        # Vérifier si la position est valide
        if self.tissue.is_valid_position(new_x, new_y):
            self.immune_cell.x = new_x
            self.immune_cell.y = new_y

        # Mettre à jour l'environnement
        self.tissue.update()
        self.current_step += 1

        # Spawn de pathogènes près des murs avec probabilité réduite
        if self._is_near_wall() and random.random() < 0.05:
            self._spawn_pathogen_near_wall()

        # Calculer la récompense
        reward = self._calculate_reward(prev_health, prev_num_pathogens, dx, dy)

        # Vérifier la condition de fin
        done = (
                self.immune_cell.is_dead() or
                self.current_step >= self.max_steps
        )

        # Respawn des pathogènes si tous sont éliminés
        if len(self.tissue.pathogens) == 0:
            self._spawn_random_pathogen()

        return self._get_state(), reward, done

    def _is_near_wall(self):
        """Vérifie si le lymphocyte est proche d'un mur"""
        margin = 60
        return (
                self.immune_cell.x < margin or
                self.immune_cell.x > self.width - margin or
                self.immune_cell.y < margin or
                self.immune_cell.y > self.height - margin
        )

    def _spawn_random_pathogen(self):
        """Génère un pathogène à une position aléatoire loin des murs"""
        margin = 100
        x = random.uniform(margin, self.width - margin)
        y = random.uniform(margin, self.height - margin)
        self.tissue.add_pathogen(x, y, "bacteria")

    def _spawn_pathogen_near_wall(self):
        """Génère un pathogène près du mur le plus proche du lymphocyte"""
        distances = [
            (self.immune_cell.x, "left"),
            (self.width - self.immune_cell.x, "right"),
            (self.immune_cell.y, "top"),
            (self.height - self.immune_cell.y, "bottom")
        ]

        dist, wall = min(distances, key=lambda x: x[0])
        variation = 30

        if wall == "left":
            pos = (random.randint(0, 20), self.immune_cell.y + random.randint(-variation, variation))
        elif wall == "right":
            pos = (
            random.randint(self.width - 20, self.width), self.immune_cell.y + random.randint(-variation, variation))
        elif wall == "top":
            pos = (self.immune_cell.x + random.randint(-variation, variation), random.randint(0, 20))
        else:  # bottom
            pos = (
            self.immune_cell.x + random.randint(-variation, variation), random.randint(self.height - 20, self.height))

        self.tissue.add_pathogen(pos[0], pos[1], "bacteria")

    def _apply_center_force(self):
        """Force un mouvement vers le centre"""
        dir_x = self.center_x - self.immune_cell.x
        dir_y = self.center_y - self.immune_cell.y
        dist = np.sqrt(dir_x ** 2 + dir_y ** 2)

        if dist > 0:
            # Amplifier le mouvement pour créer un "coup de pouce" plus fort
            force = 1.5 * self.default_speed
            self.immune_cell.x += (dir_x / dist) * force
            self.immune_cell.y += (dir_y / dist) * force

    def _calculate_reward(self, prev_health, prev_num_pathogens, dx, dy):
        reward = 0.0

        # Récompense principale: pénalité pour perte de vie
        health_change = self.immune_cell.health - prev_health
        if health_change < 0:
            return -1.0  # Forte pénalité fixe pour toute perte de vie

        # Bonus pour l'élimination de pathogènes
        pathogen_change = prev_num_pathogens - len(self.tissue.pathogens)
        if pathogen_change > 0:
            return 1.0  # Bonus fixe pour avoir éliminé un pathogène

        # Petite récompense pour le mouvement
        if abs(dx) > 0.1 or abs(dy) > 0.1:
            return 0.1

        return 0.0  # Récompense neutre par défaut

    def _is_moving_away_from_walls(self, dx, dy):
        """Vérifie si le mouvement éloigne la cellule des murs"""
        # Calculer la distance aux murs avant et après le mouvement
        wall_dist_before = min(
            self.immune_cell.x,  # Distance au mur gauche
            self.width - self.immune_cell.x,  # Distance au mur droit
            self.immune_cell.y,  # Distance au mur supérieur
            self.height - self.immune_cell.y  # Distance au mur inférieur
        )

        wall_dist_after = min(
            self.immune_cell.x + dx,  # Nouvelle distance au mur gauche
            self.width - (self.immune_cell.x + dx),  # Nouvelle distance au mur droit
            self.immune_cell.y + dy,  # Nouvelle distance au mur supérieur
            self.height - (self.immune_cell.y + dy)  # Nouvelle distance au mur inférieur
        )

        # Retourne True si la nouvelle position est plus éloignée des murs
        return wall_dist_after > wall_dist_before

    def render(self):
        """Version simplifiée du rendu pour débogage"""
        status = "✓" if not self._is_near_wall() else "⚠"
        if self.wall_stuck_counter > 0:
            status = f"⚠ Bloqué: {self.wall_stuck_counter}"

        print(
            f"Étape: {self.current_step}, Santé: {self.immune_cell.health}, Pathogènes: {len(self.tissue.pathogens)} {status}")