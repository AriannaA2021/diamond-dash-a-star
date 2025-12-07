# Diamond Dash by Analiese Gonzalez, Arianna Azcarraga, and Joshua Park
import pygame
import random  
import heapq
import sys
from typing import List, Tuple, Optional, Set

# constants for game
GRID_SIZE = 16
TILE_SIZE = 40
WINDOW_SIZE = GRID_SIZE * TILE_SIZE
FPS = 60
GAME_TIMER = 120

# colors for game
PLAYER_COLOR = (50, 200, 50)
DIAMOND_COLOR = (0, 200, 255)
GRID_COLOR = (50,50,50)
BACKGROUND_COLOR = (20, 20, 20)
TEXT_COLOR = (230, 230, 230)
LOST_COLOR = (220, 60, 60)
WIN_COLOR = (60, 220, 120)
EXIT_COLOR = (255, 215, 0)
OPP_COLOR = (220, 50, 50)

# directions for movement
DIRECTIONS = {pygame.K_UP: (0, -1),
              pygame.K_DOWN: (0, 1),
              pygame.K_LEFT: (-1, 0),
              pygame.K_RIGHT: (1, 0)}
Position = Tuple[int, int]

# A* pathfinding node
def heuristic(a: Position, b: Position) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_neighbors(pos: Position) -> List[Position]:
    neighbors = []
    for direction in DIRECTIONS.values():
        neighbor = (pos[0] + direction[0], pos[1] + direction[1])
        if 0 <= neighbor[0] < GRID_SIZE and 0 <= neighbor[1] < GRID_SIZE:
            neighbors.append(neighbor)
    return neighbors

def astar(start: Position, goal: Position) -> Optional[List[Position]]:
    if start == goal:
        return [start]
    
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            path = [current]
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]

        for direction in DIRECTIONS.values():
            neighbor = (current[0] + direction[0], current[1] + direction[1])
            if 0 <= neighbor[0] < GRID_SIZE and 0 <= neighbor[1] < GRID_SIZE:
                tentative_g_score = g_score[current] + 1
                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    if neighbor not in [i[1] for i in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return None

# setting up game
def empty_position(exclude: Set[Position]) -> Position:
    while True:
        pos = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
        if pos not in exclude:
            return pos
        
def setup_game():   #sets up initial positions for player, opponent, exit, and diamonds
    player_pos: Position = (0, 0)
    opp_pos: Position = (GRID_SIZE - 1, GRID_SIZE - 1)
    used = {player_pos, opp_pos}
    exit_pos = empty_position(used)
    used.add(exit_pos)  
    diamonds: Set[Position] = set()

    #places 3 diamonds
    for _ in range(3):  
        diamond_pos = empty_position(used)
        diamonds.add(diamond_pos)
        used.add(diamond_pos)
    return player_pos, opp_pos, exit_pos, diamonds