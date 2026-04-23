# workers.py
# ─────────────────────────────────────────────────────────────────────────────
#  WORKER HIERARCHY
#
#  Design pattern housed here (workers own this concept):
#  Pattern 9 — Chain of Responsibility : IncidentHandler chain
#                SecurityHandler -> VetHandler -> ZooManagerHandler
#
#  Base: Worker
#  Subclasses: Cleaner, Feeder, Ticketero, ShopEmployee, Security
# ─────────────────────────────────────────────────────────────────────────────

import random
from utils import log, GREEN, YELLOW, RED, CYAN, GREY


class Worker: # base
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

#─#─ Pattern 9 ───────────────────────────────────────────────────────────────────

class IncidentHandler: # base for chain of responsibility
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self._next = None

    def set_next(self, handler):
        self._next = handler
        return handler  # allows chaining: a.set_next(b).set_next(c)

    def handle(self, incident):
        raise NotImplementedError

    def _escalate(self, incident):
        if self._next:
            log("CHAIN",
                f"{self.name:<16} [{self.role}]  Cannot resolve — escalating.", GREY)
            self._next.handle(incident)
        else:
            log("CHAIN",
                f"Incident unresolved after full chain: '{incident['type']}'", RED)


class SecurityHandler(IncidentHandler): # first in chain — resolves security-related incidents.
    HANDLES = {"crowd", "trespassing", "lost_child"}

    def __init__(self, name="Marcos"):
        super().__init__(name, "Security Officer")

    def handle(self, incident):
        log("CHAIN",
            f"{self.name:<16} [{self.role}]  Received: '{incident['type']}'", RED)
        if incident["type"] in self.HANDLES:
            log("CHAIN",
                f"{self.name:<16}  RESOLVED: {incident['description']}", GREEN)
        else:
            self._escalate(incident)


class VetHandler(IncidentHandler): # second in chain — resolves animal health-related incidents.
    HANDLES = {"sick_animal", "injury", "feeding_emergency"}

    def __init__(self, name="Dr. Lopez"):
        super().__init__(name, "Zoo Veterinarian")

    def handle(self, incident):
        log("CHAIN",
            f"{self.name:<16} [{self.role}]  Received: '{incident['type']}'", YELLOW)
        if incident["type"] in self.HANDLES:
            log("CHAIN",
                f"{self.name:<16}  RESOLVED: {incident['description']}", GREEN)
        else:
            self._escalate(incident)


class ZooManagerHandler(IncidentHandler): # final in chain — resolves any incident with executive decision.

    def __init__(self, name="Director Garcia"):
        super().__init__(name, "Zoo Manager")

    def handle(self, incident):
        log("CHAIN",
            f"{self.name:<16} [{self.role}]  Received: '{incident['type']}'", CYAN)
        log("CHAIN",
            f"{self.name:<16}  RESOLVED (executive decision): "
            f"{incident['description']}", GREEN)


def build_incident_chain(): # helper function to construct the chain of responsibility
    security = SecurityHandler()
    vet = VetHandler()
    manager = ZooManagerHandler()
    security.set_next(vet).set_next(manager)
    return security


def dispatch_incident(chain_head, incident_type, description): # helper function to create and dispatch an incident through the chain
    incident = {"type": incident_type, "description": description}
    log("CHAIN",
        f"Incident dispatched  type='{incident_type}'  "
        f"desc='{description}'", RED)
    chain_head.handle(incident)