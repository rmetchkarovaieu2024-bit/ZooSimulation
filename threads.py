# threads.py
# ─────────────────────────────────────────────────────────────────────────────
#  SIMULATION THREADS
#
#  ZooSimulation      top-level controller
#  ├── ClockThread         global tick counter
#  ├── ExhibitThread       one per exhibit — decays cleanliness each tick
#  ├── AnimalThread        one per animal  — increments hunger each tick
#  ├── VisitorThread       one per visitor — drives journey logic
#  └── WorkerThread        one per worker  — dispatches tasks each tick
#       ├── CleanerThread
#       ├── FeederThread
#       ├── TicketSellerThread
#       ├── ShopEmployeeThread
#       └── SecurityThread
# ─────────────────────────────────────────────────────────────────────────────

import threading
import time
import random
from utils import log, section, blank, rule, WHITE, RED, YELLOW, GREEN, CYAN, BLUE, GREY


# ─────────────────────────────────────────────────────────────────────────────
#  CLOCK THREAD
# ─────────────────────────────────────────────────────────────────────────────

class ClockThread(threading.Thread):
    """
    Global simulation clock.
    Each tick represents one time unit.
    tick_interval controls real-world seconds per tick.
    """
    def __init__(self, total_ticks=10, tick_interval=0.05):
        super().__init__(daemon=True)
        self.tick          = 0
        self.total_ticks   = total_ticks
        self.tick_interval = tick_interval
        self._stop_event   = threading.Event()

    def run(self):
        while self.tick < self.total_ticks and not self._stop_event.is_set():
            time.sleep(self.tick_interval)
            self.tick += 1

    def stop(self):
        self._stop_event.set()

    def is_done(self):
        return self.tick >= self.total_ticks


# ─────────────────────────────────────────────────────────────────────────────
#  EXHIBIT THREAD
# ─────────────────────────────────────────────────────────────────────────────

class ExhibitThread(threading.Thread):
    """
    Manages one exhibit.
    Each tick: cleanliness decays proportional to visitor count.
    """
    DECAY_PER_VISITOR_PER_TICK = 0.003

    def __init__(self, exhibit, clock):
        super().__init__(daemon=True)
        self.exhibit = exhibit
        self.clock   = clock

    def run(self):
        last_tick = -1
        while not self.clock.is_done():
            if self.clock.tick != last_tick:
                last_tick = self.clock.tick
                decay = self.DECAY_PER_VISITOR_PER_TICK * self.exhibit.current_visitors
                self.exhibit.cleanliness = max(
                    0.0, round(self.exhibit.cleanliness - decay, 3))
            time.sleep(0.01)


# ─────────────────────────────────────────────────────────────────────────────
#  ANIMAL THREAD
# ─────────────────────────────────────────────────────────────────────────────

class AnimalThread(threading.Thread):
    """
    Manages one animal.
    Each tick: hunger increases slightly.
    Older animals (lower health) get hungry faster.
    """
    BASE_HUNGER_RATE = 0.01

    def __init__(self, animal, clock):
        super().__init__(daemon=True)
        self.animal = animal
        self.clock  = clock

    def run(self):
        last_tick = -1
        while not self.clock.is_done():
            if self.clock.tick != last_tick:
                last_tick = self.clock.tick
                # Older (less healthy) animals get hungry faster
                rate = self.BASE_HUNGER_RATE * (2.0 - self.animal.health)
                self.animal.hunger_level = min(
                    1.0, round(self.animal.hunger_level + rate, 3))
            time.sleep(0.01)


# ─────────────────────────────────────────────────────────────────────────────
#  VISITOR THREAD
# ─────────────────────────────────────────────────────────────────────────────

