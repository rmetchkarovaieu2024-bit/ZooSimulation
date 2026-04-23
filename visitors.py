# visitors.py
# ─────────────────────────────────────────────────────────────────────────────
#  VISITOR HIERARCHY
#
#  Behavioural rules by subtype:
#
#  Child   (age < 12)
#    - Moves faster: energy penalty 0.03 per move (vs 0.05 Adult baseline)
#    - Can revisit exhibits (no deduplication guard)
#    - Dwell time multiplier: 0.8  (shorter attention span)
#
#  Student (age 12-21)
#    - Standard speed, standard dwell
#
#  Adult   (age 22-60)
#    - Baseline behaviour
#
#  Senior  (age > 60)
#    - Moves slower: energy penalty 0.08 per move
#    - Dwell time multiplier: 1.6  (spends more time at each exhibit)
#    - Higher probability of rest/food stops
# ─────────────────────────────────────────────────────────────────────────────

import random
import copy
from utils import log, BLUE, CYAN, GREEN, GREY


class Visitor:
    # Subtype-specific parameters (move_penalty, dwell_multiplier, can_revisit)
    PROFILES = {
        "Child":   {"move_penalty": 0.03, "dwell_mult": 0.8,  "can_revisit": True},
        "Student": {"move_penalty": 0.05, "dwell_mult": 1.0,  "can_revisit": False},
        "Adult":   {"move_penalty": 0.05, "dwell_mult": 1.0,  "can_revisit": False},
        "Senior":  {"move_penalty": 0.08, "dwell_mult": 1.6,  "can_revisit": False},
    }


    def __init__(self, name, age):
        self.id               = random.randint(10000, 99999)
        self.name             = name
        self.age              = age
        self.subtype          = self._classify()
        self.ticket_type      = "School" if self.subtype == "Student" else "Standard"
        self.satisfaction     = round(random.uniform(0.5, 0.9), 2)
        self.energy           = round(random.uniform(0.5, 1.0), 2)
        self.money            = round(random.uniform(10, 100), 2)
        self.current_location = "Entrance"
        self.exhibits_visited = []          # tracks visit history (with repeats for kids)
        self._visited_set     = set()       # for deduplication check on non-kids

    def _classify(self):
        if self.age < 12:  return "Child"
        if self.age > 60:  return "Senior"
        if self.age < 22:  return "Student"
        return "Adult"

    def _profile(self, key):
        return self.PROFILES[self.subtype][key]

    # ── movement ──────────────────────────────────────────────────────────────

    def move(self, destination):
       #  penalty = self._profile("move_penalty")
        self.energy = max(0.0, round(self.energy - self._profile("move_penalty"), 2))
        self.current_location = destination
        speed = {"Child": "fast", "Senior": "slow"}.get(self.subtype, "normal")
        log("VISITOR",
            f"{self.name:<10} ({self.subtype:<7})  ->  {destination:<24}  "
            f"Energy: {self.energy:.2f}  [{speed} pace]", BLUE)

    # ── exhibit interaction ───────────────────────────────────────────────────

    def dwell_time(self, exhibit):
        """
        Actual dwell = exhibit base dwell * subtype multiplier.
        Seniors stay longer; kids stay shorter.
        """
        base = exhibit.base_dwell_time()
        mult = self._profile("dwell_mult")
        return max(1, round(base * mult))


    def watch_exhibit(self, exhibit):
        dwell = self.dwell_time(exhibit)
        gain  = round(random.uniform(0.02, 0.08), 2)
        self.satisfaction = min(1.0, round(self.satisfaction + gain, 2))
        self.exhibits_visited.append(exhibit.name)
        self._visited_set.add(exhibit.name)

        revisit = "  [revisit]" if self.exhibits_visited.count(exhibit.name) > 1 else ""
        log("VISITOR",
            f"{self.name:<10}  Watching {exhibit.name:<24}  "
            f"Dwell: {dwell} min   Satisfaction: {self.satisfaction:.2f}{revisit}", BLUE)

    def has_visited(self, exhibit_name):
        """Children can always re-enter; others cannot."""
        if self._profile("can_revisit"):
            return False
        return exhibit_name in self._visited_set

    # ── purchases ─────────────────────────────────────────────────────────────

    def buy_food(self):
        cost = round(random.uniform(5, 15), 2)
        self.money  = round(self.money - cost, 2)
        self.energy = min(1.0, round(self.energy + 0.15, 2))
        log("VISITOR",
            f"{self.name:<10}  Food purchase   EUR {cost:.2f}   "
            f"Balance: EUR {self.money:.2f}", BLUE)

    def buy_ticket(self):
        price = 8.0 if self.subtype == "Child" else 5.0 if self.subtype == "Senior" else 12.0
        log("TICKET",
            f"{self.name:<10}  Type: {self.ticket_type:<10}  Price: EUR {price:.2f}", CYAN)
        return price

    # ── exit ──────────────────────────────────────────────────────────────────

    def leave_zoo(self):
        unique = len(self._visited_set)
        total  = len(self.exhibits_visited)
        log("VISITOR",
            f"{self.name:<10}  Exit.   Unique exhibits: {unique}   "
            f"Total visits: {total}   Satisfaction: {self.satisfaction:.2f}   "
            f"Energy: {self.energy:.2f}", BLUE)


