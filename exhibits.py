# exhibits.py
# ─────────────────────────────────────────────────────────────────────────────
#  EXHIBIT
#
#  Design patterns housed here (exhibits own these concepts):
#    Pattern 2  — Abstract Factory : AbstractZoneFactory + concrete zone factories
#    Pattern 6  — Composite        : ExhibitGroup
#    Pattern 10 — Iterator         : ExhibitIterator
#
#  Popularity (1-10) drives:
#    - How many visitors choose this exhibit (weighted random selection)
#    - Base dwell time: dwell = 3 + popularity * 1.5  (minutes, randomised ±2)
# ─────────────────────────────────────────────────────────────────────────────

import random
import threading
from utils import GREEN, YELLOW, RED, RESET, log, BOLD, CYAN, BLUE


class Exhibit:
    def __init__(self, name, capacity, popularity, indoor=False):
        self.id               = random.randint(100, 999)
        self.name             = name
        self.capacity         = capacity
        self.popularity       = popularity   # 1 - 10
        self.indoor           = indoor
        self.animals          = []
        self.current_visitors = 0
        self.cleanliness      = round(random.uniform(0.7, 1.0), 2)
        self._lock            = threading.Lock()

    # ── animal management ─────────────────────────────────────────────────────

    def add_animal(self, animal):
        self.animals.append(animal)

    def remove_animal(self, animal):
        self.animals.remove(animal)

    # ── visitor management ────────────────────────────────────────────────────

    def add_visitor(self):
        with self._lock:
            if self.current_visitors < self.capacity:
                self.current_visitors += 1
                self.cleanliness = max(0.0, round(self.cleanliness - 0.02, 2))
                return True
            return False

    def remove_visitor(self):
        with self._lock:
            if self.current_visitors > 0:
                self.current_visitors -= 1

    def is_full(self):
        return self.current_visitors >= self.capacity

    # ── dwell time ────────────────────────────────────────────────────────────

    def base_dwell_time(self):
        """
        Returns base dwell time in minutes driven by popularity.
        popularity 1  ->  ~4-6 min
        popularity 5  ->  ~9-13 min
        popularity 10 ->  ~16-20 min
        """
        base = 3 + self.popularity * 1.5
        return max(2, int(base + random.uniform(-2, 2)))

    # ── maintenance ───────────────────────────────────────────────────────────

    def clean(self):
        self.cleanliness = 1.0

    # ── metrics ───────────────────────────────────────────────────────────────

    def utilization(self):
        return round(self.current_visitors / self.capacity * 100, 1)

    def capacity_bar(self):
        filled = int(self.current_visitors / self.capacity * 20)
        color  = RED if self.utilization() > 80 else YELLOW if self.utilization() > 50 else GREEN
        return f"{color}[{'#' * filled + '-' * (20 - filled)}]{RESET}"

    def clean_bar(self):
        f = int(self.cleanliness * 10)
        return "[" + "#" * f + "-" * (10 - f) + "]"

    def status_line(self):
        kind = "Indoor " if self.indoor else "Outdoor"
        return (f"  {self.name:<22}  {kind}  "
                f"Visitors {self.current_visitors:>3}/{self.capacity:<4} "
                f"{self.capacity_bar()}  {self.utilization():>5}%  "
                f"Clean {self.clean_bar()} {self.cleanliness:.2f}  "
                f"Pop {self.popularity}/10  "
                f"Base dwell ~{self.base_dwell_time()} min")

#─#─ Pattern 2 ───────────────────────────────────────────────────────────────────

class AbstractZoneFactory:
    def create_exhibit(self) -> Exhibit:
        raise NotImplementedError

    def create_animals(self, exhibit) -> list:
        raise NotImplementedError

    def create_zone(self):
        """Template method — returns (exhibit, [animals])."""
        exhibit = self.create_exhibit()
        animals = self.create_animals(exhibit)
        log("ABSTRACT_F",
            f"Zone built: {exhibit.name:<22}  {len(animals)} animals placed", CYAN)
        return exhibit, animals


