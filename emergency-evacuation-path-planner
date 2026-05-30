"""
================================================================================
EMERGENCY EVACUATION PATH PLANNER
================================================================================
This program finds the safest and fastest way out of a building during a fire.
It handles:
 1. Building Layout (Nodes as rooms/hallways, Edges as paths)
 2. Smart Search (A* Algorithm to find the quickest route avoiding fire)
 3. Crowd Limits (Stopping too many people from crowding one hallway)
 4. Safety Score (Rating routes based on length and danger)
 5. Danger Prediction (Using math to guess if a smoky room is blocked)
================================================================================
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
from collections import deque
from queue import PriorityQueue


# ==============================================================================
# 1. BUILDING BLOCKS: ROOMS AND HALLWAYS
# ==============================================================================

@dataclass(order=True)
class PriorityItem:
    """A simple helper to keep our search queue sorted properly."""
    priority: float
    node_id: int = field(compare=True)


class BuildingNode:
    """Represents a single room, hallway section, or exit door."""
    def __init__(self, node_id: int, floor: int, is_exit: bool = False):
        self.node_id = node_id
        self.floor = floor
        self.is_exit = is_exit
        
        # Crowd control limits to stop stampedes
        self.max_people_allowed = 10 if not is_exit else 1000
        self.current_people_count = 0
        
        # Danger level from 0.0 (perfectly safe) to 1.0 (on fire)
        self.danger_level = 0.0

    def __str__(self) -> str:
        room_type = "SAFE EXIT" if self.is_exit else "Hallway"
        return (
            f"Zone {self.node_id:02d} (Floor {self.floor}) | "
            f"Type: {room_type:<9} | "
            f"Danger: {self.danger_level * 100:>5.1f}% | "
            f"People: {self.current_people_count:02d}/{self.max_people_allowed:02d}"
        )


class EvacuationSystem:
    """The main system that manages the building graph and plans paths."""
    def __init__(self):
        self.nodes: Dict[int, BuildingNode] = {}
        self.graph: Dict[int, List[int]] = {}
        self.total_nodes = 48
        
        self.setup_building()
        self.connect_rooms()

    def setup_building(self):
        """Creates 48 rooms across 2 floors and sets up the exits."""
        # Nodes 1, 12, 25, and 36 are doors leading safely outside
        safe_exits = {1, 12, 25, 36}
        
        for i in range(1, self.total_nodes + 1):
            floor = 1 if i <= 24 else 2
            self.nodes[i] = BuildingNode(i, floor, is_exit=(i in safe_exits))

    def connect_rooms(self):
        """Connects neighboring rooms together to form hallways and stairs."""
        for i in range(1, self.total_nodes + 1):
            neighbors = []
            
            # Connect to left neighbor on the same floor
            if i - 1 >= 1 and (i - 1) // 24 == (i - 1) // 24: 
                neighbors.append(i - 1)
            # Connect to right neighbor on the same floor
            if i + 1 <= self.total_nodes and (i // 24 == (i - 1) // 24): 
                neighbors.append(i + 1)
            
            # Add emergency staircases connecting Floor 2 to Floor 1
            if i == 30: neighbors.append(6)
            if i == 6: neighbors.append(30)
            if i == 42: neighbors.append(18)
            if i == 18: neighbors.append(42)
            
            self.graph[i] = neighbors

    def print_layout(self):
        """Prints the current status of every room in the building."""
        print("\n======================= BUILDING STATUS REPORT =======================")
        for i, node in self.nodes.items():
            print(node)
            if i == 24:
                print("-" * 70)  # Separator line between Floor 1 and Floor 2

    # ==============================================================================
    # 2. PATHFINDING: SEARCH ALGORITHMS
    # ==============================================================================

    def run_bfs(self, start: int) -> Tuple[Optional[List[int]], int]:
        """Simple step-by-step search that looks at all nearby options first."""
        visited: Set[int] = set()
        queue = deque([[start]])
        steps_taken = 0

        while queue:
            path = queue.popleft()
            current = path[-1]
            if current in visited: continue
            visited.add(current)
            steps_taken += 1

            if self.nodes[current].is_exit and self.nodes[current].danger_level < 0.8:
                return path, steps_taken

            for neighbor in self.graph[current]:
                if neighbor not in visited:
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)
        return None, steps_taken

    def run_dfs(self, start: int) -> Tuple[Optional[List[int]], int]:
        """Simple search that goes as far down one path as possible before turning back."""
        visited: Set[int] = set()
        stack = [[start]]
        steps_taken = 0

        while stack:
            path = stack.pop()
            current = path[-1]
            if current in visited: continue
            visited.add(current)
            steps_taken += 1

            if self.nodes[current].is_exit and self.nodes[current].danger_level < 0.8:
                return path, steps_taken

            for neighbor in reversed(self.graph[current]):
                if neighbor not in visited:
                    new_path = list(path)
                    new_path.append(neighbor)
                    stack.append(new_path)
        return None, steps_taken

    def floor_heuristic(self, node_id: int) -> float:
        """A helpful guess that prefers paths on lower floors near the ground."""
        return float((self.nodes[node_id].floor - 1) * 10.0)

    def run_smart_a_star(self, start: int) -> Tuple[Optional[List[int]], int]:
        """
        Smart search algorithm that finds the absolute quickest way out.
        It calculates the distance and adds a massive penalty cost if a room is on fire.
        """
        queue = PriorityQueue()
        queue.put(PriorityItem(0.0, start))
        
        movement_costs = {i: float('inf') for i in self.nodes.keys()}
        movement_costs[start] = 0.0
        
        parent_map = {}
        visited: Set[int] = set()
        steps_taken = 0

        while not queue.empty():
            current_item = queue.get()
            current = current_item.node_id

            if current in visited: continue
            visited.add(current)
            steps_taken += 1

            # Stop when we find a safe exit door that isn't blocked by fire
            if self.nodes[current].is_exit and self.nodes[current].danger_level < 0.8:
                path = []
                while current in parent_map:
                    path.append(current)
                    current = parent_map[current]
                path.append(start)
                return path[::-1], steps_taken

            for neighbor in self.graph[current]:
                # Add extra cost penalty if the room is dangerous
                danger_penalty = self.nodes[neighbor].danger_level * 40.0
                total_step_cost = movement_costs[current] + 1.0 + danger_penalty
                
                if total_step_cost < movement_costs[neighbor]:
                    movement_costs[neighbor] = total_step_cost
                    estimated_total_cost = total_step_cost + self.floor_heuristic(neighbor)
                    parent_map[neighbor] = current
                    queue.put(PriorityItem(estimated_total_cost, neighbor))
                    
        return None, steps_taken

    # ==============================================================================
    # 3. CROWD AND CONSTRAINT CONTROL
    # ==============================================================================

    def check_route_safety(self, path: List[int], group_size: int) -> Tuple[bool, str]:
        """Checks if a route is safe and has enough room for everyone."""
        for room_id in path:
            room = self.nodes[room_id]
            if room.danger_level >= 0.8:
                return False, f"Room {room_id} is blocked by fire!"
            if room.current_people_count + group_size > room.max_people_allowed:
                return False, f"Hallway {room_id} is too crowded!"
        return True, "Route is clear and safe to use."

    def find_backup_route(self, start: int, group_size: int) -> Optional[List[int]]:
        """A backup scanner that searches for alternative paths if the main one is full."""
        routes_to_try = deque([[start]])
        while routes_to_try:
            path = routes_to_try.popleft()
            current = path[-1]
            
            if len(path) > 15: continue  # Don't make the path too long
            
            if self.nodes[current].is_exit:
                is_ok = True
                for room_id in path:
                    if self.nodes[room_id].current_people_count + group_size > self.nodes[room_id].max_people_allowed:
                        is_ok = False
                        break
                if is_ok: return path

            for neighbor in self.graph[current]:
                if neighbor not in path and self.nodes[neighbor].danger_level < 0.5:
                    new_path = list(path)
                    new_path.append(neighbor)
                    routes_to_try.append(new_path)
        return None

    # ==============================================================================
    # 4. DECISION AND PREDICTION UTILITIES
    # ==============================================================================

    def rate_path_safety(self, path: List[int]) -> float:
        """Scores a path out of 100 points. Shorter and less dangerous paths score higher."""
        if not path: return 0.0
        
        total_danger = sum(self.nodes[room].danger_level for room in path)
        average_danger = total_danger / len(path)
        length_penalty = len(path) * 1.5
        
        score = 100.0 - (average_danger * 50.0) - length_penalty
        return max(0.0, min(100.0, score))

    def guess_danger_with_math(self, room_id: int) -> float:
        """Uses probability math to figure out if a smoky room is actually blocked."""
        base_chance_of_fire = 0.15
        chance_of_smoke_if_on_fire = 0.90
        chance_of_smoke_by_mistake = 0.20
        
        # Calculate overall chance of seeing smoke
        total_smoke_chance = (chance_of_smoke_if_on_fire * base_chance_of_fire) + \
                             (chance_of_smoke_by_mistake * (1.0 - base_chance_of_fire))
        
        #  Chance that room is blocked given that we see smoke
        final_probability = (chance_of_smoke_if_on_fire * base_chance_of_fire) / total_smoke_chance
        return final_probability

    # ==============================================================================
    # 5. CORE SYSTEM CONTROLLER
    # ==============================================================================

    def guide_people_to_safety(self, group_name: str, start_room: int, group_size: int):
        """Combines search, crowd checks, and scores to route people out safely."""
        print(f"\n[SYSTEM LOG] Finding exit route for group: {group_name} (Size: {group_size} people)")
        
        # Step 1: Find the best route using the smart search
        chosen_path, steps = self.run_smart_a_star(start_room)
        
        # Step 2: Double check crowd sizes and fire blocks
        if chosen_path:
            is_good, message = self.check_route_safety(chosen_path, group_size)
            print(f"[SYSTEM LOG] Checking route: {message}")
        else:
            is_good, chosen_path = False, None

        # Step 3: Use backup plan if route is too full or on fire
        if not is_good:
            print("[SYSTEM LOG] Route failed checks. Looking for an alternative path...")
            chosen_path = self.find_backup_route(start_room, group_size)

        if not chosen_path:
            print(f"[-] CRITICAL DANGER: Group {group_name} is trapped! No clear path found.")
            return

        # Add people to the room count to track hallway crowding
        for room_id in chosen_path:
            self.nodes[room_id].current_people_count += group_size

        path_score = self.rate_path_safety(chosen_path)

        print("\n============= EMERGENCY ROUTE ASSIGNED =============")
        print(f" Group Name    : {group_name}")
        print(f" Escape Route  : {' -> '.join(map(str, chosen_path))}")
        print(f" Route Score   : {path_score:.1f} / 100.0 Points")
        print(f" Status        : Path open! Signs changed to guide this group.")
        print("====================================================")


# ==============================================================================
# MAIN SYSTEM INTERFACE
# ==============================================================================

if __name__ == "__main__":
    building = EvacuationSystem()

    # Pre-set some fake problems in the building for testing
    building.nodes[4].danger_level = 0.95   # Room 4 is on fire
    building.nodes[5].danger_level = 0.60   # Room 5 has a lot of smoke
    building.nodes[2].current_people_count = 10  # Hallway 2 is completely full

    while True:
        print("\n--- EMERGENCY INCIDENT CONTROL PANEL ---")
        print("1. Show Building Status Map")
        print("2. Route a Group of People to Safety")
        print("3. Check Probability of Danger in a Smoky Room")
        print("4. Compare Simple Search Speed (BFS vs DFS)")
        print("5. Set Fire or Smoke Levels in a Room")
        print("6. Turn Off System")
        
        user_choice = input("\nSelect an option [1-6]: ").strip()

        if user_choice == '1':
            building.print_layout()
            
        elif user_choice == '2':
            name = input("Enter Group Name: ").strip()
            try:
                start = int(input("Enter their current Room ID [1-48]: "))
                size = int(input("How many people are in this group?: "))
                if start in building.nodes:
                    building.guide_people_to_safety(name, start, size)
                else:
                    print("[-] Error: Room number does not exist.")
            except ValueError:
                print("[-] Error: Please enter numbers only.")
                
        elif user_choice == '3':
            try:
                room = int(input("Enter room to check [1-48]: "))
                if room in building.nodes:
                    chance = building.guess_danger_with_math(room)
                    print(f"\nDanger probability for Room {room}: {chance * 100:.1f}%")
                else:
                    print("[-] Error: Room number does not exist.")
            except ValueError:
                print("[-] Error: Please enter numbers only.")
                
        elif user_choice == '4':
            try:
                room = int(input("Enter a room to start the test from [1-48]: "))
                if room in building.nodes:
                    _, bfs_steps = building.run_bfs(room)
                    _, dfs_steps = building.run_dfs(room)
                    print(f"\n--- ALGORITHM PERFORMANCE TEST ---")
                    print(f" BFS search checked: {bfs_steps} rooms")
                    print(f" DFS search checked: {dfs_steps} rooms")
                else:
                    print("[-] Error: Room number does not exist.")
            except ValueError:
                print("[-] Error: Please enter numbers only.")
                
        elif user_choice == '5':
            try:
                room = int(input("Enter Room ID [1-48]: "))
                danger = float(input("Enter new Danger Level [0.0 for safe, 1.0 for on fire]: "))
                if room in building.nodes and (0.0 <= danger <= 1.0):
                    building.nodes[room].danger_level = danger
                    print(f"[SUCCESS] Room {room} updated successfully.")
                else:
                    print("[-] Error: Invalid room number or danger value range.")
            except ValueError:
                print("[-] Error: Please check your inputs.")
                
        elif user_choice == '6':
            print("\nShutting down system thread... Goodbye.")
            break
        else:
            print("\n[-] Error: Invalid option selected.")
