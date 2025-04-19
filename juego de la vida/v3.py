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
WHITE = (255, 255, 255)

# Config inicial
CELL_COLOR = YELLOW
BG_COLOR = GREY
WIDTH, HEIGHT = 800, 800
cell_size = 5  # Zoom: de 1 a 10
viewport_x, viewport_y = 0, 0
FPS = 60

# Espacio lógico de la grilla (puede ser muy grande)
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
    birth, survive = [], []
    b, s = rule.split('/')
    birth = list(map(int, b[1:]))
    survive = list(map(int, s[1:]))
    return birth, survive


def get_neighbors(pos):
    x, y = pos
    neighbors = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if boundary == "toro":
                nx %= GRID_WIDTH
                ny %= GRID_HEIGHT
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                neighbors.append((nx, ny))
    return neighbors


def adjust_grid(pos_set):
    birth, survive = parse_rule(rule_str)
    new_positions = set()
    candidates = pos_set.copy()
    for p in pos_set:
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
        x, y = cell
        sx = (x - viewport_x) * cell_size
        sy = (y - viewport_y) * cell_size
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
            positions = set(map(tuple, data["positions"]))
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


def main():
    global positions, cell_size, viewport_x, viewport_y, CELL_COLOR, BG_COLOR
    global iteration, boundary, rule_str

    running = True
    playing = False
    step_mode = False

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
                x = mx // cell_size + viewport_x
                y = my // cell_size + viewport_y
                pos = (x, y)
                if pos in positions:
                    positions.remove(pos)
                else:
                    positions.add(pos)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
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
                    viewport_y = min(GRID_HEIGHT, viewport_y + 10)
                elif event.key == pygame.K_LEFT:
                    viewport_x = max(0, viewport_x - 10)
                elif event.key == pygame.K_RIGHT:
                    viewport_x = min(GRID_WIDTH, viewport_x + 10)

                elif event.key == pygame.K_f:
                    CELL_COLOR = tuple(random.randint(100, 255) for _ in range(3))
                elif event.key == pygame.K_b:
                    BG_COLOR = tuple(random.randint(0, 150) for _ in range(3))

        if playing or step_mode:
            positions = adjust_grid(positions)
            history.append(len(positions))
            iteration += 1
            step_mode = False

        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()