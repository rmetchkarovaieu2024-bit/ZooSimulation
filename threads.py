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
    Maps real elapsed seconds to simulation time 09:00 – 18:00.
     real_duration_seconds controls how long 9 sim-hours take in real time.
    """
    SIM_START_MIN = 9 * 60  # 09:00 in minutes from midnight
    SIM_END_MIN = 18 * 60  # 18:00
    SIM_DURATION = 540  # 9 hours in sim-minutes

    def __init__(self,real_duration_seconds=60):
        super().__init__(daemon=True)
        self.real_duration  = real_duration_seconds
        self._start_real = None
        self.tick          = 0
        #self.total_ticks   = total_ticks
        #self.tick_interval = tick_interval
        self._stop_event   = threading.Event()
        self._running = False

    # ── time properties ───────────────────────────────────────────────────────

    @property
    def sim_minute(self): #simulation minutes since 09:00 (0 – 540)
        if self._start_real is None:
            return 0
        elapsed = time.time() - self._start_real
        return min(int(elapsed / self.real_duration * self.SIM_DURATION),
                   self.SIM_DURATION)

    @property
    def sim_time_str(self):
        total = self.SIM_START_MIN + self.sim_minute
        return f"{total // 60:02d}:{total % 60:02d}"

    def real_second_for(self, arrival_minute):
        return arrival_minute / self.SIM_DURATION * self.real_duration

     # ── state checks ─────────────────────────────────────────────────────────

    def is_running(self):
        return self._running and not self._stop_event.is_set()


    def stop(self):
        self._stop_event.set()

    def is_done(self):
        return self._stop_event.is_set() or self.sim_minute >= self.SIM_DURATION

    # ── thread body ───────────────────────────────────────────────────────────

    def run(self):
        self._start_real = time.time()
        self._running = True

        announced = set()
        milestones = {
            0: "Zoo opens — 09:00",
            60: "10:00  — Morning rush begins",
            180: "12:00  — Midday peak",
            300: "15:00  — Afternoon wave",
            420: "16:00  — Closing in two hours",
            510: "17:30  — Last admissions",
            540: "18:00  — Zoo closes",
        }

        while not self._stop_event.is_set():
            time.sleep(0.05)
            self.tick += 1

            # Announce time milestones
            sm = self.sim_minute
            for threshold, label in milestones.items():
                if sm >= threshold and threshold not in announced:
                    announced.add(threshold)
                    log("CLOCK", f"{label}", CYAN)

            if sm >= self.SIM_DURATION:
                break



# ─────────────────────────────────────────────────────────────────────────────
#  EXHIBIT THREAD
# ─────────────────────────────────────────────────────────────────────────────

class ExhibitThread(threading.Thread):
    """
    Manages one exhibit.
    Each tick: cleanliness decays proportional to visitor count.
    """
    DECAY_PER_VISITOR_PER_TICK = 0.004

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
            time.sleep(0.02)


# ─────────────────────────────────────────────────────────────────────────────
#  ANIMAL THREAD
# ─────────────────────────────────────────────────────────────────────────────

class AnimalThread(threading.Thread):
    """
    Manages one animal.
    Each tick: hunger increases slightly.
    Older animals (lower health) get hungry faster.
    """
    BASE_HUNGER_RATE = 0.012

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
    def __init__(self, visitor, exhibits, shop_employee, zoo, clock, arrival_minute =0, db=None):
        super().__init__(daemon=True)
        self.visitor      = visitor
        self.exhibits     = exhibits
        self.shop_emp     = shop_employee
        self.zoo          = zoo
        self.clock       = clock
        self.arrival_minute = arrival_minute  # minutes after 09:00
        self.db = db
        self.money_start = visitor.money  # capture balance before any spend

    def run(self):
        v       = self.visitor

        # before onening
        if self.clock._start_real is not None:
            target_real = (self.clock._start_real
                           + self.clock.real_second_for(self.arrival_minute))
            wait = target_real - time.time()
            if wait > 0:
                time.sleep(wait)

        # on time
        price = 8.0 if v.subtype == "Child" else 5.0 if v.subtype == "Senior" else 12.0
        self.zoo.revenue += price
        self.zoo.visitors.append(v)
        log("ARRIVAL",
            f"{v.name:<10} ({v.subtype:<7}) arrives.  "
            f"Ticket: EUR {price:.2f}   Balance: EUR {v.money:.2f}", CYAN)

        # log initial state
        blank()
        rule()
        log("JOURNEY",
            f"Visitor: {v.name}   Subtype: {v.subtype}   Age: {v.age}   "
            f"Energy: {v.energy:.2f}   Balance: EUR {v.money:.2f}", WHITE)
        rule()

        # Weighted exhibit selection by popularity
        weights  = [e.popularity for e in self.exhibits]
        # Higher energy -> more exhibits visited.
        # energy 0.5 -> 2-3 visits, energy 0.75 -> 3-5, energy 1.0 -> 5-7
        n_visits =  max(2, min(7, int(v.energy * 6) + random.randint(0, 2)))

        for _ in range(n_visits):
            if v.energy <= 0.1:
                log("VISITOR",
                    f"{v.name:<10}  Energy depleted — heading to exit.", GREY)
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

            dwell_secs = v.dwell_time(chosen) * 0.15 # more realistic
            time.sleep(dwell_secs)
            chosen.remove_visitor()
            #visited_this_trip.append(chosen.name)

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

        if self.db:
            self.db.log_visitor(v,self.arrival_minute,self.money_start)


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
                    if ex.cleanliness < 0.60:
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
                        if animal.hunger_level > 0.65:
                            self.worker.feed_animals(ex)
                            break
            time.sleep(0.05)
        self.worker.check_food_stock()


class TicketSellerThread(WorkerThread):
    def __init__(self, worker, visitor_count, clock):
        super().__init__(worker, clock)
        self.visitor_count = visitor_count
    def run(self):
        log("TICKET",
            f"{self.worker.name:<12}  Gate open.  "
            f"Expecting {self.visitor_count} visitors today.", CYAN)

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
            if self.clock.tick != last_tick and self.clock.tick % 5 == 0:
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
#  LIFECYCLE THREAD  —  end-of-day death confirmation + procreation
# ─────────────────────────────────────────────────────────────────────────────

class LifecycleThread(threading.Thread):
    PROCREATION_CHANCE = 0.15

    OFFSPRING_NAMES = {
        "Lion":       ["Kion", "Kiara", "Nuka", "Vitani", "Taka"],
        "Elephant":   ["Ellie", "Tembo", "Jumbo", "Elba", "Trunky"],
        "Tiger":      ["Tigra", "Rajah", "Bangel", "Kira", "Shere"],
        "Monkey":     ["Bongo", "Momo", "Zazu", "Pip", "Koko"],
        "Zebra":      ["Zara", "Zed", "Ziggy", "Zola", "Stripe"],
        "Parrot":     ["Rio", "Coco", "Kiko", "Pico", "Lora"],
        "Eagle":      ["Talon", "Aria", "Hawk", "Storm", "Swoop"],
        "Penguin":    ["Waddle", "Frost", "Floe", "Slick", "Blizzard"],
        "Flamingo":   ["Blush", "Coral", "Pinky", "Rosie", "Flo"],
        "Owl":        ["Luna", "Shadow", "Sage", "Wren", "Hoot Jr"],
        "Shark":      ["Finn", "Chomp", "Reef", "Surge", "Jag"],
        "Frog":       ["Hoppy", "Leap", "Dart", "Puddle", "Splash"],
        "Toad":       ["Wart", "Bog", "Murk", "Toadie", "Bumble"],
        "Salamander": ["Slim", "Blaze", "Ember", "Ash", "Newbie"],
        "Axolotl":    ["Gilly", "Axie", "Ripple", "Wade", "Bubbles"],
        "Crocodile":  ["Snap", "Gnash", "Chomper", "Lurk", "Swamp"],
        "Snake":      ["Slither", "Coil", "Hiss Jr", "Venom", "Fang Jr"],
        "Turtle":     ["Shelly", "Mossy", "Pebble", "Dune", "Sandy"],
        "Lizard":     ["Dart", "Scale", "Spike", "Skitter", "Dash"],
        "Chameleon":  ["Chromie", "Pixel", "Hue", "Shade", "Tint"],
        "Clownfish":  ["Nemo Jr", "Bubbles", "Coral Jr", "Stripe Jr", "Finn Jr"],
        "Goldfish":   ["Flake", "Bubble", "Glitter", "Sunny", "Spark"],
        "Stingray":   ["Glide", "Skate", "Drifter", "Ray Jr", "Ripple Jr"],
        "Seahorse":   ["Tide", "Current", "Drift", "Brine", "Coral Jr"],
    }

    def __init__(self, exhibits, all_animals, db=None):
        super().__init__(daemon=True)
        self.exhibits    = exhibits
        self.all_animals = all_animals
        self.db          = db
        self.new_animals = []

    def run(self):
        from animals import clone_animal
        import random as _rand

        log("LIFECYCLE", "End-of-day lifecycle check...", YELLOW)

        for exhibit in self.exhibits:
            living  = [a for a in exhibit.animals if a.is_alive]
            checked = set()

            for i, a in enumerate(living):
                for b in living[i+1:]:
                    pair = tuple(sorted([a.name, b.name]))
                    if pair in checked:
                        continue
                    checked.add(pair)
                    if not a.can_procreate_with(b):
                        continue
                    if _rand.random() > self.PROCREATION_CHANCE:
                        continue

                    pool      = self.OFFSPRING_NAMES.get(a.species, ["Junior"])
                    taken     = {x.name for x in self.all_animals}
                    available = [n for n in pool if n not in taken]
                    name      = available[0] if available else f"{a.species}_cub"

                    offspring = clone_animal(a, new_name=name, new_age=0)
                    offspring.hunger_level = 0.1
                    exhibit.add_animal(offspring)
                    self.all_animals.append(offspring)
                    self.new_animals.append(offspring)

                    log("LIFECYCLE",
                        f"BIRTH  {a.species} '{name}'  "
                        f"parents: {a.name} x {b.name}  "
                        f"exhibit: {exhibit.name}", GREEN)

                    if self.db:
                        self.db.record_birth(offspring, mother=a, father=b)

        died  = sum(1 for a in self.all_animals if not a.is_alive)
        born  = len(self.new_animals)
        color = RED if died > 0 else YELLOW
        log("LIFECYCLE", f"Complete — Born: {born}  Died: {died}", color)



# ─────────────────────────────────────────────────────────────────────────────
#  ZOO SIMULATION CONTROLLER
# ─────────────────────────────────────────────────────────────────────────────

class ZooSimulation:
    def __init__(self, zoo, exhibits, all_animals, all_visitors, all_workers,
                 arrival_minutes, real_duration_seconds= 60, db=None):
        self.zoo                = zoo
        self.exhibits           = exhibits
        self.all_animals        = all_animals
        self.all_visitors       = all_visitors
        self.all_workers        = all_workers
        self.arrival_minutes    = arrival_minutes
        self.real_duration      = real_duration_seconds

        self.db                 = db

        # Unpack workers by role
        self.cleaner  = next(w for w in all_workers if w.role == "Cleaner")
        self.feeder   = next(w for w in all_workers if w.role == "Feeder")
        self.ticketer = next(w for w in all_workers if w.role == "Ticketero")
        self.shop_emp = next(w for w in all_workers if w.role == "Shop Employee")
        self.security = next(w for w in all_workers if w.role == "Security")

    def run(self):
        import utils
        clock = ClockThread(real_duration_seconds=self.real_duration)
        utils.set_sim_clock(clock)

        # Build thread pool
        exhibit_threads  = [ExhibitThread(ex, clock)        for ex in self.exhibits]
        animal_threads   = [AnimalThread(a, clock, db=self.db)           for a in self.all_animals]
        worker_threads   = [
            CleanerThread     (self.cleaner,  self.exhibits,                    clock),
            FeederThread      (self.feeder,   self.exhibits,                    clock),
            TicketSellerThread(self.ticketer, len(self.all_visitors),           clock),
            ShopEmployeeThread(self.shop_emp,                                   clock),
            SecurityThread    (self.security, self.exhibits,                    clock),
        ]
        visitor_threads  = [
            VisitorThread(v, self.exhibits, self.shop_emp, self.zoo , clock, arrival_minute=self.arrival_minutes[i], db=self.db)
            for i, v in enumerate(self.all_visitors)
        ]

        # Start infrastructure threads
        clock.start()
        for t in exhibit_threads + animal_threads + worker_threads:
            t.start()


 # Start ALL visitor threads — arrival times spread them across the day
        section("VISITOR ARRIVALS & JOURNEYS  (09:00 – 18:00)")
        for t in visitor_threads:
            t.start()

        # Wait for every visitor to finish their journey
        for t in visitor_threads:
            t.join()

            # End-of-day lifecycle: procreation + confirm deaths
        lifecycle = LifecycleThread(self.exhibits, self.all_animals, db=self.db)
        lifecycle.start()
        lifecycle.join()
        self.zoo._animals_died = sum(1 for a in self.all_animals if not a.is_alive)
        self.zoo._animals_born = len(lifecycle.new_animals)

        # Stop the clock; let worker/exhibit/animal threads wind down
        clock.stop()
        clock.join()
        for t in worker_threads + exhibit_threads + animal_threads:
            t.join(timeout=0.5)

        # Clear the global clock reference so post-sim logs show real time
        utils.set_sim_clock(None)
"""
        # Ticket selling (sequential, before visitors enter)
        worker_threads[2].start()   # TicketSellerThread
        worker_threads[2].join()

        # Start remaining worker threads
        for t in [worker_threads[0], worker_threads[1], worker_threads[3], worker_threads[4]]:
            t.start()

        # Visitor journeys (sequential for clean terminal output)
        section("8. VISITOR JOURNEYS")
        BATCH_SIZE = 10
        for batch_start in range(0, len(visitor_threads), BATCH_SIZE):
            batch = visitor_threads[batch_start: batch_start + BATCH_SIZE]
            for t in batch:
                t.start()
            for t in batch:
                t.join()

        # Let clock finish
        clock.join()

        # Finish worker threads
        for t in [worker_threads[0], worker_threads[1], worker_threads[3], worker_threads[4]]:
            t.join(timeout=1)
"""