# =========================================================
# SMART PARKING ALLOCATION SYSTEM (Full Project Code)
# =========================================================
# Total Slots = 48
# Reserved Slots = 5
# Normal Parking = Rs.50/hour
# Reserved Parking = Rs.60/hour
# =========================================================

from collections import deque
from queue import PriorityQueue
import time

# =========================================================
# PARKING SLOT CLASS
# =========================================================
class ParkingSlot:
    def __init__(self, slot_id, floor):
        self.slot_id = slot_id
        self.floor = floor
        self.is_reserved = False
        self.is_occupied = False
        self.vehicle_number = None
        self.entry_time = None

    def __str__(self):
        if self.is_reserved:
            status = "Reserved"
        elif self.is_occupied:
            status = "Occupied"
        else:
            status = "Free"
        return f"Slot {self.slot_id} | Floor {self.floor} | Status: {status}"

# =========================================================
# SMART PARKING SYSTEM CLASS
# =========================================================
class SmartParkingSystem:
    def __init__(self):
        self.slots = {}
        self.graph = {}
        self.initialize_slots()
        self.create_graph()

    # -----------------------------------------------------
    # Initialize 48 slots, assign reserved ones
    # -----------------------------------------------------
    def initialize_slots(self):
        reserved_slots = [5, 11, 18, 27, 35]
        for i in range(1, 49):
            floor = 1 if i <= 24 else 2
            self.slots[i] = ParkingSlot(i, floor)
            if i in reserved_slots:
                self.slots[i].is_reserved = True

    # -----------------------------------------------------
    # Create graph representation (neighbors)
    # -----------------------------------------------------
    def create_graph(self):
        for i in range(1, 49):
            neighbors = []
            if i - 1 >= 1:
                neighbors.append(i - 1)
            if i + 1 <= 48:
                neighbors.append(i + 1)
            self.graph[i] = neighbors

    # -----------------------------------------------------
    # Display all slots
    # -----------------------------------------------------
    def display_slots(self):
        print("\n========= PARKING STATUS =========")
        for slot in self.slots.values():
            print(slot)

    # -----------------------------------------------------
    # BFS Search
    # -----------------------------------------------------
    def bfs_search(self, start=1):
        visited = set()
        queue = deque([start])
        while queue:
            node = queue.popleft()
            if node not in visited:
                visited.add(node)
                if not self.slots[node].is_occupied:
                    return node
                for neighbor in self.graph[node]:
                    queue.append(neighbor)
        return None

    # -----------------------------------------------------
    # DFS Search
    # -----------------------------------------------------
    def dfs_search(self, start=1):
        visited = set()
        stack = [start]
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                if not self.slots[node].is_occupied:
                    return node
                for neighbor in self.graph[node]:
                    stack.append(neighbor)
        return None

    # -----------------------------------------------------
    # Heuristic for A* (prefer lower floor)
    # -----------------------------------------------------
    def heuristic(self, slot_id):
        return self.slots[slot_id].floor

    # -----------------------------------------------------
    # A* Search
    # -----------------------------------------------------
    def a_star_search(self):
        pq = PriorityQueue()
        pq.put((0, 1))
        visited = set()
        while not pq.empty():
            cost, node = pq.get()
            if node not in visited:
                visited.add(node)
                if not self.slots[node].is_occupied:
                    return node
                for neighbor in self.graph[node]:
                    priority = cost + self.heuristic(neighbor)
                    pq.put((priority, neighbor))
        return None

    # -----------------------------------------------------
    # Constraint Satisfaction Check
    # -----------------------------------------------------
    def constraint_check(self, slot_id, parking_type):
        slot = self.slots[slot_id]
        if parking_type == "RESERVED":
            if not slot.is_reserved:
                return False
        else:
            if slot.is_reserved:
                return False
        if slot.is_occupied:
            return False
        return True

    # -----------------------------------------------------
    # Utility Function (lower floor preferred)
    # -----------------------------------------------------
    def utility_function(self, slot_id):
        slot = self.slots[slot_id]
        score = 100
        score -= slot.floor * 10
        return score

    # -----------------------------------------------------
    # Allocate Slot (Hybrid reasoning: Search + CSP + Utility)
    # -----------------------------------------------------
    def allocate_slot(self, vehicle_number, parking_type):
        print("\nSearching for best parking slot...")
        slot_id = self.a_star_search()
        if slot_id is None:
            print("Parking Full")
            return
        if not self.constraint_check(slot_id, parking_type):
            found = False
            for sid in self.slots:
                if self.constraint_check(sid, parking_type):
                    slot_id = sid
                    found = True
                    break
            if not found:
                print("No suitable slot available")
                return
        slot = self.slots[slot_id]
        slot.is_occupied = True
        slot.vehicle_number = vehicle_number
        slot.entry_time = time.time()
        utility = self.utility_function(slot_id)
        print("\n========= SLOT ALLOCATED =========")
        print(f"Vehicle Number : {vehicle_number}")
        print(f"Parking Type   : {parking_type}")
        print(f"Allocated Slot : {slot_id}")
        print(f"Utility Score  : {utility}")

    # -----------------------------------------------------
    # Vehicle Exit + Cost Calculation
    # -----------------------------------------------------
    def vehicle_exit(self, vehicle_number):
        for slot in self.slots.values():
            if slot.vehicle_number == vehicle_number:
                exit_time = time.time()
                total_seconds = exit_time - slot.entry_time
                total_minutes = total_seconds / 60
                total_hours = total_minutes / 60
                if total_hours < 1:
                    total_hours = 1
                total_hours = round(total_hours)
                if slot.is_reserved:
                    total_cost = total_hours * 60
                else:
                    total_cost = total_hours * 50
                slot.is_occupied = False
                slot.vehicle_number = None
                slot.entry_time = None
                print("\n========= VEHICLE EXIT =========")
                print(f"Vehicle Number : {vehicle_number}")
                print(f"Parking Time   : {total_minutes:.2f} minutes")
                print(f"Parking Cost   : Rs.{total_cost}")
                return
        print("\nVehicle not found")

    # -----------------------------------------------------
    # Probability Prediction (Availability)
    # -----------------------------------------------------
    def predict_availability(self):
        free_slots = 0
        for slot in self.slots.values():
            if not slot.is_occupied:
                free_slots += 1
        probability = free_slots / 48
        print("\n========= AVAILABILITY PREDICTION =========")
        print(f"Probability of free slot: {probability:.2f}")
        if probability > 0.7:
            print("High Availability")
        elif probability > 0.4:
            print("Medium Availability")
        else:
            print("Low Availability")

