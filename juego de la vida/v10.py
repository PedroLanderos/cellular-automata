import pygame
import random
import json
import math
import matplotlib.pyplot as plt
from tkinter import filedialog, Tk

pygame.init()

# Colores
BLACK = (0, 0, 0)
GREY = (50, 50, 50)
YELLOW = (255, 255, 0)

# Config inicial
CELL_COLOR = YELLOW
BG_COLOR = GREY
WIDTH, HEIGHT = 800, 800
cell_size = 5
viewport_x, viewport_y = 0, 0
FPS = 60

# Espacio lógico
GRID_WIDTH = 1000
GRID_HEIGHT = 1000
positions = set()
history = []
iteration = 0
rule_str = "B3/S23"
boundary = "toro"

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


def parse_rule(rule):
    b, s = rule.split('/')
    birth = list(map(int, b[1:]))
    survive = list(map(int, s[1:]))
    return birth, survive


def get_neighbors(pos):
    col, row = pos
    neighbors = []
    for dc in [-1, 0, 1]:
        for dr in [-1, 0, 1]:
            if dc == 0 and dr == 0:
                continue
            nc, nr = col + dc, row + dr
            if boundary == "toro":
                nc %= GRID_WIDTH
                nr %= GRID_HEIGHT
            if 0 <= nc < GRID_WIDTH and 0 <= nr < GRID_HEIGHT:
                neighbors.append((nc, nr))
    return neighbors


def adjust_grid(pos_set):
    birth, survive = parse_rule(rule_str)
    new_positions = set()
    candidates = set()
    for p in pos_set:
        candidates.add(p)
        candidates.update(get_neighbors(p))
    for cell in candidates:
        count = sum((n in pos_set) for n in get_neighbors(cell))
        if cell in pos_set and count in survive:
            new_positions.add(cell)
        elif cell not in pos_set and count in birth:
            new_positions.add(cell)
    return new_positions


def draw_grid():
    for cell in positions:
        col, row = cell
        sx = (col - viewport_x) * cell_size
        sy = (row - viewport_y) * cell_size
        if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
            pygame.draw.rect(screen, CELL_COLOR, (sx, sy, cell_size, cell_size))


def save_config():
    Tk().withdraw()
    path = filedialog.asksaveasfilename(defaultextension=".json")
    if path:
        data = {
            "positions": list(positions),
            "rule": rule_str,
            "boundary": boundary
        }
        with open(path, 'w') as f:
            json.dump(data, f)


def load_config():
    global positions, rule_str, boundary
    Tk().withdraw()
    path = filedialog.askopenfilename()
    if path:
        with open(path) as f:
            data = json.load(f)
            positions.clear()
            positions.update(map(tuple, data["positions"]))
            rule_str = data.get("rule", "B3/S23")
            boundary = data.get("boundary", "toro")


def plot_density():
    if not history:
        return
    plt.figure("Densidad")
    plt.plot(history, label="Normal")
    plt.legend()
    plt.figure("Log10")
    log_history = [math.log10(x) if x > 0 else 0 for x in history]
    plt.plot(log_history, label="Log10")
    plt.legend()
    plt.show()


def generate_clustered_cells(num_clusters=10, cells_per_cluster=2000, cluster_radius=25):
    positions.clear()
    for _ in range(num_clusters):
        center_col = random.randint(100, GRID_WIDTH - 100)
        center_row = random.randint(100, GRID_HEIGHT - 100)
        for _ in range(cells_per_cluster):
            dx = random.randint(-cluster_radius, cluster_radius)
            dy = random.randint(-cluster_radius, cluster_radius)
            col = (center_col + dx) % GRID_WIDTH
            row = (center_row + dy) % GRID_HEIGHT
            positions.add((col, row))


def main():
    global positions, cell_size, viewport_x, viewport_y, CELL_COLOR, BG_COLOR
    global iteration, boundary, rule_str

    running = True
    playing = False
    step_mode = False
    frame_counter = 0
    delay_between_steps = 10  # mayor = más lento

    while running:
        screen.fill(BG_COLOR)
        draw_grid()
        pygame.display.set_caption(f"Iter: {iteration}  Vivas: {len(positions)}  Rule: {rule_str}  Boundary: {boundary}")
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                col = mx // cell_size + viewport_x
                row = my // cell_size + viewport_y
                pos = (col, row)
                if pos in positions:
                    positions.remove(pos)
                else:
                    positions.add(pos)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if len(positions) == 0:
                        print("⚠ No hay células vivas. Presiona G para generar o dibuja una.")
                    else:
                        playing = not playing

                elif event.key == pygame.K_n:
                    step_mode = True

                elif event.key == pygame.K_c:
                    positions.clear()
                    iteration = 0
                    history.clear()

                elif event.key == pygame.K_s:
                    save_config()

                elif event.key == pygame.K_l:
                    load_config()

                elif event.key == pygame.K_d:
                    plot_density()

                elif event.key == pygame.K_r:
                    rule_str = input("Regla B/S: (ej: B3/S23) ")

                elif event.key == pygame.K_b:
                    boundary = "nula" if boundary == "toro" else "toro"

                elif event.key == pygame.K_z:
                    cell_size = max(1, cell_size - 1)
                elif event.key == pygame.K_x:
                    cell_size = min(10, cell_size + 1)

                elif event.key == pygame.K_UP:
                    viewport_y = max(0, viewport_y - 10)
                elif event.key == pygame.K_DOWN:
                    viewport_y = min(GRID_HEIGHT - HEIGHT // cell_size, viewport_y + 10)
                elif event.key == pygame.K_LEFT:
                    viewport_x = max(0, viewport_x - 10)
                elif event.key == pygame.K_RIGHT:
                    viewport_x = min(GRID_WIDTH - WIDTH // cell_size, viewport_x + 10)

                elif event.key == pygame.K_f:
                    CELL_COLOR = tuple(random.randint(100, 255) for _ in range(3))

                elif event.key == pygame.K_v:
                    BG_COLOR = tuple(random.randint(0, 150) for _ in range(3))

                elif event.key == pygame.K_g:
                    generate_clustered_cells(num_clusters=15, cells_per_cluster=2000, cluster_radius=30)
                    iteration = 0
                    history.clear()
                    viewport_x = GRID_WIDTH // 2 - WIDTH // (2 * cell_size)
                    viewport_y = GRID_HEIGHT // 2 - HEIGHT // (2 * cell_size)

        if (playing and frame_counter >= delay_between_steps) or step_mode:
            positions_new = adjust_grid(positions)
            if not positions_new:
                playing = False
                print("⚠ Todas las células han muerto.")
            positions = positions_new
            history.append(len(positions))
            iteration += 1
            frame_counter = 0
            step_mode = False
        else:
            frame_counter += 1

        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
