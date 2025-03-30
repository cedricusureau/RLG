# neural_battler/src/game/world/tissue.py
import random
from neural_battler.src.game.entities.immune_cell import ImmuneCell
from neural_battler.src.game.entities.pathogen import Pathogen


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
        self.difficulty_factor = 0.98  # Réduire le temps de 2% à chaque spawn
        self.game_time = 0  # Compteur de temps de jeu

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

    def get_nearby_pathogens(self, x, y, radius):
        # Retourne les pathogènes à portée
        nearby = []
        for pathogen in self.pathogens:
            dx = pathogen.x - x
            dy = pathogen.y - y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance <= radius:
                nearby.append(pathogen)
        return nearby

    def get_nearby_immune_cells(self, x, y, radius):
        # Retourne les cellules immunitaires à portée
        nearby = []
        for cell in self.immune_cells:
            dx = cell.x - x
            dy = cell.y - y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance <= radius:
                nearby.append(cell)
        return nearby

    def add_immune_cell(self, x, y, cell_type="t_cell"):
        cell = ImmuneCell(x, y, cell_type)
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