# =========================================================
# MAIN PROGRAM
# =========================================================
parking = SmartParkingSystem()

while True:
    print("\n========= SMART PARKING MENU =========")
    print("1. Display Parking Slots")
    print("2. Allocate Parking Slot")
    print("3. Vehicle Exit")
    print("4. Predict Availability")
    print("5. BFS Search")
    print("6. DFS Search")
    print("7. Exit")

    choice = input("\nEnter your choice: ")

    if choice == '1':
        parking.display_slots()
    elif choice == '2':
        vehicle_number = input("Enter Vehicle Number: ")
        parking_type = input("Enter Parking Type (NORMAL / RESERVED): ").upper()
        parking.allocate_slot(vehicle_number, parking_type)
    elif choice == '3':
        vehicle_number = input("Enter Vehicle Number: ")
        parking.vehicle_exit(vehicle_number)
    elif choice == '4':
        parking.predict_availability()
    elif choice == '5':
        slot = parking.bfs_search()
        print(f"\nBFS Found Free Slot: {slot}")
    elif choice == '6':
        slot = parking.dfs_search()
        print(f"\nDFS Found Free Slot: {slot}")
    elif choice == '7':
        print("\nExiting Smart Parking Allocation System")
        break
    else:
        print("\nInvalid Choice")
