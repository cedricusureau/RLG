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
        self.mana = 0
        self.max_mana = 100
        self.attack_damage = 15
        self.attack_range = 3
        self.attack_cooldown = 0
        self.attack_cooldown_max = 30  # Frames entre chaque attaque
        self.speed = 1.0
        self.target = None
        self.radius = 15  # Rayon du cercle représentant la cellule
        self.color = (0, 0, 255)  # Bleu pour les cellules immunitaires

    def update(self, game_state):
        # Récupération des pathogens proches
        pathogens = game_state.get_nearby_pathogens(self.x, self.y, self.attack_range)

        # Recherche d'une cible si on n'en a pas
        if not self.target or self.target not in pathogens:
            if pathogens:
                self.target = self.find_closest_target(pathogens)
            else:
                self.target = None

        # Gestion du cooldown d'attaque
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Attaque si une cible est disponible
        if self.target and self.attack_cooldown == 0:
            self.attack(self.target)
            # Chaque attaque de base génère du mana
            self.mana = min(self.max_mana, self.mana + 20)

        # Utilisation de la capacité spéciale si mana plein
        if self.mana >= self.max_mana:
            self.use_special_ability(game_state)

        # Déplacement vers la cible ou errance aléatoire
        if self.target:
            self.move_towards_target()
        else:
            self.wander()

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
        # (nécessite une méthode is_valid_position dans game_state)
        new_x = self.x + dx
        new_y = self.y + dy

        # Pour le prototype, nous supposerons que c'est valide
        self.x = new_x
        self.y = new_y

    def attack(self, target):
        target.take_damage(self.attack_damage)
        self.attack_cooldown = self.attack_cooldown_max

    def use_special_ability(self, game_state):
        # Implémentation de la capacité spéciale du LT: attaque de zone
        pathogens = game_state.get_nearby_pathogens(self.x, self.y, self.attack_range * 2)

        for pathogen in pathogens:
            pathogen.take_damage(self.attack_damage * 2)

        # Animation simple pour l'attaque spéciale (ajout ultérieur)
        # game_state.add_effect("aoe_attack", self.x, self.y, self.attack_range * 2)

        # Réinitialisation du mana
        self.mana = 0

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

        # Dessine la barre de mana
        mana_width = int(self.radius * 2 * (self.mana / self.max_mana))
        mana_height = 3
        mana_x = int(self.x + offset_x - self.radius)
        mana_y = int(self.y + offset_y - self.radius - 5)

        # Fond de la barre de mana
        pygame.draw.rect(screen, (100, 100, 100),
                         (mana_x, mana_y, self.radius * 2, mana_height))
        # Barre de mana active
        pygame.draw.rect(screen, (0, 0, 255),
                         (mana_x, mana_y, mana_width, mana_height))