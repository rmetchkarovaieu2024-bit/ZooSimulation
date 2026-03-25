# exhibits.py
# ─────────────────────────────────────────────────────────────────────────────
#  EXHIBIT
#  Popularity (1-10) drives:
#    - How many visitors choose this exhibit (weighted random selection)
#    - Base dwell time: dwell = 3 + popularity * 1.5  (minutes, randomised ±2)
# ─────────────────────────────────────────────────────────────────────────────

import random
import threading
from utils import GREEN, YELLOW, RED, RESET


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
