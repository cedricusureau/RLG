# neural_battler/src/ai/inference/immune_cell_controller.py
import torch
from ..models import ImmuneCellAgent


class ImmuneCellController:
    def __init__(self, model_path, state_size=23, action_size=9):
        """
        Contrôleur qui utilise un modèle entraîné pour diriger un lymphocyte
        """
        self.agent = ImmuneCellAgent(state_size, action_size)
        self.agent.load(model_path)
        self.agent.policy_network.eval()  # Passe en mode évaluation
        # Définir une vitesse par défaut pour le contrôleur
        self.default_speed = 1.0

    def get_action(self, immune_cell, pathogens, tissue_width, tissue_height):
        """
        Détermine l'action à prendre pour le lymphocyte basé sur l'état actuel
        """
        state = self.agent.get_state(immune_cell, pathogens, tissue_width, tissue_height)
        with torch.no_grad():
            q_values = self.agent.policy_network(state)
            action = torch.argmax(q_values).item()

        return action

    def update(self, immune_cell, pathogens, tissue):
        """
        Met à jour le comportement du lymphocyte en fonction du modèle
        """
        state = self._get_state(immune_cell, pathogens, tissue.width, tissue.height)
        with torch.no_grad():
            q_values = self.agent.policy_network(state)
            action_idx = torch.argmax(q_values).item()

        # Séparation des actions de mouvement et de capacité spéciale
        # Action 0-8: mouvement, Action 9: utiliser capacité spéciale + ne pas bouger
        use_special = action_idx == 9
        movement_idx = 8 if use_special else action_idx  # Si spécial, ne pas bouger (action 8)

        # Utiliser la vitesse par défaut
        dx, dy = self.agent.action_to_movement(movement_idx, self.default_speed)

        # Mettre à jour la position du lymphocyte
        new_x = immune_cell.x + dx
        new_y = immune_cell.y + dy

        # Vérifier que la nouvelle position est valide
        if tissue.is_valid_position(new_x, new_y):
            immune_cell.x = new_x
            immune_cell.y = new_y

        return {"use_special": use_special}