from tkinter import Tk, StringVar, Label, Button, OptionMenu
from pyamaze import maze, agent, COLOR, textLabel
from bfs_solver import solve_bfs
from dfs_solver import solve_dfs


def path_to_trace(path):
    if not path:
        return {}

    trace = {}
    for i in range(len(path) - 1):
        trace[path[i]] = path[i + 1]
    return trace


def launch_maze(algorithm):
    m = maze(20, 30)
    m.CreateMaze(1, 30, loopPercent=30)

    if algorithm == "BFS":
        path, visited_count, runtime, search_order = solve_bfs(m)
        color = COLOR.cyan
    else:
        path, visited_count, runtime, search_order = solve_dfs(m)
        color = COLOR.yellow

    textLabel(m, "Algorithm", algorithm)

    if path is None:
        textLabel(m, "Result", "No Path Found")
        textLabel(m, "Visited Cells", visited_count)
        textLabel(m, "Runtime", round(runtime, 6))
    else:
        textLabel(m, "Path Length", len(path) - 1)
        textLabel(m, "Visited Cells", visited_count)
        textLabel(m, "Runtime", round(runtime, 6))

        search_agent = agent(m,footprints=True,color=COLOR.yellow, filled=True)

        final_agent = agent(m, footprints=True, color=COLOR.cyan, filled=True)

        m.tracePath({search_agent:search_order}, delay= 55)

        m.tracePath({final_agent:path_to_trace(path)}, delay= 80)

    m._win.title(f"{algorithm} Maze Solver")
    m.run()


def solve_and_open():
    algorithm = selected_algorithm.get()
    menu.destroy()
    launch_maze(algorithm)


menu = Tk()
menu.title("Maze Solver Menu")
menu.geometry("250x150")

selected_algorithm = StringVar()
selected_algorithm.set("BFS")

Label(menu, text="Choose Algorithm:").pack(pady=10)

OptionMenu(menu, selected_algorithm, "BFS", "DFS").pack(pady=5)

Button(menu, text="Solve", command=solve_and_open).pack(pady=15)

menu.mainloop()