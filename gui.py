import random
from tkinter import Tk, StringVar, Label, Button, OptionMenu, Canvas, Frame
from bfs_solver import solve_bfs
from dfs_solver import solve_dfs

CELL   = 25
MARGIN = 20
ROWS   = 20
COLS   = 30


# --- Maze generator (same maze_map format as pyamaze, no extra window) ---
class MazeData:
    def __init__(self, rows, cols):
        self.rows  = rows
        self.cols  = cols
        self._goal = (1, cols)
        self.maze_map = {
            (r, c): {'N': False, 'S': False, 'E': False, 'W': False}
            for r in range(1, rows + 1)
            for c in range(1, cols + 1)
        }
        self._carve(rows, cols)

    def _carve(self, start_r, start_c):
        visited = set()
        stack   = [(start_r, start_c)]
        visited.add((start_r, start_c))
        dirs = [('N', -1, 0, 'S'), ('S', 1, 0, 'N'),
                ('E', 0, 1, 'W'),  ('W', 0, -1, 'E')]
        while stack:
            r, c = stack[-1]
            neighbors = [
                (r + dr, c + dc, d, rd)
                for d, dr, dc, rd in dirs
                if 1 <= r + dr <= self.rows
                and 1 <= c + dc <= self.cols
                and (r + dr, c + dc) not in visited
            ]
            if neighbors:
                nr, nc, d, rd = random.choice(neighbors)
                self.maze_map[(r,  c )][d]  = True
                self.maze_map[(nr, nc)][rd] = True
                visited.add((nr, nc))
                stack.append((nr, nc))
            else:
                stack.pop()


# --- Main window ---
root = Tk()
root.title("Maze Solver")

# --- Controls ---
controls = Frame(root)
controls.pack(side='top', pady=5)

Label(controls, text="Algorithm:").pack(side='left', padx=5)
selected = StringVar(value="BFS")
OptionMenu(controls, selected, "BFS", "DFS").pack(side='left', padx=5)
solve_btn = Button(controls, text="Solve")
solve_btn.pack(side='left', padx=5)
new_btn = Button(controls, text="New Maze")
new_btn.pack(side='left', padx=5)

# --- Stats label ---
stats_var = StringVar(value="Select an algorithm and click Solve")
Label(root, textvariable=stats_var, font=('Arial', 10)).pack(side='top', pady=3)

# --- Canvas ---
BG    = '#1e1e1e'
WALL  = 'white'
GAP   = BG       # color shown between colored blocks

canvas = Canvas(root,
                width=COLS * CELL + 2 * MARGIN,
                height=ROWS * CELL + 2 * MARGIN,
                bg=BG)
canvas.pack(padx=10, pady=10)

state = {'maze': None}


def cell_xy(r, c):
    return MARGIN + (c - 1) * CELL, MARGIN + (r - 1) * CELL


# Each internal wall is drawn exactly once and tagged uniquely.
# Horizontal walls (between row r and r+1) → tag  h_{r}_{c}
# Vertical   walls (between col c and c+1) → tag  v_{r}_{c}

def draw_walls(m):
    canvas.delete('wall')
    # Outer border
    x0, y0 = cell_xy(1, 1)
    x1, y1 = cell_xy(ROWS, COLS)
    canvas.create_rectangle(x0, y0, x1 + CELL, y1 + CELL,
                             outline=WALL, width=3, tags='wall')
    # Internal walls
    for r in range(1, ROWS + 1):
        for c in range(1, COLS + 1):
            x, y = cell_xy(r, c)
            cm = m.maze_map[(r, c)]
            # South wall shared with north of (r+1, c)
            if r < ROWS and not cm['S']:
                canvas.create_line(x, y + CELL, x + CELL, y + CELL,
                                   fill=WALL, width=3, tags=('wall', f'h_{r}_{c}'))
            # East wall shared with west of (r, c+1)
            if c < COLS and not cm['E']:
                canvas.create_line(x + CELL, y, x + CELL, y + CELL,
                                   fill=WALL, width=3, tags=('wall', f'v_{r}_{c}'))


def mark_cell(r, c, color, text):
    x, y = cell_xy(r, c)
    canvas.create_rectangle(x + 2, y + 2, x + CELL - 2, y + CELL - 2,
                             fill=color, outline='', tags='marker')
    canvas.create_text(x + CELL // 2, y + CELL // 2,
                       text=text, fill='white', font=('Arial', 8, 'bold'), tags='marker')


def color_cell(r, c, color):
    x, y = cell_xy(r, c)
    m = state['maze']
    cm = m.maze_map[(r, c)]

    canvas.create_rectangle(x, y, x + CELL, y + CELL,
                             fill=color, outline='')

    canvas.tag_raise('wall')
    canvas.tag_raise('marker')


def draw_maze_on_canvas(m):
    canvas.delete("all")
    draw_walls(m)
    mark_cell(ROWS, COLS, 'green', 'S')
    mark_cell(*m._goal, 'red', 'E')


def generate_new_maze():
    state['maze'] = MazeData(ROWS, COLS)
    draw_maze_on_canvas(state['maze'])
    stats_var.set("Select an algorithm and click Solve")
    solve_btn.config(state='normal')
    new_btn.config(state='normal')


def animate(cells, color, delay, on_done):
    start = (ROWS, COLS)
    goal  = state['maze']._goal
    idx   = [0]

    def step():
        if idx[0] < len(cells):
            r, c = cells[idx[0]]
            if (r, c) != start and (r, c) != goal:
                color_cell(r, c, color)
            idx[0] += 1
            canvas.after(delay, step)
        else:
            on_done()

    step()


def solve():
    m = state['maze']
    if m is None:
        return

    solve_btn.config(state='disabled')
    new_btn.config(state='disabled')
    algorithm = selected.get()

    if algorithm == "BFS":
        path, visited_count, runtime, search_order = solve_bfs(m)
    else:
        path, visited_count, runtime, search_order = solve_dfs(m)

    draw_maze_on_canvas(m)

    if path is None:
        stats_var.set(
            f"{algorithm}  |  No Path Found  |  "
            f"Visited: {visited_count}  |  Time: {runtime:.6f}s"
        )
        solve_btn.config(state='normal')
        new_btn.config(state='normal')
        return

    stats_var.set(
        f"{algorithm}  |  Path: {len(path) - 1} steps  |  "
        f"Visited: {visited_count}  |  Time: {runtime:.6f}s"
    )

    def show_path():
        def done():
            mark_cell(ROWS, COLS, 'green', 'S')
            mark_cell(*m._goal, 'red', 'E')
            solve_btn.config(state='normal')
            new_btn.config(state='normal')
        animate(path, '#00FFFF', 80, done)

    animate(search_order, '#FFD700', 20, show_path)


solve_btn.config(command=solve)
new_btn.config(command=generate_new_maze)

generate_new_maze()
root.mainloop()
