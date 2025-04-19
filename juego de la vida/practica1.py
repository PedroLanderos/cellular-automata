#Landeros Cortes Pedro Jonas
#practica 1
#automata celular


import pygame
import random
import json
import math
import matplotlib.pyplot as plt
from tkinter import filedialog, Tk

pygame.init()

BLACK = (0, 0, 0)
GREY = (50, 50, 50)
YELLOW = (255, 255, 0)

CELL_COLOR = YELLOW
BG_COLOR = GREY
WIDTH, HEIGHT = 800, 800
cellSize = 5
viewportX, viewportY = 0, 0
FPS = 60

GRID_WIDTH = 1000
GRID_HEIGHT = 1000
positions = set()
history = []
iteration = 0
ruleStr = "B3/S23"
boundary = "toro"

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

def ParseRule(rule):
    b, s = rule.split('/')
    birth = list(map(int, b[1:]))
    survive = list(map(int, s[1:]))
    return birth, survive

def GetNeighbors(pos):
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

def AdjustGrid(posSet):
    birth, survive = ParseRule(ruleStr)
    newPositions = set()
    candidates = set()
    for p in posSet:
        candidates.add(p)
        candidates.update(GetNeighbors(p))
    for cell in candidates:
        count = sum((n in posSet) for n in GetNeighbors(cell))
        if cell in posSet and count in survive:
            newPositions.add(cell)
        elif cell not in posSet and count in birth:
            newPositions.add(cell)
    return newPositions

def DrawGrid():
    for cell in positions:
        col, row = cell
        sx = (col - viewportX) * cellSize
        sy = (row - viewportY) * cellSize
        if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
            pygame.draw.rect(screen, CELL_COLOR, (sx, sy, cellSize, cellSize))

def SaveConfig():
    Tk().withdraw()
    path = filedialog.asksaveasfilename(defaultextension=".json")
    if path:
        data = {
            "positions": list(positions),
            "rule": ruleStr,
            "boundary": boundary
        }
        with open(path, 'w') as f:
            json.dump(data, f)

def LoadConfig():
    global positions, ruleStr, boundary
    Tk().withdraw()
    path = filedialog.askopenfilename()
    if path:
        with open(path) as f:
            data = json.load(f)
            positions.clear()
            positions.update(map(tuple, data["positions"]))
            ruleStr = data.get("rule", "B3/S23")
            boundary = data.get("boundary", "toro")

def PlotDensity():
    if not history:
        return
    plt.figure("Densidad")
    plt.plot(history, label="Normal")
    plt.legend()
    plt.figure("Log10")
    logHistory = [math.log10(x) if x > 0 else 0 for x in history]
    plt.plot(logHistory, label="Log10")
    plt.legend()
    plt.show()

def GenerateClusteredCells(numClusters=15, cellsPerCluster=2000, clusterRadius=30):
    positions.clear()
    for _ in range(numClusters):
        centerCol = random.randint(100, GRID_WIDTH - 100)
        centerRow = random.randint(100, GRID_HEIGHT - 100)
        for _ in range(cellsPerCluster):
            dx = random.randint(-clusterRadius, clusterRadius)
            dy = random.randint(-clusterRadius, clusterRadius)
            col = (centerCol + dx) % GRID_WIDTH
            row = (centerRow + dy) % GRID_HEIGHT
            positions.add((col, row))

def main():
    global positions, cellSize, viewportX, viewportY, CELL_COLOR, BG_COLOR
    global iteration, boundary, ruleStr

    running = True
    playing = False
    stepMode = False
    frameCounter = 0
    delayBetweenSteps = 10

    while running:
        screen.fill(BG_COLOR)
        DrawGrid()
        pygame.display.set_caption(f"Iter: {iteration}  Vivas: {len(positions)}  Rule: {ruleStr}  Boundary: {boundary}")
        pygame.display.update()

        # Obtener el estado de todas las teclas
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    col = mx // cellSize + viewportX
                    row = my // cellSize + viewportY
                    pos = (col, row)
                    if pos in positions:
                        positions.remove(pos)
                    else:
                        positions.add(pos)
                elif event.button == 4:
                    cellSize = min(10, cellSize + 1)
                elif event.button == 5:
                    cellSize = max(1, cellSize - 1)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if len(positions) == 0:
                        print("⚠ No hay celulas vivas. Presiona G para generar o dibuja una.")
                    else:
                        playing = not playing

                elif event.key == pygame.K_n:
                    stepMode = True

                elif event.key == pygame.K_c:
                    positions.clear()
                    iteration = 0
                    history.clear()

                elif event.key == pygame.K_s:
                    SaveConfig()

                elif event.key == pygame.K_l:
                    LoadConfig()

                elif event.key == pygame.K_d:
                    PlotDensity()

                elif event.key == pygame.K_r:
                    ruleStr = input("Regla B/S: (ej: B3/S23) ")

                elif event.key == pygame.K_b:
                    boundary = "nula" if boundary == "toro" else "toro"

                elif event.key == pygame.K_z:
                    cellSize = max(1, cellSize - 1)
                elif event.key == pygame.K_x:
                    cellSize = min(10, cellSize + 1)

                elif event.key == pygame.K_f:
                    CELL_COLOR = tuple(random.randint(100, 255) for _ in range(3))

                elif event.key == pygame.K_v:
                    BG_COLOR = tuple(random.randint(0, 150) for _ in range(3))

                elif event.key == pygame.K_g:
                    GenerateClusteredCells()
                    iteration = 0
                    history.clear()
                    viewportX = GRID_WIDTH // 2 - WIDTH // (2 * cellSize)
                    viewportY = GRID_HEIGHT // 2 - HEIGHT // (2 * cellSize)

        # Desplazamiento continuo con las teclas de flecha
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            viewportY = max(0, viewportY - 10)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            viewportY = min(GRID_HEIGHT - HEIGHT // cellSize, viewportY + 10)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            viewportX = max(0, viewportX - 10)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            viewportX = min(GRID_WIDTH - WIDTH // cellSize, viewportX + 10)

        if (playing and frameCounter >= delayBetweenSteps) or stepMode:
            positionsNew = AdjustGrid(positions)
            if not positionsNew:
                playing = False
                print("Todas las celulas han muerto")
            positions = positionsNew
            history.append(len(positions))
            iteration += 1
            frameCounter = 0
            stepMode = False
        else:
            frameCounter += 1

        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