# ── Concrete subclasses (extend for custom overrides in the future) ───────────

class RegularVisitor(Visitor):
    pass

class KidsVisitor(Visitor):
    pass

class SeniorVisitor(Visitor):
    pass

class StudentVisitor(Visitor):
    pass

# clone
def clone_visitor(template, name, age):
    cloned = copy.deepcopy(template)
    cloned.id = random.randint(10000, 99999)
    cloned.name = name
    cloned.age = age
    cloned.subtype = cloned._classify()
    cloned.ticket_type = "School" if cloned.subtype == "Student" else "Standard"
    # Wide ranges so visitors genuinely differ from each other
    cloned.energy = round(random.uniform(0.50, 1.00), 2)
    cloned.money = round(random.uniform(10, 100), 2)
    cloned.satisfaction = round(random.uniform(0.50, 0.90), 2)
    cloned.current_location = "Entrance"
    cloned.exhibits_visited = []
    cloned._visited_set = set()
    return cloned

_TEMPLATES = { # prototype instances with placeholder name and age (overridden in cloning)
    "Child": KidsVisitor("__template__", 9),
    "Student": StudentVisitor("__template__", 20),
    "Adult": RegularVisitor("__template__", 35),
    "Senior": SeniorVisitor("__template__", 68),
}

class VisitorFactory:
    # Name pools — enough names to avoid duplicates for typical counts
    NAMES = {
        "Child": [
            "Lucas", "Elena", "Pablo", "Sofia", "Matias", "Valentina",
            "Emilio", "Isabela", "Diego", "Lucia", "Andres", "Camila",
            "Juan", "Maria", "Pedro", "Ana", "Carlos", "Rosa",
            "Luis", "Carla", "Miguel", "Carmen", "Felix", "Ines", "Hugo",
        ],
        "Student": [
            "Mia", "Daniel", "Alejandro", "Valeria", "Mateo", "Sara",
            "Sebastian", "Paula", "Tomas", "Andrea", "Julian", "Mariana",
            "Nicolas", "Fernanda", "Samuel", "Alba", "Ivan", "Nadia",
            "Omar", "Irene",
        ],
        "Adult": [
            "Sofia", "Marco", "Carmen", "Andres", "Isabella", "Rafael",
            "Valentina", "Santiago", "Camila", "Nicolas", "Lucia", "Diego",
            "Ana", "Jorge", "Monica", "Carlos", "Patricia", "Fernando",
            "Daniela", "Alberto", "Rosa", "Miguel", "Claudia", "Eduardo",
            "Natalia", "Roberto", "Laura", "Victor", "Gabriela", "Sergio",
            "Elena", "Pablo", "Hector", "Silvia", "Ramon", "Teresa",
        ],
        "Senior": [
            "Javier", "Beatriz", "Manuel", "Esperanza", "Antonio", "Pilar",
            "Francisco", "Mercedes", "Jose", "Dolores", "Ramon", "Consuelo",
            "Alfredo", "Rosario", "Enrique", "Carmen", "Luis", "Amparo",
            "Pedro", "Concepcion",
        ],
    }

    AGE_RANGES = {
        "Child": (5, 11),
        "Student": (17, 22),
        "Adult": (23, 60),
        "Senior": (61, 82),
    }

    @classmethod
    def generate(cls, counts: dict) -> list:
        visitors = []
        for subtype, n in counts.items():
            template = _TEMPLATES[subtype]
            name_pool = cls.NAMES[subtype][:]
            random.shuffle(name_pool)
            age_min, age_max = cls.AGE_RANGES[subtype]

            for i in range(n):
                name = name_pool[i % len(name_pool)]
                if i >= len(name_pool):  # cycle with suffix if needed
                    name = f"{name}{i // len(name_pool) + 1}"
                age = random.randint(age_min, age_max)
                v = clone_visitor(template, name, age)
                visitors.append(v)

        log("VISITOR_F",
            f"Generated {len(visitors)} visitors via Prototype cloning  "
            f"({', '.join(f'{n} {s}' for s, n in counts.items())})", GREEN)

        random.shuffle(visitors)  # mix subtypes across the day
        return visitors