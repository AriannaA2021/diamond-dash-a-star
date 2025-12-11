import diamondDash
import heapq
import time
import math

# 1. Define the Manhattan Heuristic
def manhattan_heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# 2. Implement A* using the Manhattan Heuristic
# This is a modified version of the game's astar function
def astar_manhattan(start, goal):
    if start == goal:
        return [start]
    
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    # Use manhattan_heuristic here
    f_score = {start: manhattan_heuristic(start, goal)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return path[::-1]

        for direction in diamondDash.DIRECTIONS.values():
            neighbor = (current[0] + direction[0], current[1] + direction[1])
            # Check bounds using GRID_SIZE from the game module
            if 0 <= neighbor[0] < diamondDash.GRID_SIZE and 0 <= neighbor[1] < diamondDash.GRID_SIZE:
                tentative_g_score = g_score[current] + 1
                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    # Use manhattan_heuristic here
                    f_score[neighbor] = tentative_g_score + manhattan_heuristic(neighbor, goal)
                    if neighbor not in [i[1] for i in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return None

# 3. AI Logic to Determine Target
def get_user_target(player_pos, diamonds, exit_pos):
    """
    Decides where the AI User wants to go.
    Logic: Go to the nearest diamond (by Manhattan distance). 
           If no diamonds, go to the exit.
    """
    if diamonds:
        # Find nearest diamond using Manhattan distance
        nearest_diamond = min(diamonds, key=lambda d: manhattan_heuristic(player_pos, d))
        return nearest_diamond
    else:
        return exit_pos

# 4. Main Simulation Loop
def run_simulation(num_simulations=500):
    total_astar_time_ns = 0
    total_astar_calls = 0
    player_wins = 0
    player_losses = 0
    
    print(f"Running {num_simulations} simulations...")
    
    for i in range(num_simulations):
        # Reset game state
        player_pos, opp_pos, exit_pos, diamonds = diamondDash.setup_game()
        game_over = False
        steps = 0
        max_steps = 1000  # Safety break to prevent infinite loops
        won = False
        
        while not game_over and steps < max_steps:
            steps += 1
            
            # --- USER AI TURN ---
            # 1. Determine target
            target = get_user_target(player_pos, diamonds, exit_pos)
            
            # 2. Execute and Time A* Search
            start_time = time.perf_counter_ns()
            path = astar_manhattan(player_pos, target)
            end_time = time.perf_counter_ns()
            
            # Accumulate stats
            total_astar_time_ns += (end_time - start_time)
            total_astar_calls += 1
            
            # 3. Move Player
            if path and len(path) > 1:
                player_pos = path[1]
            
            # --- CHECK GAME LOGIC ---
            if player_pos in diamonds:
                diamonds.remove(player_pos)
            
            # Check Win
            if player_pos == exit_pos and not diamonds:
                game_over = True
                won = True
            
            # --- OPPONENT TURN ---
            # Opponent moves towards player (uses original game logic)
            # We assume the opponent still behaves normally
            if not game_over:
                opp_pos = diamondDash.opponent_move(opp_pos, player_pos)
                
                # Check Loss
                if player_pos == opp_pos:
                    game_over = True
                    won = False
        
        # Track win/loss after game ends
        if won:
            player_wins += 1
        else:
            player_losses += 1

    # 5. Calculate and Print Results
    if total_astar_calls > 0:
        avg_ns = total_astar_time_ns / total_astar_calls
        avg_us = avg_ns / 1000.0  # Convert nanoseconds to microseconds
        win_rate = (player_wins / num_simulations) * 100 if num_simulations > 0 else 0
        print(f"\n--- Results ---")
        print(f"Total Simulations: {num_simulations}")
        print(f"Player Wins: {player_wins}")
        print(f"Player Losses: {player_losses}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Total A* Calls: {total_astar_calls}")
        print(f"Average A* Time: {avg_us:.4f} microseconds")
    else:
        print("No A* calls were made.")

if __name__ == "__main__":
    run_simulation()
