# neural_battler/src/main_ai.py
import pygame
import sys
import os
import argparse

from neural_battler.src.game.world import Tissue
from neural_battler.src.ai.inference.immune_cell_controller import ImmuneCellController
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


def draw_grid(screen, cell_size=50):
    # Dessine une grille de référence
    for x in range(0, SCREEN_WIDTH, cell_size):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, cell_size):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))


def draw_stats(screen, tissue, font, survival_time, steps_survived):
    # Affiche des statistiques sur l'écran
    immune_count = len(tissue.immune_cells)
    pathogen_count = len(tissue.pathogens)

    immune_text = font.render(f"Cellules immunitaires: {immune_count}", True, (0, 0, 128))
    pathogen_text = font.render(f"Pathogènes: {pathogen_count}", True, (128, 0, 0))
    time_text = font.render(f"Temps de survie: {survival_time:.1f}s", True, (0, 100, 0))
    steps_text = font.render(f"Pas: {steps_survived}", True, (0, 100, 0))

    screen.blit(immune_text, (10, 10))
    screen.blit(pathogen_text, (10, 40))
    screen.blit(time_text, (10, 70))
    screen.blit(steps_text, (10, 100))


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
    pygame.display.set_caption("Neural Battler - AI Lymphocyte")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    # Création de l'environnement
    tissue = Tissue(TISSUE_WIDTH, TISSUE_HEIGHT)

    # Ajout d'un lymphocyte T
    lt = tissue.add_immune_cell(TISSUE_WIDTH / 2, TISSUE_HEIGHT / 2, "t_cell")

    # Génération de pathogènes initiaux
    for _ in range(5):
        spawn_random_pathogen(tissue)

    # Chargement du contrôleur AI si un modèle est spécifié
    controller = None
    if model_path and os.path.exists(model_path):
        print(f"Chargement du modèle AI: {model_path}")
        controller = ImmuneCellController(model_path)
    else:
        print("Mode manuel: utilisez les flèches pour contrôler le lymphocyte")

    # Variables pour le suivi de la survie
    steps_survived = 0
    survival_time = 0
    spawn_timer = 0

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

        # Mode manuel (contrôle clavier) si pas de contrôleur AI
        if not controller:
            keys = pygame.key.get_pressed()
            move_x, move_y = 0, 0

            if keys[pygame.K_UP]:
                move_y -= lt.speed
            if keys[pygame.K_DOWN]:
                move_y += lt.speed
            if keys[pygame.K_LEFT]:
                move_x -= lt.speed
            if keys[pygame.K_RIGHT]:
                move_x += lt.speed

            # Appliquer le mouvement
            new_x = lt.x + move_x
            new_y = lt.y + move_y

            if tissue.is_valid_position(new_x, new_y):
                lt.x = new_x
                lt.y = new_y
        else:
            # Mode AI: le contrôleur gère le lymphocyte
            controller.update(lt, tissue.pathogens, tissue)

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

        # Mise à jour de l'affichage
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    print(f"Fin de la simulation. Survie: {survival_time:.1f} secondes, {steps_survived} pas.")
    return survival_time, steps_survived


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Démarrer le jeu avec un modèle AI")
    parser.add_argument("--model", type=str, default=None,
                        help="Chemin vers le modèle d'IA à utiliser (facultatif)")

    args = parser.parse_args()
    check_and_document_architecture()

    if args.model:
        print(f"Utilisation du modèle: {args.model}")
    else:
        print("Mode manuel activé (aucun modèle spécifié)")

    main(args.model)