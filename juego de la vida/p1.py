import tkinter as tk
from tkinter import filedialog, colorchooser
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class LifeSimulator:
    def __init__(self, master):
        self.master = master
        master.title("Autómata Celular - Life")
        
        self.cell_size = 5
        self.rows = 1000
        self.cols = 1000
        self.running = False
        self.rule_b = [3]
        self.rule_s = [2, 3]
        self.border_mode = "toroidal"  # o "nulo"

        self.grid = np.zeros((self.rows, self.cols), dtype=bool)

        self.canvas_frame = tk.Frame(master)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg='white', scrollregion=(0, 0, self.cols * self.cell_size, self.rows * self.cell_size))
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.h_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.v_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.config(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)
        self.canvas.bind("<Button-1>", self.toggle_cell)

        control_frame = tk.Frame(master)
        control_frame.pack()

        self.step_btn = tk.Button(control_frame, text="Paso", command=self.step)
        self.step_btn.pack(side=tk.LEFT)

        self.count_label = tk.Label(control_frame, text="Células vivas: 0")
        self.count_label.pack(side=tk.LEFT, padx=10)

        self.draw_grid()

    def toggle_cell(self, event):
        x = int(self.canvas.canvasx(event.x) / self.cell_size)
        y = int(self.canvas.canvasy(event.y) / self.cell_size)
        if 0 <= x < self.cols and 0 <= y < self.rows:
            self.grid[y, x] = not self.grid[y, x]
            self.draw_cell(x, y)

    def draw_grid(self):
        self.canvas.delete("cell")
        for y in range(self.rows):
            for x in range(self.cols):
                if self.grid[y, x]:
                    self.draw_cell(x, y)

    def draw_cell(self, x, y):
        x1 = x * self.cell_size
        y1 = y * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size
        color = "black" if self.grid[y, x] else "white"
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray", tags="cell")

    def step(self):
        new_grid = np.zeros_like(self.grid)
        for y in range(self.rows):
            for x in range(self.cols):
                count = self.get_neighbors(x, y)
                if self.grid[y, x]:
                    new_grid[y, x] = count in self.rule_s
                else:
                    new_grid[y, x] = count in self.rule_b
        self.grid = new_grid
        self.count_label.config(text=f"Células vivas: {np.sum(self.grid)}")
        self.draw_grid()

    def get_neighbors(self, x, y):
        total = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if self.border_mode == "toroidal":
                    nx %= self.cols
                    ny %= self.rows
                    total += self.grid[ny, nx]
                elif 0 <= nx < self.cols and 0 <= ny < self.rows:
                    total += self.grid[ny, nx]
        return total

if __name__ == "__main__":
    root = tk.Tk()
    app = LifeSimulator(root)
    root.mainloop()
