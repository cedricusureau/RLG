import numpy as np
import random
from ...game.world.tissue import Tissue
from ..models import ImmuneCellAgent


class TrainingEnvironment:
    """Environnement d'entraînement pour un agent lymphocyte par renforcement"""

    def __init__(self, width=800, height=600, max_steps=1000):
        self.width = width
        self.height = height
        self.max_steps = max_steps
        self.current_step = 0
        self.tissue = None
        self.immune_cell = None
        self.default_speed = 1.0
        self.wall_stuck_counter = 0
        self.helper_agent = ImmuneCellAgent(23, 9)
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

        # Vérifier si l'agent est bloqué contre un mur
        if self._is_near_wall():
            if abs(self.immune_cell.x - prev_pos_x) < 0.1 and abs(self.immune_cell.y - prev_pos_y) < 0.1:
                self.wall_stuck_counter += 1
            else:
                self.wall_stuck_counter = 0
        else:
            self.wall_stuck_counter = 0

        # Spawn de pathogènes près des murs avec probabilité réduite
        if self._is_near_wall() and random.random() < 0.05:
            self._spawn_pathogen_near_wall()

        # Calculer la récompense
        reward = self._calculate_reward(prev_health, prev_num_pathogens, dx, dy)

        # Vérifier la condition de fin
        done = (
                self.immune_cell.is_dead() or
                self.current_step >= self.max_steps or
                self.wall_stuck_counter >= 20  # Terminer l'épisode si bloqué trop longtemps
        )

        # Respawn des pathogènes si tous sont éliminés
        if len(self.tissue.pathogens) == 0:
            reward += 5.0  # Bonus pour avoir éliminé tous les pathogènes
            for _ in range(random.randint(3, 5)):
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
        """Calcule la récompense basée sur plusieurs facteurs"""
        reward = 0.0

        # 1. Récompense de base pour la survie
        reward += 0.1

        # 2. Récompense/pénalité pour changement de santé
        health_diff = self.immune_cell.health - prev_health
        reward += health_diff * 0.1

        # 3. Pénalité pour être près d'un mur
        if self._is_near_wall():
            # Distance au mur le plus proche
            wall_dist = min(
                self.immune_cell.x,
                self.width - self.immune_cell.x,
                self.immune_cell.y,
                self.height - self.immune_cell.y
            )
            # Pénalité qui augmente à mesure qu'on s'approche du mur
            wall_penalty = 0.5 * (1 - (wall_dist / 60))
            reward -= wall_penalty

            # Pénalité sévère pour immobilité près des murs
            if abs(dx) < 0.1 and abs(dy) < 0.1:
                reward -= 1.0

            # Récompense pour mouvement vers le centre quand près d'un mur
            dir_to_center_x = self.center_x - self.immune_cell.x
            dir_to_center_y = self.center_y - self.immune_cell.y
            center_dist = np.sqrt(dir_to_center_x ** 2 + dir_to_center_y ** 2)

            if center_dist > 0:
                # Vérifier si le mouvement est orienté vers le centre
                dot_product = (dx * dir_to_center_x + dy * dir_to_center_y) / center_dist
                if dot_product > 0:  # Si le mouvement est vers le centre
                    reward += 1.0 * dot_product

        # 4. Récompense pour maintenir une distance de sécurité avec les pathogènes
        if self.tissue.pathogens:
            min_distance = float('inf')
            for pathogen in self.tissue.pathogens:
                dist = np.sqrt((pathogen.x - self.immune_cell.x) ** 2 + (pathogen.y - self.immune_cell.y) ** 2)
                min_distance = min(min_distance, dist)

            safe_distance = 100
            if min_distance < safe_distance:
                # Petite récompense proportionnelle à la distance
                reward += 0.2 * (min_distance / safe_distance)
            else:
                reward += 0.2  # Récompense complète si à distance sûre

        # 5. Pénalité progressive si bloqué contre un mur
        if self.wall_stuck_counter > 0:
            reward -= 0.5 * self.wall_stuck_counter

        # 6. Forte pénalité si mort
        if self.immune_cell.is_dead():
            reward -= 10.0

        return reward

    def render(self):
        """Version simplifiée du rendu pour débogage"""
        status = "✓" if not self._is_near_wall() else "⚠"
        if self.wall_stuck_counter > 0:
            status = f"⚠ Bloqué: {self.wall_stuck_counter}"

        print(
            f"Étape: {self.current_step}, Santé: {self.immune_cell.health}, Pathogènes: {len(self.tissue.pathogens)} {status}")