class VisitorThread(threading.Thread):
    """
    Drives a single visitor's journey through the zoo.

    Exhibit selection:
      - Weighted random by popularity — more popular = more likely to be chosen
      - Children: can revisit; skip full-exhibit check on revisit
      - Seniors: spend more time (dwell_mult = 1.6, applied inside visitor.watch_exhibit)
      - Full exhibits: queued visitors skip and log a miss

    The visitor selects a candidate exhibit list, then walks through it.
    """
    def __init__(self, visitor, exhibits, shop_employee, zoo):
        super().__init__(daemon=True)
        self.visitor      = visitor
        self.exhibits     = exhibits
        self.shop_emp     = shop_employee
        self.zoo          = zoo

    def run(self):
        v       = self.visitor
        blank()
        rule()
        log("JOURNEY",
            f"Visitor: {v.name}   Subtype: {v.subtype}   Age: {v.age}   "
            f"Energy: {v.energy:.2f}   Balance: EUR {v.money:.2f}", WHITE)
        rule()

        # Weighted exhibit selection by popularity
        weights  = [e.popularity for e in self.exhibits]
        n_visits = random.randint(3, 5)

        visited_this_trip = []
        for _ in range(n_visits):
            if v.energy <= 0.1:
                log("VISITOR", f"{v.name:<10}  Energy depleted. Heading to exit.", GREY)
                break

            # Pick exhibit weighted by popularity
            chosen = random.choices(self.exhibits, weights=weights, k=1)[0]

            # Non-kids skip already-visited exhibits
            if v.has_visited(chosen.name):
                log("QUEUE",
                    f"{v.name:<10}  Already visited {chosen.name} -- skipping.", GREY)
                continue

            if chosen.is_full():
                log("QUEUE",
                    f"{v.name:<10}  Exhibit at capacity -- skipping: {chosen.name}", RED)
                continue

            v.move(chosen.name)
            chosen.add_visitor()
            v.watch_exhibit(chosen)
            chosen.remove_visitor()
            visited_this_trip.append(chosen.name)

            # Food stop: Seniors more likely (0.45), others 0.3
            food_prob = 0.45 if v.subtype == "Senior" else 0.30
            if random.random() < food_prob:
                v.move("Food Court")
                v.buy_food()
                self.zoo.revenue += random.uniform(5, 15)

            # Shop stop
            if random.random() < 0.25:
                v.move("Gift Shop")
                self.shop_emp.sell_item(v)
                self.zoo.revenue += random.uniform(5, 25)

        v.leave_zoo()


# ─────────────────────────────────────────────────────────────────────────────
#  WORKER THREADS
# ─────────────────────────────────────────────────────────────────────────────

class WorkerThread(threading.Thread):
    """Base worker thread — override run() per role."""
    def __init__(self, worker, clock):
        super().__init__(daemon=True)
        self.worker = worker
        self.clock  = clock


class CleanerThread(WorkerThread):
    def __init__(self, worker, exhibits, clock):
        super().__init__(worker, clock)
        self.exhibits = exhibits

    def run(self):
        last_tick = -1
        while not self.clock.is_done():
            if self.clock.tick != last_tick and self.clock.tick % 3 == 0:
                last_tick = self.clock.tick
                for ex in self.exhibits:
                    if ex.cleanliness < 0.65:
                        self.worker.move(ex.name)
                        self.worker.clean_exhibit(ex)
            time.sleep(0.05)
        # Final sweep
        self.worker.clean_restroom()
        self.worker.clean_path("Main Promenade")
        self.worker.clean_path("North Walkway")


class FeederThread(WorkerThread):
    def __init__(self, worker, exhibits, clock):
        super().__init__(worker, clock)
        self.exhibits = exhibits

    def run(self):
        last_tick = -1
        while not self.clock.is_done():
            if self.clock.tick != last_tick and self.clock.tick % 2 == 0:
                last_tick = self.clock.tick
                for ex in self.exhibits:
                    for animal in ex.animals:
                        if animal.hunger_level > 0.6:
                            self.worker.feed_animals(ex)
                            break
            time.sleep(0.05)
        self.worker.check_food_stock()


class TicketSellerThread(WorkerThread):
    def __init__(self, worker, visitors, zoo, clock):
        super().__init__(worker, clock)
        self.visitors = visitors
        self.zoo      = zoo

    def run(self):
        section("5. VISITOR ARRIVALS")
        blank()
        for v in self.visitors:
            self.worker.validate_ticket(v)
            price = v.buy_ticket()
            self.zoo.revenue += price
            self.zoo.visitors.append(v)
            time.sleep(0.05)


