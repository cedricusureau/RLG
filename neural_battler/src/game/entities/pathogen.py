# src/game/entities/pathogen.py
import pygame
import math
import random


class Pathogen:
    def __init__(self, x, y, pathogen_type="bacteria"):
        self.x = x
        self.y = y
        self.pathogen_type = pathogen_type
        self.health = 50
        self.max_health = 50
        self.attack_damage = 5
        self.attack_range = 1.5  # Portée d'attaque courte
        self.attack_cooldown = 0
        self.attack_cooldown_max = 45
        self.speed = 0.7
        self.radius = 10
        self.color = (255, 0, 0)  # Rouge pour les pathogènes

    def update(self, game_state):
        # Les bactéries ciblent maintenant toujours le lymphocyte
        if game_state.immune_cells:
            # Toujours cibler le lymphocyte (premier dans la liste)
            self.target = game_state.immune_cells[0]

            # Calculer la distance au lymphocyte
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            # Si la bactérie est à portée d'attaque et le cooldown est terminé
            if distance <= self.attack_range + self.radius + self.target.radius and self.attack_cooldown == 0:
                self.attack(self.target)
            else:
                # Sinon, se déplacer vers le lymphocyte
                self.move_towards_target()

            # Gestion du cooldown d'attaque
            if self.attack_cooldown > 0:
                self.attack_cooldown -= 1
        else:
            # Si pas de lymphocyte, errer aléatoirement
            self.wander()

    def move_towards_target(self):
        if not self.target:
            return

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # Si la distance est positive, se déplacer vers la cible
        if distance > 0:
            dx = dx / distance * self.speed
            dy = dy / distance * self.speed
            self.x += dx
            self.y += dy

    def wander(self):
        # Mouvement aléatoire quand pas de cible
        dx = random.uniform(-0.5, 0.5) * self.speed
        dy = random.uniform(-0.5, 0.5) * self.speed

        # Vérifie que le mouvement reste dans les limites du terrain
        new_x = self.x + dx
        new_y = self.y + dy

        # Pour le prototype, nous supposerons que c'est valide
        self.x = new_x
        self.y = new_y

    def attack(self, target):
        target.take_damage(self.attack_damage)
        self.attack_cooldown = self.attack_cooldown_max

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0

    def is_dead(self):
        return self.health <= 0

    def draw(self, screen, offset_x=0, offset_y=0):
        # Dessine le pathogène
        pygame.draw.circle(screen, self.color,
                           (int(self.x + offset_x), int(self.y + offset_y)),
                           self.radius)

        # Dessine la barre de vie
        health_width = int(self.radius * 2 * (self.health / self.max_health))
        health_height = 3
        health_x = int(self.x + offset_x - self.radius)
        health_y = int(self.y + offset_y - self.radius - 7)

        # Fond de la barre de vie
        pygame.draw.rect(screen, (100, 100, 100),
                         (health_x, health_y, self.radius * 2, health_height))
        # Barre de vie active
        pygame.draw.rect(screen, (0, 255, 0),
                         (health_x, health_y, health_width, health_height))