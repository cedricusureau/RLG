# main.py
import pygame
import sys
from game.world.tissue import Tissue
from game.entities.immune_cell import ImmuneCell
from game.entities.pathogen import Pathogen
from helper.architecture import check_and_document_architecture

# Initialisation de Pygame
pygame.init()

# Constantes
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TISSUE_WIDTH = 800
TISSUE_HEIGHT = 600
FPS = 60

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRID_COLOR = (200, 200, 220)

# Configuration de l'écran
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Neural Battler - Immune System")
clock = pygame.time.Clock()

# Police pour le texte
font = pygame.font.SysFont(None, 24)


def draw_grid(screen, cell_size=50):
    # Dessine une grille de référence
    for x in range(0, SCREEN_WIDTH, cell_size):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, cell_size):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))


def draw_stats(screen, tissue):
    # Affiche des statistiques sur l'écran
    immune_count = len(tissue.immune_cells)
    pathogen_count = len(tissue.pathogens)

    immune_text = font.render(f"Cellules immunitaires: {immune_count}", True, (0, 0, 128))
    pathogen_text = font.render(f"Pathogènes: {pathogen_count}", True, (128, 0, 0))

    screen.blit(immune_text, (10, 10))
    screen.blit(pathogen_text, (10, 40))


def main():
    # Création de l'environnement
    tissue = Tissue(TISSUE_WIDTH, TISSUE_HEIGHT)

    # Ajout d'un seul lymphocyte T
    lt = tissue.add_immune_cell(200, 300, "t_cell")

    # Ajout d'une seule bactérie
    bacteria = tissue.add_pathogen(600, 300, "bacteria")

    # Boucle principale
    running = True
    while running:
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Mise à jour de l'état du jeu
        tissue.update()

        # Rendu
        screen.fill(WHITE)
        draw_grid(screen)
        tissue.draw(screen)
        draw_stats(screen, tissue)

        # Mise à jour de l'affichage
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    check_and_document_architecture()
    main()