class SavannahFactory(AbstractZoneFactory):
    def create_exhibit(self):
        return Exhibit("Savannah Enclosure", capacity=150, popularity=9, indoor=False)

    def create_animals(self, exhibit):
        from animals import AnimalFactory
        return [
            AnimalFactory.create("Lion", "Simba", 5, exhibit.name),
            AnimalFactory.create("Lion", "Nala", 4, exhibit.name),
            AnimalFactory.create("Tiger", "Raja", 18, exhibit.name),
            AnimalFactory.create("Zebra", "Stripes", 3, exhibit.name),
        ]


class AquaticFactory(AbstractZoneFactory):
    def create_exhibit(self):
        return Exhibit("Aquarium", capacity=80, popularity=7, indoor=True)

    def create_animals(self, exhibit):
        from animals import AnimalFactory
        return [
            AnimalFactory.create("Shark", "Jaws", 15, exhibit.name),
            AnimalFactory.create("Clownfish", "Nemo", 2, exhibit.name),
            AnimalFactory.create("Stingray", "Ray", 5, exhibit.name),
            AnimalFactory.create("Seahorse", "Poseidon", 3, exhibit.name),
        ]


class PrimateFactory(AbstractZoneFactory):
    def create_exhibit(self):
        return Exhibit("Primate Zone", capacity=100, popularity=8, indoor=False)

    def create_animals(self, exhibit):
        from animals import AnimalFactory
        return [
            AnimalFactory.create("Monkey", "Chico", 4, exhibit.name),
            AnimalFactory.create("Monkey", "Coco", 14, exhibit.name),
        ]

#─#─ Pattern 6 ───────────────────────────────────────────────────────────────────

class ExhibitComponent:
    def status_line(self):  raise NotImplementedError
    def utilization(self):  raise NotImplementedError
    def clean(self):        raise NotImplementedError


class ExhibitGroup(ExhibitComponent):
    def __init__(self, name):
        self.name = name
        self._children = []

    def add(self, exhibit):
        self._children.append(exhibit)

    def remove(self, exhibit):
        self._children.remove(exhibit)

    def utilization(self):
        if not self._children:
            return 0.0
        return round(
            sum(e.utilization() for e in self._children) / len(self._children), 1)

    def clean(self):
        for exhibit in self._children:
            exhibit.clean()
        log("COMPOSITE",
            f"Group '{self.name}' cleaned — {len(self._children)} exhibit(s).", GREEN)

    def status_line(self):
        lines = [f"  {BOLD}[GROUP] {self.name}{RESET}  "
                 f"Avg Utilization: {self.utilization()}%"]
        for ex in self._children:
            lines.append("  " + ex.status_line().strip())
        return "\n".join(lines)

    def __iter__(self):
        return iter(self._children)

    def __len__(self):
        return len(self._children)

#─#─ Pattern 10 ───────────────────────────────────────────────────────────────────

class ExhibitIterator: # supported orders: 'popularity', 'utilization', 'capacity', 'name'

    ORDERS = {
        "popularity": lambda e: e.popularity,
        "utilization": lambda e: e.utilization(),
        "capacity": lambda e: e.capacity,
        "name": lambda e: e.name,
    }

    def __init__(self, exhibits, order="popularity", reverse=True):
        if order not in self.ORDERS:
            raise ValueError(
                f"ExhibitIterator: unknown order '{order}'. "
                f"Choose from {list(self.ORDERS)}")
        self._sorted = sorted(exhibits, key=self.ORDERS[order], reverse=reverse)
        self._index = 0
        self._order = order

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._sorted):
            raise StopIteration
        exhibit = self._sorted[self._index]
        self._index += 1
        return exhibit

    def reset(self):
        self._index = 0

    def print_order(self):
        log("ITERATOR",
            f"Exhibit traversal order: {self._order.upper()}", BLUE)
        for i, ex in enumerate(self._sorted, 1):
            val = self.ORDERS[self._order](ex)
            print(f"  {i:>2}.  {ex.name:<26}  {self._order}: {val}")