class ShopEmployeeThread(WorkerThread):
    def run(self):
        while not self.clock.is_done():
            time.sleep(0.1)
        self.worker.restock_shop()


class SecurityThread(WorkerThread):
    ZONES = ["North Zone", "East Zone", "South Zone", "West Zone", "Central Plaza"]
    INCIDENTS = [
        "Unattended baggage near Reptile House entrance",
        "Visitor attempting to feed restricted animals",
        "Crowd disturbance near Aquarium exit",
        "Lost child reported near Primate Zone",
    ]

    def __init__(self, worker, exhibits, clock):
        super().__init__(worker, clock)
        self.exhibits = exhibits

    def run(self):
        last_tick = -1
        while not self.clock.is_done():
            if self.clock.tick != last_tick and self.clock.tick % 4 == 0:
                last_tick = self.clock.tick
                zone = random.choice(self.ZONES)
                self.worker.patrol(zone)
                for ex in self.exhibits:
                    if ex.utilization() > 75:
                        self.worker.control_crowd(ex)
            time.sleep(0.05)
        # End-of-day incident check
        if random.random() < 0.65:
            self.worker.handle_incident(random.choice(self.INCIDENTS))


# ─────────────────────────────────────────────────────────────────────────────
#  ZOO SIMULATION CONTROLLER
# ─────────────────────────────────────────────────────────────────────────────

class ZooSimulation:
    """
    Orchestrates all threads.
    Call .run() to execute the full simulation.
    """

    def __init__(self, zoo, exhibits, all_animals, all_visitors, all_workers,
                 total_ticks=12, tick_interval=0.04):
        self.zoo          = zoo
        self.exhibits     = exhibits
        self.all_animals  = all_animals
        self.all_visitors = all_visitors
        self.all_workers  = all_workers
        self.total_ticks  = total_ticks
        self.tick_interval= tick_interval

        # Unpack workers by role
        self.cleaner  = next(w for w in all_workers if w.role == "Cleaner")
        self.feeder   = next(w for w in all_workers if w.role == "Feeder")
        self.ticketer = next(w for w in all_workers if w.role == "Ticketero")
        self.shop_emp = next(w for w in all_workers if w.role == "Shop Employee")
        self.security = next(w for w in all_workers if w.role == "Security")

    def run(self):
        clock = ClockThread(self.total_ticks, self.tick_interval)

        # Build thread pool
        exhibit_threads  = [ExhibitThread(ex, clock)        for ex in self.exhibits]
        animal_threads   = [AnimalThread(a, clock)           for a in self.all_animals]
        worker_threads   = [
            CleanerThread     (self.cleaner,  self.exhibits,                    clock),
            FeederThread      (self.feeder,   self.exhibits,                    clock),
            TicketSellerThread(self.ticketer, self.all_visitors, self.zoo,      clock),
            ShopEmployeeThread(self.shop_emp,                                   clock),
            SecurityThread    (self.security, self.exhibits,                    clock),
        ]
        visitor_threads  = [
            VisitorThread(v, self.exhibits, self.shop_emp, self.zoo)
            for v in self.all_visitors
        ]

        # Start infrastructure threads
        clock.start()
        for t in exhibit_threads + animal_threads:
            t.start()

        # Ticket selling (sequential, before visitors enter)
        worker_threads[2].start()   # TicketSellerThread
        worker_threads[2].join()

        # Start remaining worker threads
        for t in [worker_threads[0], worker_threads[1], worker_threads[3], worker_threads[4]]:
            t.start()

        # Visitor journeys (sequential for clean terminal output)
        section("8. VISITOR JOURNEYS")
        for t in visitor_threads:
            t.start()
            t.join()

        # Let clock finish
        clock.join()

        # Finish worker threads
        for t in [worker_threads[0], worker_threads[1], worker_threads[3], worker_threads[4]]:
            t.join(timeout=1)
