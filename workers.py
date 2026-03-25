# workers.py
# ─────────────────────────────────────────────────────────────────────────────
#  WORKER HIERARCHY
#  Base: Worker
#  Subclasses: Cleaner, Feeder, Ticketero, ShopEmployee, Security
# ─────────────────────────────────────────────────────────────────────────────

import random
from utils import log, GREEN, YELLOW, RED, CYAN, GREY


class Worker:
    def __init__(self, name, role, shift_start, shift_end, salary):
        self.id               = random.randint(200, 999)
        self.name             = name
        self.role             = role
        self.shift_start      = shift_start
        self.shift_end        = shift_end
        self.salary           = salary
        self.current_location = "Staff Room"

    def start_shift(self):
        log("WORKER",
            f"{self.name:<12}  Role: {self.role:<16}  "
            f"Shift: {self.shift_start}-{self.shift_end}   "
            f"Salary: EUR {self.salary}/mo  [START]", GREEN)

    def end_shift(self):
        log("WORKER",
            f"{self.name:<12}  Role: {self.role:<16}  [END OF SHIFT]", GREY)

    def move(self, location):
        self.current_location = location
        log("WORKER", f"{self.name:<12}  Relocating to: {location}", GREY)

    def perform_task(self, task):
        log("WORKER", f"{self.name:<12}  Task: {task}", GREY)


# ─────────────────────────────────────────────────────────────────────────────

class Cleaner(Worker):
    def __init__(self, name):
        super().__init__(name, "Cleaner", "08:00", "16:00", 1200)

    def clean_exhibit(self, exhibit):
        exhibit.clean()
        log("CLEANER",
            f"{self.name:<12}  Cleaned: {exhibit.name:<24}  Cleanliness: 1.00", GREEN)

    def clean_path(self, path):
        log("CLEANER", f"{self.name:<12}  Cleaned path: {path}", GREEN)

    def clean_restroom(self):
        log("CLEANER", f"{self.name:<12}  Cleaned restrooms.", GREEN)


# ─────────────────────────────────────────────────────────────────────────────

class Feeder(Worker):
    def __init__(self, name):
        super().__init__(name, "Feeder", "07:00", "15:00", 1400)

    def feed_animals(self, exhibit):
        log("FEEDER", f"{self.name:<12}  Feeding animals in: {exhibit.name}", YELLOW)
        for animal in exhibit.animals:
            animal.eat()

    def check_food_stock(self):
        pct   = random.randint(20, 100)
        color = RED if pct < 30 else YELLOW if pct < 60 else GREEN
        log("FEEDER", f"{self.name:<12}  Food stock level: {color}{pct}%\033[0m", YELLOW)


# ─────────────────────────────────────────────────────────────────────────────

class Ticketero(Worker):
    def __init__(self, name):
        super().__init__(name, "Ticketero", "09:00", "18:00", 1300)

    def sell_ticket(self, visitor):
        return visitor.buy_ticket()

    def validate_ticket(self, visitor):
        log("TICKET",
            f"{self.name:<12}  Validated for {visitor.name:<10}  [OK]", CYAN)


# ─────────────────────────────────────────────────────────────────────────────

class ShopEmployee(Worker):
    ITEMS = ["Plush toy", "Zoo map", "Keychain", "Cap", "Mug", "Poster", "Guidebook"]

    def __init__(self, name):
        super().__init__(name, "Shop Employee", "10:00", "19:00", 1100)

    def sell_item(self, visitor):
        item = random.choice(self.ITEMS)
        cost = round(random.uniform(5, 25), 2)
        visitor.money = round(visitor.money - cost, 2)
        log("SHOP",
            f"{self.name:<12}  Sold '{item}' to {visitor.name:<10}   EUR {cost:.2f}", YELLOW)

    def restock_shop(self):
        log("SHOP", f"{self.name:<12}  Shop restocked.", YELLOW)


# ─────────────────────────────────────────────────────────────────────────────

class Security(Worker):
    def __init__(self, name):
        super().__init__(name, "Security", "08:00", "20:00", 1500)

    def patrol(self, zone):
        log("SECURITY", f"{self.name:<12}  Patrolling zone: {zone}", RED)

    def control_crowd(self, exhibit):
        log("SECURITY",
            f"{self.name:<12}  Crowd management at {exhibit.name:<22}  "
            f"Occupancy: {exhibit.current_visitors}/{exhibit.capacity}", RED)

    def handle_incident(self, description):
        log("SECURITY", f"{self.name:<12}  Incident: {description}", RED)
