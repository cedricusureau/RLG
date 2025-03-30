# neural_battler/src/game/entities/ai_immune_cell.py
import pygame
import math
import random
from neural_battler.src.game.entities.immune_cell import ImmuneCell
from neural_battler.src.ai.inference.immune_cell_controller import ImmuneCellController


class AIImmuneCell(ImmuneCell):
    def __init__(self, x, y, cell_type="t_cell", ai_model_path=None):
        super().__init__(x, y, cell_type)
        self.controller = None
        self.ai_controlled = False

        # Charger le contrôleur IA si un modèle est spécifié
        if ai_model_path:
            try:
                self.controller = ImmuneCellController(ai_model_path)
                self.ai_controlled = True
                self.color = (100, 100, 255)  # Bleu clair pour indiquer cellule IA
            except Exception as e:
                print(f"Erreur lors du chargement du modèle IA: {e}")

    def update(self, game_state):
        """
        Met à jour l'état de la cellule immunitaire
        Si contrôlée par IA, utilise le modèle pour le mouvement
        Sinon, utilise le comportement par défaut
        """
        if self.ai_controlled and self.controller:
            # Laisser le contrôleur IA gérer le mouvement
            self.controller.update(self, game_state.pathogens, game_state)

            # Le reste de la logique normale (attaque, etc.)
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
        else:
            # Comportement par défaut
            super().update(game_state)

    def set_ai_model(self, model_path):
        """
        Change ou active le modèle d'IA pour cette cellule
        """
        try:
            self.controller = ImmuneCellController(model_path)
            self.ai_controlled = True
            self.color = (100, 100, 255)  # Bleu clair pour indiquer cellule IA
            return True
        except Exception as e:
            print(f"Erreur lors du chargement du modèle IA: {e}")
            return False

    def disable_ai(self):
        """
        Désactive le contrôle par IA
        """
        self.ai_controlled = False
        self.color = (0, 0, 255)  # Retour à la couleur bleue standard