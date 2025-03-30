# src/game/entities/immune_cell.py
import pygame
import math
import random


class ImmuneCell:
    def __init__(self, x, y, cell_type="t_cell"):
        self.x = x
        self.y = y
        self.cell_type = cell_type
        self.health = 100
        self.max_health = 100
        self.attack_damage = 15
        self.attack_range = 250  # Portée augmentée pour les projectiles
        self.attack_cooldown = 0
        self.attack_cooldown_max = 45  # Frames entre chaque tir
        self.radius = 15  # Rayon du cercle représentant la cellule
        self.color = (0, 0, 255)  # Bleu pour les cellules immunitaires
        self.projectiles = []  # Liste pour stocker les projectiles

    def update(self, game_state):
        # Récupération des pathogens à portée
        pathogens = game_state.get_nearby_pathogens(self.x, self.y, self.attack_range)

        # Gestion du cooldown d'attaque
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Tir si des pathogènes sont à portée et cooldown terminé
        if pathogens and self.attack_cooldown == 0:
            closest_pathogen = self.find_closest_target(pathogens)
            if closest_pathogen:
                self.shoot_at(closest_pathogen)
                self.attack_cooldown = self.attack_cooldown_max

        # Mise à jour des projectiles
        self.update_projectiles(game_state)

    def shoot_at(self, target):
        # Créer un nouveau projectile
        dx = target.x - self.x
        dy = target.y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # Normaliser le vecteur de direction
        if distance > 0:
            dx = dx / distance * 3  # Vitesse du projectile
            dy = dy / distance * 3

        projectile = {
            'x': self.x,
            'y': self.y,
            'dx': dx,
            'dy': dy,
            'damage': self.attack_damage,
            'radius': 5,
            'color': (0, 255, 255)  # Cyan pour les projectiles
        }

        self.projectiles.append(projectile)

    def update_projectiles(self, game_state):
        # Mettre à jour la position de chaque projectile et vérifier les collisions
        projectiles_to_remove = []

        for i, projectile in enumerate(self.projectiles):
            # Mettre à jour la position
            projectile['x'] += projectile['dx']
            projectile['y'] += projectile['dy']

            # Vérifier si le projectile est hors limites
            if (projectile['x'] < 0 or projectile['x'] > game_state.width or
                    projectile['y'] < 0 or projectile['y'] > game_state.height):
                projectiles_to_remove.append(i)
                continue

            # Vérifier les collisions avec les pathogènes
            for pathogen in game_state.pathogens:
                dx = pathogen.x - projectile['x']
                dy = pathogen.y - projectile['y']
                distance = math.sqrt(dx ** 2 + dy ** 2)

                if distance < pathogen.radius + projectile['radius']:
                    # Collision détectée
                    pathogen.take_damage(projectile['damage'])
                    projectiles_to_remove.append(i)
                    break

        # Supprimer les projectiles qui ont frappé une cible ou sont hors limites
        for i in sorted(projectiles_to_remove, reverse=True):
            if i < len(self.projectiles):
                self.projectiles.pop(i)

    def find_closest_target(self, targets):
        closest = None
        min_distance = float('inf')

        for target in targets:
            dx = target.x - self.x
            dy = target.y - self.y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            if distance < min_distance:
                min_distance = distance
                closest = target

        return closest

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0

    def is_dead(self):
        return self.health <= 0

    def draw(self, screen, offset_x=0, offset_y=0):
        # Dessine la cellule immunitaire
        pygame.draw.circle(screen, self.color,
                           (int(self.x + offset_x), int(self.y + offset_y)),
                           self.radius)

        # Dessine la barre de vie
        health_width = int(self.radius * 2 * (self.health / self.max_health))
        health_height = 5
        health_x = int(self.x + offset_x - self.radius)
        health_y = int(self.y + offset_y - self.radius - 10)

        # Fond de la barre de vie
        pygame.draw.rect(screen, (100, 100, 100),
                         (health_x, health_y, self.radius * 2, health_height))
        # Barre de vie active
        pygame.draw.rect(screen, (0, 255, 0),
                         (health_x, health_y, health_width, health_height))

        # Dessine les projectiles
        for projectile in self.projectiles:
            pygame.draw.circle(screen, projectile['color'],
                               (int(projectile['x'] + offset_x), int(projectile['y'] + offset_y)),
                               projectile['radius'])