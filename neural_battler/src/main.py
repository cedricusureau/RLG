# src/main.py
import pygame
import sys
import argparse

# Imports relatifs à la position du fichier
from .game import Tissue
from .helper.architecture import check_and_document_architecture

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


def draw_grid(screen, cell_size=50):
    # Dessine une grille de référence
    for x in range(0, SCREEN_WIDTH, cell_size):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, cell_size):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))


def draw_stats(screen, tissue, font, survival_time=None, steps_survived=None):
    # Affiche des statistiques sur l'écran
    immune_count = len(tissue.immune_cells)
    pathogen_count = len(tissue.pathogens)

    if immune_count > 0:
        lt_health = tissue.immune_cells[0].health
        health_text = font.render(f"Santé du lymphocyte: {lt_health}", True, (0, 0, 128))
        screen.blit(health_text, (10, 70))

    immune_text = font.render(f"Cellules immunitaires: {immune_count}", True, (0, 0, 128))
    pathogen_text = font.render(f"Pathogènes: {pathogen_count}", True, (128, 0, 0))

    screen.blit(immune_text, (10, 10))
    screen.blit(pathogen_text, (10, 40))

    # Afficher le temps de survie si fourni (pour le mode IA)
    if survival_time is not None:
        time_text = font.render(f"Temps de survie: {survival_time:.1f}s", True, (0, 100, 0))
        screen.blit(time_text, (10, 100))

    if steps_survived is not None:
        steps_text = font.render(f"Pas: {steps_survived}", True, (0, 100, 0))
        screen.blit(steps_text, (10, 130))


def draw_game_over(screen):
    # Affiche l'écran de fin de jeu
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)  # Semi-transparent
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    large_font = pygame.font.SysFont(None, 72)
    font = pygame.font.SysFont(None, 24)

    game_over_text = large_font.render("GAME OVER", True, RED)
    text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(game_over_text, text_rect)

    restart_text = font.render("Appuyez sur R pour recommencer ou ESC pour quitter", True, WHITE)
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(restart_text, restart_rect)


def spawn_random_pathogen(tissue):
    """Génère un nouveau pathogène à une position aléatoire"""
    import random
    margin = 50  # Pour éviter de spawner trop près des bords
    x = random.uniform(margin, tissue.width - margin)
    y = random.uniform(margin, tissue.height - margin)
    return tissue.add_pathogen(x, y, "bacteria")


def main(model_path=None):
    # Configuration de l'écran
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    caption = "Neural Battler - AI Lymphocyte" if model_path else "Neural Battler - Immune System"
    pygame.display.set_caption(caption)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    # Création de l'environnement
    tissue = Tissue(TISSUE_WIDTH, TISSUE_HEIGHT)

    # Ajout d'un lymphocyte T au centre (avec ou sans IA)
    lt = tissue.add_immune_cell(TISSUE_WIDTH / 2, TISSUE_HEIGHT / 2, "t_cell", model_path)

    # Génération de pathogènes initiaux
    for _ in range(5):
        spawn_random_pathogen(tissue)

    # Variables pour le suivi de la survie
    steps_survived = 0
    survival_time = 0
    spawn_timer = 0
    game_over = False

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
                elif event.key == pygame.K_r and game_over:
                    # Réinitialiser le jeu
                    tissue = Tissue(TISSUE_WIDTH, TISSUE_HEIGHT)
                    lt = tissue.add_immune_cell(TISSUE_WIDTH / 2, TISSUE_HEIGHT / 2, "t_cell", model_path)
                    for _ in range(5):
                        spawn_random_pathogen(tissue)
                    steps_survived = 0
                    survival_time = 0
                    spawn_timer = 0
                    game_over = False

        # Vérifier si le lymphocyte est mort
        if not game_over and (not tissue.immune_cells or tissue.immune_cells[0].is_dead()):
            game_over = True

        if not game_over:
            # Mode manuel (contrôle clavier) si le lymphocyte n'est pas contrôlé par IA
            if not model_path:
                keys = pygame.key.get_pressed()
                move_x, move_y = 0, 0

                if keys[pygame.K_UP]:
                    move_y -= lt.speed if hasattr(lt, 'speed') else 1.0
                if keys[pygame.K_DOWN]:
                    move_y += lt.speed if hasattr(lt, 'speed') else 1.0
                if keys[pygame.K_LEFT]:
                    move_x -= lt.speed if hasattr(lt, 'speed') else 1.0
                if keys[pygame.K_RIGHT]:
                    move_x += lt.speed if hasattr(lt, 'speed') else 1.0

                # Appliquer le mouvement
                new_x = lt.x + move_x
                new_y = lt.y + move_y

                if tissue.is_valid_position(new_x, new_y):
                    lt.x = new_x
                    lt.y = new_y

            # Mise à jour de l'état du jeu
            tissue.update()

            # Génération périodique de nouveaux pathogènes
            spawn_timer += 1
            if spawn_timer >= 180:  # Toutes les ~3 secondes (à 60 FPS)
                spawn_random_pathogen(tissue)
                spawn_timer = 0

            # Mise à jour des compteurs de survie
            if not lt.is_dead():
                steps_survived += 1
                survival_time += 1 / FPS

        # Rendu
        screen.fill(WHITE)
        draw_grid(screen)
        tissue.draw(screen)
        draw_stats(screen, tissue, font, survival_time, steps_survived)

        # Afficher l'écran de fin de jeu si nécessaire
        if game_over:
            draw_game_over(screen)

        # Mise à jour de l'affichage
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    print(f"Fin de la simulation. Survie: {survival_time:.1f} secondes, {steps_survived} pas.")
    return survival_time, steps_survived


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Neural Battler")
    parser.add_argument("--model", type=str, default=None,
                        help="Chemin vers le modèle d'IA à utiliser (facultatif)")

    args = parser.parse_args()
    check_and_document_architecture()

    if args.model:
        print(f"Utilisation du modèle: {args.model}")
    else:
        print("Mode manuel activé (aucun modèle spécifié)")

    main(args.model)