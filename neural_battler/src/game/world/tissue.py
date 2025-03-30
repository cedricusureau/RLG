# src/game/world/tissue.py
class Tissue:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.immune_cells = []
        self.pathogens = []
        self.effects = []  # Pour animations et effets visuels

    def update(self):
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
        from game.entities.immune_cell import ImmuneCell
        cell = ImmuneCell(x, y, cell_type)
        self.immune_cells.append(cell)
        return cell

    def add_pathogen(self, x, y, pathogen_type="bacteria"):
        from game.entities.pathogen import Pathogen
        pathogen = Pathogen(x, y, pathogen_type)
        self.pathogens.append(pathogen)
        return pathogen

    def can_add_pathogen(self):
        # Limitation du nombre de pathogènes pour éviter les explosions de population
        return len(self.pathogens) < 100

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