import pygame
import random
import time
import csv
from collections import deque

# Initialisation de Pygame
pygame.init()

# Dimensions de l'écran
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
GRID_SIZE = 3  # 3x3 pour le 8-puzzle, 4x4 pour le 15-puzzle
TILE_SIZE = SCREEN_WIDTH // GRID_SIZE

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 149, 237)

# Création de la fenêtre
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Puzzle à glissements")

# Génération du puzzle
def generate_puzzle(grid_size):
    tiles = list(range(1, grid_size**2)) + [0]
    random.shuffle(tiles)
    return [tiles[i:i + grid_size] for i in range(0, len(tiles), grid_size)]

# Trouver la position de la case vide (valeur 0)
def find_empty_tile(grid):
    for row in range(len(grid)):
        for col in range(len(grid[row])):
            if grid[row][col] == 0:
                return row, col

# Dessin du puzzle sur l'écran
def draw_puzzle(grid):
    screen.fill(WHITE)
    font = pygame.font.Font(None, 60)
    for row in range(len(grid)):
        for col in range(len(grid[row])):
            value = grid[row][col]
            if value != 0:  # Ignorer la case vide
                pygame.draw.rect(screen, BLUE, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                text = font.render(str(value), True, WHITE)
                text_rect = text.get_rect(center=(col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE + TILE_SIZE // 2))
                screen.blit(text, text_rect)
            pygame.draw.rect(screen, BLACK, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)

# Vérification de victoire
def is_solved(grid):
    n = len(grid)
    correct = list(range(1, n**2)) + [0]
    flat_grid = [tile for row in grid for tile in row]
    return flat_grid == correct

# Déplacement des tuiles
def move_tile(grid, direction):
    empty_row, empty_col = find_empty_tile(grid)
    target_row, target_col = empty_row, empty_col
    if direction == "UP" and empty_row > 0:
        target_row -= 1
    elif direction == "DOWN" and empty_row < len(grid) - 1:
        target_row += 1
    elif direction == "LEFT" and empty_col > 0:
        target_col -= 1
    elif direction == "RIGHT" and empty_col < len(grid[0]) - 1:
        target_col += 1
    if target_row != empty_row or target_col != empty_col:
        grid[empty_row][empty_col], grid[target_row][target_col] = grid[target_row][target_col], grid[empty_row][empty_col]

# Générer tous les mouvements possibles à partir d'un état donné
def generate_moves(grid):
    moves = []
    empty_row, empty_col = find_empty_tile(grid)
    if empty_row > 0:
        moves.append(("UP", empty_row - 1, empty_col))
    if empty_row < len(grid) - 1:
        moves.append(("DOWN", empty_row + 1, empty_col))
    if empty_col > 0:
        moves.append(("LEFT", empty_row, empty_col - 1))
    if empty_col < len(grid[0]) - 1:
        moves.append(("RIGHT", empty_row, empty_col + 1))
    return moves

# Recherche en largeur (BFS) pour résoudre le puzzle
def solve_puzzle(grid):
    queue = deque([(grid, [])])
    visited = set()
    while queue:
        current_grid, path = queue.popleft()
        if is_solved(current_grid):
            return path
        for direction, target_row, target_col in generate_moves(current_grid):
            new_grid = [row[:] for row in current_grid]
            empty_row, empty_col = find_empty_tile(new_grid)
            new_grid[empty_row][empty_col], new_grid[target_row][target_col] = new_grid[target_row][target_col], new_grid[empty_row][empty_col]
            flat_grid = tuple(tuple(row) for row in new_grid)
            if flat_grid not in visited:
                visited.add(flat_grid)
                queue.append((new_grid, path + [direction]))
    return []

# Enregistrer les résultats dans un fichier CSV
def save_results(filename, results):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Time", "Moves", "Success"])
        writer.writerows(results)

# Boucle principale du jeu
def main():
    grid = generate_puzzle(GRID_SIZE)
    clock = pygame.time.Clock()
    running = True
    auto_solve = False
    results = []

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    move_tile(grid, "UP")
                elif event.key == pygame.K_DOWN:
                    move_tile(grid, "DOWN")
                elif event.key == pygame.K_LEFT:
                    move_tile(grid, "LEFT")
                elif event.key == pygame.K_RIGHT:
                    move_tile(grid, "RIGHT")
                elif event.key == pygame.K_s:
                    auto_solve = True

        if auto_solve:
            start_time = time.time()
            solution = solve_puzzle(grid)
            end_time = time.time()
            elapsed_time = end_time - start_time
            success = is_solved(grid)
            results.append([elapsed_time, len(solution), success])
            for move in solution:
                move_tile(grid, move)
                draw_puzzle(grid)
                pygame.display.flip()
                pygame.time.wait(500)  # Attendre 500 ms entre chaque mouvement
            auto_solve = False
            save_results("results.csv", results)

        draw_puzzle(grid)
        pygame.display.flip()

        if is_solved(grid):
            print("Félicitations, vous avez résolu le puzzle !")
            running = False

        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
