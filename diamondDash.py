# Diamond Dash by Analiese Gonzalez, Arianna Azcarraga, and Joshua Park
import pygame
import random  
import heapq
import sys
import math
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
def heuristic(a: Position, b: Position) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])

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
                current = came_from[current]
                path.append(current)
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

    # places 3 diamonds
    for _ in range(3):  
        diamond_pos = empty_position(used)
        diamonds.add(diamond_pos)
        used.add(diamond_pos)
    return player_pos, opp_pos, exit_pos, diamonds

def grid(surface: pygame.Surface):
    for x in range(0, WINDOW_SIZE, TILE_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, WINDOW_SIZE))
    for y in range(0, WINDOW_SIZE, TILE_SIZE):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (WINDOW_SIZE, y))

def tiles(surface: pygame.Surface, positions: Set[Position], color: Tuple[int, int, int], padding: int = 4):
    for x, y in positions:
        rect = pygame.Rect(
            x * TILE_SIZE + padding,
            y * TILE_SIZE + padding,
            TILE_SIZE - 2 * padding,
            TILE_SIZE - 2 * padding,
        )
        pygame.draw.rect(surface, color, rect, border_radius=4)

def draw_path(surface: pygame.Surface, path: List[Position], color: Tuple[int, int, int], alpha: int = 128, width: int = 2):
    """
    Draw a path as lines connecting consecutive positions.
    """
    if not path or len(path) < 2:
        return
    
    #reate a temporary surface for the path with alpha support
    path_surface = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
    
    # Draw lines between consecutive path nodes
    for i in range(len(path) - 1):
        start_pos = path[i]
        end_pos = path[i + 1]
        
        # Convert grid positions to pixel coordinates (center of tiles)
        start_pixel = (start_pos[0] * TILE_SIZE + TILE_SIZE // 2, 
                       start_pos[1] * TILE_SIZE + TILE_SIZE // 2)
        end_pixel = (end_pos[0] * TILE_SIZE + TILE_SIZE // 2,
                     end_pos[1] * TILE_SIZE + TILE_SIZE // 2)
        
        # Draw line with alpha
        pygame.draw.line(path_surface, (*color, alpha), start_pixel, end_pixel, width)
    surface.blit(path_surface, (0, 0))

def draw_game(surface: pygame.Surface, player_pos: Position, opp_pos: Position, exit_pos: Position, diamonds: Set[Position], font: pygame.font.Font, score: int, time_left: int, game_over: bool, win: bool, opp_path: Optional[List[Position]] = None):
    surface.fill(BACKGROUND_COLOR)
    grid(surface)
    
    # Draw opponent path
    if opp_path and not game_over:
        draw_path(surface, opp_path, (220, 50, 50), alpha=150, width=2)
    
    tiles(surface, {exit_pos}, EXIT_COLOR)
    tiles(surface, diamonds, DIAMOND_COLOR)
    tiles(surface, {player_pos}, PLAYER_COLOR)
    tiles(surface, {opp_pos}, OPP_COLOR)

    score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
    time_text = font.render(f"Time: {time_left}", True, TEXT_COLOR)
    # blunders_text = font.render(f"Blunders: {blunders}", True, TEXT_COLOR)
    
    surface.blit(score_text, (10, 10))
    surface.blit(time_text, (WINDOW_SIZE - time_text.get_width() - 10, 10))
    # surface.blit(blunders_text, (10, WINDOW_SIZE - blunders_text.get_height() - 10))


    if game_over:
        overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
        overlay.set_alpha(200)
        overlay.fill(BACKGROUND_COLOR)
        surface.blit(overlay, (0, 0))
        if win:
            msg = "You Win!"
            color = WIN_COLOR
        else:
            msg = "Game Over!"
            color = LOST_COLOR
        msg_text = font.render(msg, True, color)
        surface.blit(msg_text, ((WINDOW_SIZE - msg_text.get_width()) // 2, (WINDOW_SIZE - msg_text.get_height()) // 2))

def player_move(player_pos: Position, direction: Tuple[int, int]) -> Position:
    new_x = max(0, min(GRID_SIZE - 1, player_pos[0] + direction[0]))
    new_y = max(0, min(GRID_SIZE - 1, player_pos[1] + direction[1]))
    return (new_x, new_y)

def opponent_move(opp_pos: Position, player_pos: Position) -> Position:
    path = astar(opp_pos, player_pos)
    if path and len(path) > 1:
        return path[1]
    return opp_pos

def get_optimal_next_step(player_pos: Position, diamonds: Set[Position], exit_pos: Position) -> Optional[Position]:
    """
    Find the optimal next step toward the nearest goal (diamond or exit).
    """
    # Determine the current goal: nearest diamond if any remain, otherwise exit
    if diamonds:
        # Find nearest diamond
        nearest_diamond = None
        min_distance = float('inf')
        for diamond in diamonds:
            distance = heuristic(player_pos, diamond)
            if distance < min_distance:
                min_distance = distance
                nearest_diamond = diamond
        
        if nearest_diamond:
            path = astar(player_pos, nearest_diamond)
            if path and len(path) > 1:
                return path[1]  # Return next step in path
    else:
        # All diamonds collected, go to exit
        path = astar(player_pos, exit_pos)
        if path and len(path) > 1:
            return path[1]  # Return next step in path
    
    return None

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("Diamond Dash")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    player_pos, opp_pos, exit_pos, diamonds = setup_game()
    score = 0
    start_ticks = pygame.time.get_ticks()
    game_over = False
    win = False
    player_moved = False
    
    # Blunders tracking
    # blunders = 0
    
    while True:
        dt = clock.tick(FPS) / 1000
        time_left = GAME_TIMER - (pygame.time.get_ticks() - start_ticks) // 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and not game_over:
                if event.key in DIRECTIONS:
                    # Get optimal next step before player moves
                    optimal_next = get_optimal_next_step(player_pos, diamonds, exit_pos)
                    
                    # Move player
                    new_player_pos = player_move(player_pos, DIRECTIONS[event.key])
                    
                    # Check if move is a blunder (doesn't match optimal)
                    # if optimal_next and new_player_pos != optimal_next:
                    #     blunders += 1
                    
                    player_pos = new_player_pos
                    player_moved = True

        if not game_over:
            if player_moved:  #only move opponent if player has moved
                opp_pos = opponent_move(opp_pos, player_pos)
                player_moved = False
            if player_pos in diamonds:
                diamonds.remove(player_pos)
                score += 1

            # losing if player gets caught or time runs out
            if player_pos == opp_pos or time_left <= 0:
                game_over = True
                win = False

            # winning if player reaches exit with all diamonds
            if player_pos == exit_pos and not diamonds:
                game_over = True
                win = True

        # Calculate opponent path for visualization
        opp_path = None
        if not game_over:
            opp_path = astar(opp_pos, player_pos)

        draw_game(screen, player_pos, opp_pos, exit_pos, diamonds, font, score, time_left, game_over, win, opp_path)
        pygame.display.flip()

if __name__ == "__main__": 
    main()