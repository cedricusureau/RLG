# main.py
import pygame
import sys

from neural_battler.src.game.world import Tissue
from neural_battler.src.game.entities import ImmuneCell, Pathogen
from neural_battler.src.helper.architecture import check_and_document_architecture

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
RED = (255, 0, 0)

# Configuration de l'écran
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Neural Battler - Immune System")
clock = pygame.time.Clock()

# Police pour le texte
font = pygame.font.SysFont(None, 24)
large_font = pygame.font.SysFont(None, 72)


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

    # Calcul du temps de jeu en secondes
    game_time_seconds = tissue.game_time // 60  # à 60 FPS
    time_text = font.render(f"Temps de jeu: {game_time_seconds} s", True, (0, 0, 0))
    screen.blit(time_text, (10, 100))

    # Affichage de la fréquence d'apparition des bactéries
    spawn_rate = 60 / tissue.pathogen_spawn_timer  # Nombre de bactéries par seconde
    difficulty_text = font.render(f"Fréquence d'apparition: {spawn_rate:.2f} /s", True, (128, 0, 0))
    screen.blit(difficulty_text, (10, 130))

    if immune_count > 0:
        lt_health = tissue.immune_cells[0].health
        health_text = font.render(f"Santé du lymphocyte: {lt_health}", True, (0, 0, 128))
        screen.blit(health_text, (10, 70))

    immune_text = font.render(f"Cellules immunitaires: {immune_count}", True, (0, 0, 128))
    pathogen_text = font.render(f"Pathogènes: {pathogen_count}", True, (128, 0, 0))

    screen.blit(immune_text, (10, 10))
    screen.blit(pathogen_text, (10, 40))


def draw_game_over(screen):
    # Affiche l'écran de fin de jeu
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)  # Semi-transparent
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    game_over_text = large_font.render("GAME OVER", True, RED)
    text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(game_over_text, text_rect)

    restart_text = font.render("Appuyez sur R pour recommencer ou ESC pour quitter", True, WHITE)
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(restart_text, restart_rect)


def main():
    # Création de l'environnement
    tissue = Tissue(TISSUE_WIDTH, TISSUE_HEIGHT)

    # Ajout d'un lymphocyte T au centre
    lt = tissue.add_immune_cell(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, "t_cell")

    # Variables de contrôle du jeu
    running = True
    game_over = False

    # Boucle principale
    while running:
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    # Réinitialiser le jeu
                    tissue = Tissue(TISSUE_WIDTH, TISSUE_HEIGHT)
                    lt = tissue.add_immune_cell(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, "t_cell")
                    game_over = False

        # Vérifier si le lymphocyte est mort
        if not game_over and (not tissue.immune_cells or tissue.immune_cells[0].is_dead()):
            game_over = True

        # Mise à jour de l'état du jeu seulement si le jeu n'est pas terminé
        if not game_over:
            tissue.update()

        # Rendu
        screen.fill(WHITE)
        draw_grid(screen)
        tissue.draw(screen)
        draw_stats(screen, tissue)

        # Afficher l'écran de fin de jeu si nécessaire
        if game_over:
            draw_game_over(screen)

        # Mise à jour de l'affichage
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    check_and_document_architecture()
    main()