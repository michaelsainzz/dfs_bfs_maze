from collections import deque
import time

def solve_bfs(m, start=None):
    if start is None:
        start = (m.rows, m.cols)

    start_time = time.time()

    frontier = deque([start])
    parent = {}
    visited = {start}
    search_order = []

    found = False

    while frontier:
        curr = frontier.popleft()
        search_order.append(curr)

        if curr == m._goal:
            found = True
            break

        for d in "ESNW":
            if m.maze_map[curr][d]:
                if d == "E":
                    nxt = (curr[0], curr[1] + 1)
                elif d == "W":
                    nxt = (curr[0], curr[1] - 1)
                elif d == "N":
                    nxt = (curr[0] - 1, curr[1])
                else:
                    nxt = (curr[0] + 1, curr[1])

                if nxt not in visited:
                    visited.add(nxt)
                    parent[nxt] = curr
                    frontier.append(nxt)

    runtime = time.time() - start_time

    if not found:
        return None, len(visited), runtime, search_order

    path = []
    cell = m._goal
    while cell != start:
        path.append(cell)
        cell = parent[cell]
    path.append(start)
    path.reverse()

    return path, len(visited), runtime, search_order