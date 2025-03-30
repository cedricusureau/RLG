# neural_battler/src/ai/training/environment.py
import numpy as np
import random
from neural_battler.src.game.world.tissue import Tissue
from neural_battler.src.game.entities.immune_cell import ImmuneCell
from neural_battler.src.game.entities.pathogen import Pathogen


class TrainingEnvironment:
    def __init__(self, width=800, height=600, max_steps=1000):
        self.width = width
        self.height = height
        self.max_steps = max_steps
        self.current_step = 0
        self.tissue = None
        self.immune_cell = None
        # Définir une vitesse par défaut pour l'environnement d'entraînement
        self.default_speed = 1.0
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
        from neural_battler.src.ai.models.immune_cell_model import ImmuneCellAgent
        dummy_agent = ImmuneCellAgent(23, 9)  # Juste pour utiliser la méthode get_state
        return dummy_agent.get_state(self.immune_cell, self.tissue.pathogens, self.width, self.height)

    def step(self, action):
        """
        Effectue une action et retourne le nouvel état, la récompense, et si l'épisode est terminé
        """
        from neural_battler.src.ai.models.immune_cell_model import ImmuneCellAgent
        dummy_agent = ImmuneCellAgent(23, 9)

        # Utiliser la vitesse par défaut définie dans cette classe plutôt que d'accéder à l'attribut
        # speed de ImmuneCell qui n'existe peut-être pas
        dx, dy = dummy_agent.action_to_movement(action, self.default_speed)

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

        return reward

    def render(self):
        """
        Version simplifiée du rendu (pour le débogage)
        """
        print(f"Step: {self.current_step}, Health: {self.immune_cell.health}, Pathogens: {len(self.tissue.pathogens)}")