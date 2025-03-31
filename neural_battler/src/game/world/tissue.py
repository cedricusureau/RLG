# neural_battler/src/game/world/tissue.py
import random

import random
import numpy as np
from scipy.spatial import cKDTree

from ..entities.immune_cell import ImmuneCell
from ..entities.pathogen import Pathogen


class Tissue:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.immune_cells = []
        self.pathogens = []
        self.effects = []  # Pour animations et effets visuels

        # Paramètres d'apparition des pathogènes
        self.initial_spawn_time = 180  # 3 secondes à 60 FPS
        self.min_spawn_time = 30  # Intervalle minimal: 0.5 seconde
        self.pathogen_spawn_timer = self.initial_spawn_time  # Timer initial
        self.pathogen_spawn_cooldown = self.pathogen_spawn_timer

        # Facteur de progression de la difficulté
        self.difficulty_factor = 1  # Réduire le temps de 2% à chaque spawn
        self.game_time = 0  # Compteur de temps de jeu

        self._update_spatial_index = True
        self._pathogen_tree = None
        self._immune_cell_tree = None

    def update(self):
        # Mise à jour du compteur de temps
        self.game_time += 1

        # Mise à jour de toutes les entités
        game_state = self  # Pour la simplicité

        # Mise à jour des cellules immunitaires
        for cell in self.immune_cells[:]:
            cell.update(game_state)
            if cell.is_dead():
                self.immune_cells.remove(cell)

        # Mise à jour des pathogènes
        for pathogen in self.pathogens[:]:
            pathogen.update(game_state)
            if pathogen.is_dead():
                self.pathogens.remove(pathogen)

        # Gestion de l'apparition aléatoire des nouveaux pathogènes
        self.pathogen_spawn_cooldown -= 1
        if self.pathogen_spawn_cooldown <= 0 and self.can_add_pathogen():
            # Spawn un nouveau pathogène à une position aléatoire
            x = random.randint(50, self.width - 50)
            y = random.randint(50, self.height - 50)
            self.add_pathogen(x, y, "bacteria")

            # Réduire le temps avant la prochaine apparition (difficulté progressive)
            self.pathogen_spawn_timer = max(
                self.min_spawn_time,
                int(self.pathogen_spawn_timer * self.difficulty_factor)
            )
            self.pathogen_spawn_cooldown = self.pathogen_spawn_timer

        # Mise à jour des effets visuels (à implémenter plus tard)
        for effect in self.effects[:]:
            # Logique d'animation...
            pass

        self._update_spatial_index = True

    def get_nearby_pathogens(self, x, y, radius):
        """Retourne les pathogènes à portée en utilisant KDTree pour efficacité"""
        # Si peu de pathogènes, utiliser la méthode directe
        if len(self.pathogens) < 10:
            # Méthode simple originale pour petits nombres
            nearby = []
            for pathogen in self.pathogens:
                dx = pathogen.x - x
                dy = pathogen.y - y
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if distance <= radius:
                    nearby.append(pathogen)
            return nearby

        # Pour beaucoup de pathogènes, utiliser KDTree
        try:
            # Recalculer l'arbre KD seulement si nécessaire
            if self._update_spatial_index or self._pathogen_tree is None:
                positions = np.array([[p.x, p.y] for p in self.pathogens])
                self._pathogen_tree = cKDTree(positions)

            # Trouver les indices des pathogènes proches
            indices = self._pathogen_tree.query_ball_point([x, y], radius)
            return [self.pathogens[i] for i in indices]

        except (ValueError, ImportError) as e:
            # Fallback en cas d'erreur avec la méthode optimisée
            print(f"Erreur avec KDTree: {e}, utilisation de la méthode standard")
            # Utiliser la méthode originale comme fallback
            nearby = []
            for pathogen in self.pathogens:
                dx = pathogen.x - x
                dy = pathogen.y - y
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if distance <= radius:
                    nearby.append(pathogen)
            return nearby

    def get_nearby_immune_cells(self, x, y, radius):
        """Retourne les cellules immunitaires à portée en utilisant KDTree pour efficacité"""
        # Même logique que pour get_nearby_pathogens
        if len(self.immune_cells) < 10:
            # Méthode originale comme fallback
            nearby = []
            for cell in self.immune_cells:
                dx = cell.x - x
                dy = cell.y - y
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if distance <= radius:
                    nearby.append(cell)
            return nearby

        # Pour plusieurs cellules, utiliser KDTree
        try:
            if self._update_spatial_index or self._immune_cell_tree is None:
                positions = np.array([[c.x, c.y] for c in self.immune_cells])
                self._immune_cell_tree = cKDTree(positions)

            indices = self._immune_cell_tree.query_ball_point([x, y], radius)
            return [self.immune_cells[i] for i in indices]

        except (ValueError, ImportError) as e:
            # Fallback
            nearby = []
            for cell in self.immune_cells:
                dx = cell.x - x
                dy = cell.y - y
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if distance <= radius:
                    nearby.append(cell)
            return nearby

    def add_immune_cell(self, x, y, cell_type="t_cell", ai_model_path=None):
        cell = ImmuneCell(x, y, cell_type, ai_model_path)
        self.immune_cells.append(cell)
        return cell

    def add_pathogen(self, x, y, pathogen_type="bacteria"):
        pathogen = Pathogen(x, y, pathogen_type)
        self.pathogens.append(pathogen)
        return pathogen

    def can_add_pathogen(self):
        # Limitation du nombre de pathogènes pour éviter les explosions de population
        return len(self.pathogens) < 20  # Limitation à 20 pathogènes max

    def add_effect(self, effect_type, x, y, radius):
        # À implémenter plus tard
        self.effects.append({
            "type": effect_type,
            "x": x,
            "y": y,
            "radius": radius,
            "duration": 30  # Frames
        })

    def is_valid_position(self, x, y):
        # Vérifie si une position est dans les limites du tissu
        return 0 <= x < self.width and 0 <= y < self.height

    def draw(self, screen):
        # Dessine le fond
        screen.fill((240, 240, 245))  # Fond légèrement bleuté

        # Dessine les cellules et pathogènes
        for cell in self.immune_cells:
            cell.draw(screen)

        for pathogen in self.pathogens:
            pathogen.draw(screen)

        # Dessine les effets (à implémenter plus tard)
        for effect in self.effects:
            # Logique de dessin...
            pass