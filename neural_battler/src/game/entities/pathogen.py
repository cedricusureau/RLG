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
        self.attack_range = 1.5
        self.attack_cooldown = 0
        self.attack_cooldown_max = 45  # Plus lent que les cellules immunitaires
        self.speed = 0.7
        self.target = None
        self.radius = 10  # Plus petit que les cellules immunitaires
        self.color = (255, 0, 0)  # Rouge pour les pathogènes
        self.division_timer = random.randint(500, 1000)  # Temps avant division

    def update(self, game_state):
        # Récupération des cellules immunitaires proches
        immune_cells = game_state.get_nearby_immune_cells(self.x, self.y, self.attack_range)

        # Recherche d'une cible si on n'en a pas
        if not self.target or self.target not in immune_cells:
            if immune_cells:
                self.target = self.find_closest_target(immune_cells)
            else:
                self.target = None

        # Gestion du cooldown d'attaque
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Attaque si une cible est disponible
        if self.target and self.attack_cooldown == 0:
            self.attack(self.target)

        # Déplacement vers la cible ou errance aléatoire
        if self.target:
            self.move_towards_target()
        else:
            self.wander()

        # Gestion de la division bactérienne
        if self.pathogen_type == "bacteria":
            self.division_timer -= 1
            if self.division_timer <= 0 and self.health > self.max_health * 0.6:
                # Création d'une nouvelle bactérie si suffisamment de santé
                if game_state.can_add_pathogen():
                    new_x = self.x + random.uniform(-20, 20)
                    new_y = self.y + random.uniform(-20, 20)
                    game_state.add_pathogen(new_x, new_y, "bacteria")
                    # La division coûte de la santé
                    self.health -= self.max_health * 0.3
                    self.division_timer = random.randint(500, 1000)

    def move_towards_target(self):
        if not self.target:
            return

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # Ne se déplace que si la cible est hors de portée d'attaque
        if distance > self.attack_range:
            # Normalisation et application de la vitesse
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