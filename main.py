import random
import time
import threading
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
#  TERMINAL FORMATTING
# ─────────────────────────────────────────────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
WHITE  = "\033[97m"
CYAN   = "\033[36m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
RED    = "\033[31m"
BLUE   = "\033[34m"
GREY   = "\033[90m"

W = 72


def header(title):
    print()
    print(f"{BOLD}{'=' * W}{RESET}")
    print(f"{BOLD}  {title}{RESET}")
    print(f"{BOLD}{'=' * W}{RESET}")
    print()


def section(title):
    print()
    print(f"{CYAN}{BOLD}  {title}{RESET}")
    print(f"{CYAN}  {'─' * (W - 2)}{RESET}")


def log(tag, msg, color=RESET):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"  {GREY}[{ts}]{RESET}  {color}{BOLD}[{tag:<12}]{RESET}  {msg}")


def rule():
    print(f"  {GREY}{'·' * (W - 2)}{RESET}")


def blank():
    print()


# ─────────────────────────────────────────────────────────────────────────────
#  ANIMAL HIERARCHY
# ─────────────────────────────────────────────────────────────────────────────

class Animal:
    category = "Animal"

    def __init__(self, name, species, age, exhibit_name):
        self.id            = random.randint(1000, 9999)
        self.name          = name
        self.species       = species
        self.age           = age
        self.health_status = "Healthy"
        self.hunger_level  = round(random.uniform(0.1, 0.6), 2)
        self.exhibit_name  = exhibit_name

    def eat(self):
        self.hunger_level = max(0.0, round(self.hunger_level - 0.3, 2))
        log("ANIMAL", f"{self.name:<14} ({self.species:<12})  Fed.   Hunger: {self.hunger_level:.2f}", YELLOW)

    def sleep(self):
        log("ANIMAL", f"{self.name:<14} ({self.species:<12})  Resting.", GREY)

    def make_sound(self):
        sounds = {
            "Lion": "roar", "Elephant": "trumpet", "Tiger": "growl",
            "Monkey": "chatter", "Zebra": "bark",
            "Parrot": "squawk", "Eagle": "screech", "Penguin": "honk",
            "Flamingo": "call", "Owl": "hoot",
            "Snake": "hiss", "Crocodile": "bellow", "Turtle": "hiss",
            "Lizard": "chirp", "Chameleon": "--",
            "Frog": "croak", "Toad": "croak", "Salamander": "--",
            "Newt": "--", "Axolotl": "--",
            "Shark": "--", "Clownfish": "--", "Goldfish": "--",
            "Stingray": "--", "Seahorse": "--",
        }
        sound = sounds.get(self.species, "--")
        log("ANIMAL", f"{self.name:<14} ({self.species:<12})  Sound: [{sound}]", YELLOW)

    def move_inside_exhibit(self):
        log("ANIMAL", f"{self.name:<14} moves within {self.exhibit_name}.", GREY)

    def hunger_bar(self):
        filled = int(self.hunger_level * 10)
        return "[" + "#" * filled + "-" * (10 - filled) + "]"

    def status_line(self):
        return (f"  {self.id:<6}  {self.name:<14}  {self.species:<14}  "
                f"Age {self.age:>3}   Hunger {self.hunger_bar()} {self.hunger_level:.2f}   "
                f"{self.health_status}")


# ── Mammals ───────────────────────────────────────────────────────────────────

class Mammal(Animal):
    category = "Mammal"

class Lion(Mammal):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Lion", age, exhibit_name)

class Elephant(Mammal):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Elephant", age, exhibit_name)

class Tiger(Mammal):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Tiger", age, exhibit_name)

class Monkey(Mammal):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Monkey", age, exhibit_name)

class Zebra(Mammal):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Zebra", age, exhibit_name)


# ── Birds ─────────────────────────────────────────────────────────────────────

class Bird(Animal):
    category = "Bird"

class Parrot(Bird):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Parrot", age, exhibit_name)

class Eagle(Bird):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Eagle", age, exhibit_name)

class Penguin(Bird):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Penguin", age, exhibit_name)

class Flamingo(Bird):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Flamingo", age, exhibit_name)

class Owl(Bird):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Owl", age, exhibit_name)


# ── Reptiles ──────────────────────────────────────────────────────────────────

class Reptile(Animal):
    category = "Reptile"

class Snake(Reptile):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Snake", age, exhibit_name)

class Crocodile(Reptile):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Crocodile", age, exhibit_name)

class Turtle(Reptile):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Turtle", age, exhibit_name)

class Lizard(Reptile):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Lizard", age, exhibit_name)

class Chameleon(Reptile):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Chameleon", age, exhibit_name)


# ── Amphibians ────────────────────────────────────────────────────────────────

class Amphibian(Animal):
    category = "Amphibian"

class Frog(Amphibian):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Frog", age, exhibit_name)

class Toad(Amphibian):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Toad", age, exhibit_name)

class Salamander(Amphibian):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Salamander", age, exhibit_name)

class Newt(Amphibian):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Newt", age, exhibit_name)

class Axolotl(Amphibian):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Axolotl", age, exhibit_name)


# ── Fish ──────────────────────────────────────────────────────────────────────

class Fish(Animal):
    category = "Fish"

class Shark(Fish):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Shark", age, exhibit_name)

class Clownfish(Fish):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Clownfish", age, exhibit_name)

class Goldfish(Fish):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Goldfish", age, exhibit_name)

class Stingray(Fish):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Stingray", age, exhibit_name)

class Seahorse(Fish):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Seahorse", age, exhibit_name)


# ─────────────────────────────────────────────────────────────────────────────
#  EXHIBIT
# ─────────────────────────────────────────────────────────────────────────────

class Exhibit:
    def __init__(self, name, capacity, popularity, indoor=False):
        self.id               = random.randint(100, 999)
        self.name             = name
        self.capacity         = capacity
        self.popularity       = popularity
        self.indoor           = indoor
        self.animals          = []
        self.current_visitors = 0
        self.cleanliness      = round(random.uniform(0.7, 1.0), 2)
        self._lock            = threading.Lock()

    def add_animal(self, animal):
        self.animals.append(animal)

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

    def clean(self):
        self.cleanliness = 1.0

    def utilization(self):
        return round(self.current_visitors / self.capacity * 100, 1)

    def capacity_bar(self):
        filled = int(self.current_visitors / self.capacity * 20)
        color  = RED if self.utilization() > 80 else YELLOW if self.utilization() > 50 else GREEN
        return f"{color}[{'#' * filled + '-' * (20 - filled)}]{RESET}"

    def clean_bar(self):
        filled = int(self.cleanliness * 10)
        return "[" + "#" * filled + "-" * (10 - filled) + "]"

    def status_line(self):
        kind = "Indoor " if self.indoor else "Outdoor"
        return (f"  {self.name:<22}  {kind}  "
                f"Visitors {self.current_visitors:>3}/{self.capacity:<4} "
                f"{self.capacity_bar()}  {self.utilization():>5}%  "
                f"Clean {self.clean_bar()} {self.cleanliness:.2f}  "
                f"Pop {self.popularity}/10")


# ─────────────────────────────────────────────────────────────────────────────
#  VISITOR HIERARCHY
# ─────────────────────────────────────────────────────────────────────────────

class Visitor:
    def __init__(self, name, age):
        self.id               = random.randint(10000, 99999)
        self.name             = name
        self.age              = age
        self.subtype          = self._classify()
        self.ticket_type      = "School" if self.subtype == "Student" else "Standard"
        self.satisfaction     = round(random.uniform(0.6, 0.9), 2)
        self.energy           = round(random.uniform(0.7, 1.0), 2)
        self.money            = round(random.uniform(20, 80), 2)
        self.current_location = "Entrance"
        self.exhibits_visited = []

    def _classify(self):
        if self.age < 12:  return "Child"
        if self.age > 60:  return "Senior"
        if self.age < 22:  return "Student"
        return "Adult"

    def move(self, destination):
        penalty = 0.08 if self.subtype == "Senior" else 0.05
        self.energy = max(0.0, round(self.energy - penalty, 2))
        self.current_location = destination
        log("VISITOR", f"{self.name:<10} ({self.subtype:<7})  ->  {destination:<24}  Energy: {self.energy:.2f}", BLUE)

    def watch_exhibit(self, exhibit_name):
        dwell = random.randint(5, 15)
        self.satisfaction = min(1.0, round(self.satisfaction + random.uniform(0.02, 0.08), 2))
        self.exhibits_visited.append(exhibit_name)
        log("VISITOR", f"{self.name:<10}  Watching {exhibit_name:<24}  Dwell: {dwell} min   Satisfaction: {self.satisfaction:.2f}", BLUE)

    def buy_food(self):
        cost = round(random.uniform(5, 15), 2)
        self.money  = round(self.money - cost, 2)
        self.energy = min(1.0, round(self.energy + 0.15, 2))
        log("VISITOR", f"{self.name:<10}  Food purchase   EUR {cost:.2f}   Balance: EUR {self.money:.2f}", BLUE)

    def buy_ticket(self):
        price = 8.0 if self.subtype == "Child" else 5.0 if self.subtype == "Senior" else 12.0
        log("TICKET", f"{self.name:<10}  Type: {self.ticket_type:<10}  Price: EUR {price:.2f}", CYAN)
        return price

    def leave_zoo(self):
        log("VISITOR", f"{self.name:<10}  Exit.   Exhibits: {len(self.exhibits_visited):<3}  "
            f"Satisfaction: {self.satisfaction:.2f}   Energy: {self.energy:.2f}", BLUE)


class RegularVisitor(Visitor):
    pass

class KidsVisitor(Visitor):
    pass

class SeniorVisitor(Visitor):
    pass

class StudentVisitor(Visitor):
    pass


# ─────────────────────────────────────────────────────────────────────────────
#  WORKER HIERARCHY
# ─────────────────────────────────────────────────────────────────────────────

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
        log("WORKER", f"{self.name:<12}  Role: {self.role:<16}  Shift: {self.shift_start}-{self.shift_end}   "
            f"Salary: EUR {self.salary}/mo  [START]", GREEN)

    def end_shift(self):
        log("WORKER", f"{self.name:<12}  Role: {self.role:<16}  [END OF SHIFT]", GREY)

    def move(self, location):
        self.current_location = location
        log("WORKER", f"{self.name:<12}  Relocating to: {location}", GREY)

    def perform_task(self, task):
        log("WORKER", f"{self.name:<12}  Task: {task}", GREY)


class Cleaner(Worker):
    def __init__(self, name):
        super().__init__(name, "Cleaner", "08:00", "16:00", 1200)

    def clean_exhibit(self, exhibit):
        exhibit.clean()
        log("CLEANER", f"{self.name:<12}  Cleaned: {exhibit.name:<24}  Cleanliness: 1.00", GREEN)

    def clean_path(self, path):
        log("CLEANER", f"{self.name:<12}  Cleaned path: {path}", GREEN)

    def clean_restroom(self):
        log("CLEANER", f"{self.name:<12}  Cleaned restrooms.", GREEN)


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
        log("FEEDER", f"{self.name:<12}  Food stock level: {color}{pct}%{RESET}", YELLOW)


class Ticketero(Worker):
    def __init__(self, name):
        super().__init__(name, "Ticketero", "09:00", "18:00", 1300)

    def sell_ticket(self, visitor):
        return visitor.buy_ticket()

    def validate_ticket(self, visitor):
        log("TICKET", f"{self.name:<12}  Validated for {visitor.name:<10}  [OK]", CYAN)


class ShopEmployee(Worker):
    ITEMS = ["Plush toy", "Zoo map", "Keychain", "Cap", "Mug", "Poster", "Guidebook"]

    def __init__(self, name):
        super().__init__(name, "Shop Employee", "10:00", "19:00", 1100)

    def sell_item(self, visitor):
        item = random.choice(self.ITEMS)
        cost = round(random.uniform(5, 25), 2)
        visitor.money = round(visitor.money - cost, 2)
        log("SHOP", f"{self.name:<12}  Sold '{item}' to {visitor.name:<10}   EUR {cost:.2f}", YELLOW)

    def restock_shop(self):
        log("SHOP", f"{self.name:<12}  Shop restocked.", YELLOW)


class Security(Worker):
    def __init__(self, name):
        super().__init__(name, "Security", "08:00", "20:00", 1500)

    def patrol(self, zone):
        log("SECURITY", f"{self.name:<12}  Patrolling zone: {zone}", RED)

    def control_crowd(self, exhibit):
        log("SECURITY", f"{self.name:<12}  Crowd management at {exhibit.name:<22}  "
            f"Occupancy: {exhibit.current_visitors}/{exhibit.capacity}", RED)

    def handle_incident(self, description):
        log("SECURITY", f"{self.name:<12}  Incident: {description}", RED)


# ─────────────────────────────────────────────────────────────────────────────
#  TICKET
# ─────────────────────────────────────────────────────────────────────────────

class Ticket:
    def __init__(self, visitor):
        self.id           = random.randint(100000, 999999)
        self.visitor_type = visitor.subtype
        self.valid_date   = datetime.now().strftime("%Y-%m-%d")
        self.price        = (8.0  if visitor.subtype == "Child"  else
                             5.0  if visitor.subtype == "Senior" else 12.0)

    def validate_ticket(self):
        return True


# ─────────────────────────────────────────────────────────────────────────────
#  ZOO
# ─────────────────────────────────────────────────────────────────────────────

class Zoo:
    def __init__(self, name):
        self.name     = name
        self.exhibits = []
        self.workers  = []
        self.visitors = []
        self.revenue  = 0.0

    def add_exhibit(self, exhibit):
        self.exhibits.append(exhibit)
        log("ZOO", f"Registered: {exhibit.name:<22}  Capacity: {exhibit.capacity:<4}  "
            f"Popularity: {exhibit.popularity}/10  {'Indoor' if exhibit.indoor else 'Outdoor'}", GREEN)

    def open_zoo(self):
        log("ZOO", f"{self.name}  --  STATUS: OPEN", GREEN)

    def close_zoo(self):
        log("ZOO", f"{self.name}  --  STATUS: CLOSED", RED)

    def kpi_report(self):
        section("END-OF-DAY KPI REPORT")
        blank()
        total    = len(self.visitors)
        avg_sat  = round(sum(v.satisfaction for v in self.visitors) / max(1, total), 2)
        avg_nrg  = round(sum(v.energy       for v in self.visitors) / max(1, total), 2)
        lost     = sum(1 for v in self.visitors if v.energy < 0.2)
        busiest  = max(self.exhibits, key=lambda e: e.current_visitors) if self.exhibits else None
        util_avg = round(sum(e.utilization() for e in self.exhibits) / max(1, len(self.exhibits)), 1)

        rows = [
            ("Total Visitors",               str(total)),
            ("Avg Satisfaction Score",        f"{avg_sat:.2f} / 1.00"),
            ("Avg Energy at Exit",            f"{avg_nrg:.2f} / 1.00"),
            ("Lost Visitors (energy < 0.2)",  str(lost)),
            ("Avg Exhibit Utilization",       f"{util_avg} %"),
            ("Total Revenue (EUR)",           f"{self.revenue:.2f}"),
            ("Busiest Exhibit",               busiest.name if busiest else "N/A"),
        ]
        print(f"  {'Metric':<36}  Value")
        print(f"  {'─' * 36}  {'─' * 20}")
        for label, value in rows:
            print(f"  {label:<36}  {value}")
        blank()


# ─────────────────────────────────────────────────────────────────────────────
#  SIMULATION
# ─────────────────────────────────────────────────────────────────────────────

def run_simulation():
    header("ZOO OPERATIONS SYSTEM SIMULATION  |  TERMINAL MODE")
    print(f"  Start  : {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}")
    print(f"  Engine : Agent-Based + Discrete-Event  |  Language: Python")
    blank()
    time.sleep(0.3)

    # ── 1. INITIALISE ZOO ──────────────────────────────────────────────────────
    section("1. INITIALISING ZOO")
    zoo = Zoo("Safari World Zoo")

    exhibits_data = [
        ("Savannah Enclosure",  150, 9, False),
        ("Elephant Grounds",    200, 8, False),
        ("Tropical Bird House",  60, 7, True),
        ("Reptile House",        40, 6, True),
        ("Amphibian Centre",     35, 6, True),
        ("Aquarium",             80, 7, True),
        ("Primate Zone",        100, 8, False),
    ]
    exs = {}
    for name, cap, pop, indoor in exhibits_data:
        e = Exhibit(name, cap, pop, indoor)
        zoo.add_exhibit(e)
        exs[name] = e
    time.sleep(0.3)

    # ── 2. POPULATE ANIMALS ────────────────────────────────────────────────────
    section("2. POPULATING ANIMAL EXHIBITS")
    blank()
    print(f"  {'ID':<6}  {'Name':<14}  {'Species':<14}  {'Category':<12}  Exhibit")
    print(f"  {'─' * 68}")

    animals_config = [
        (Lion,        "Simba",    5,  "Savannah Enclosure"),
        (Lion,        "Nala",     4,  "Savannah Enclosure"),
        (Tiger,       "Raja",     6,  "Savannah Enclosure"),
        (Zebra,       "Stripes",  3,  "Savannah Enclosure"),
        (Elephant,    "Dumbo",   12,  "Elephant Grounds"),
        (Elephant,    "Nandita",  8,  "Elephant Grounds"),
        (Parrot,      "Polly",    3,  "Tropical Bird House"),
        (Eagle,       "Aquila",   7,  "Tropical Bird House"),
        (Penguin,     "Pebble",   4,  "Tropical Bird House"),
        (Flamingo,    "Rosa",     5,  "Tropical Bird House"),
        (Owl,         "Hoot",     6,  "Tropical Bird House"),
        (Snake,       "Viper",    4,  "Reptile House"),
        (Crocodile,   "Crunch",  15,  "Reptile House"),
        (Turtle,      "Shell",   20,  "Reptile House"),
        (Lizard,      "Gecko",    2,  "Reptile House"),
        (Chameleon,   "Kali",     3,  "Reptile House"),
        (Frog,        "Ribbit",   2,  "Amphibian Centre"),
        (Toad,        "Bumpy",    3,  "Amphibian Centre"),
        (Salamander,  "Sal",      4,  "Amphibian Centre"),
        (Newt,        "Newton",   2,  "Amphibian Centre"),
        (Axolotl,     "Axel",     1,  "Amphibian Centre"),
        (Shark,       "Jaws",     8,  "Aquarium"),
        (Clownfish,   "Nemo",     2,  "Aquarium"),
        (Goldfish,    "Goldie",   1,  "Aquarium"),
        (Stingray,    "Ray",      5,  "Aquarium"),
        (Seahorse,    "Poseidon", 3,  "Aquarium"),
        (Monkey,      "Chico",    4,  "Primate Zone"),
        (Monkey,      "Coco",     3,  "Primate Zone"),
    ]

    all_animals = []
    for AnimalClass, name, age, ex_name in animals_config:
        animal = AnimalClass(name, age, ex_name)
        exs[ex_name].add_animal(animal)
        all_animals.append(animal)
        print(f"  {animal.id:<6}  {animal.name:<14}  {animal.species:<14}  "
              f"{animal.category:<12}  {ex_name}")
    time.sleep(0.3)

    # ── 3. HIRE WORKERS ────────────────────────────────────────────────────────
    section("3. WORKER SHIFT REGISTRATION")
    blank()
    cleaner  = Cleaner      ("Maria"  )
    feeder   = Feeder       ("Carlos" )
    ticketer = Ticketero    ("Ana"    )
    shop_emp = ShopEmployee ("Pedro"  )
    security = Security     ("Marcos" )
    all_workers = [cleaner, feeder, ticketer, shop_emp, security]
    zoo.workers = all_workers
    for w in all_workers:
        w.start_shift()
    time.sleep(0.3)

    # ── 4. OPEN ZOO ────────────────────────────────────────────────────────────
    section("4. ZOO OPERATIONS")
    blank()
    zoo.open_zoo()
    time.sleep(0.3)

    # ── 5. VISITOR ARRIVALS ────────────────────────────────────────────────────
    section("5. VISITOR ARRIVALS")
    blank()
    visitor_config = [
        (RegularVisitor, "Lucas",    10),
        (RegularVisitor, "Sofia",    35),
        (SeniorVisitor,  "Javier",   68),
        (StudentVisitor, "Mia",      20),
        (KidsVisitor,    "Elena",     8),
        (RegularVisitor, "Marco",    42),
        (SeniorVisitor,  "Beatriz",  72),
        (StudentVisitor, "Daniel",   19),
        (RegularVisitor, "Carmen",   31),
        (KidsVisitor,    "Pablo",    11),
    ]
    all_visitors = []
    for VisitorClass, vname, age in visitor_config:
        v = VisitorClass(vname, age)
        ticketer.validate_ticket(v)
        price = v.buy_ticket()
        zoo.revenue += price
        zoo.visitors.append(v)
        all_visitors.append(v)
        time.sleep(0.05)
    time.sleep(0.3)

    # ── 6. MORNING EXHIBIT STATUS ──────────────────────────────────────────────
    section("6. EXHIBIT STATUS  --  MORNING")
    blank()
    for v in all_visitors:
        random.choice(zoo.exhibits).add_visitor()
    print(f"  {'Exhibit':<22}  {'Type':<8}  {'Occupancy':<14}  "
          f"{'Capacity Bar':<24}  {'Util':>5}  {'Clean Bar':<14}  Clean   Pop")
    print(f"  {'─' * 100}")
    for ex in zoo.exhibits:
        print(ex.status_line())
    time.sleep(0.3)

    # ── 7. FEEDING SHOW ────────────────────────────────────────────────────────
    section("7. SCHEDULED EVENT  --  FEEDING SHOW  (Savannah Enclosure)")
    blank()
    sav = exs["Savannah Enclosure"]
    log("EVENT", "Feeding show commencing. Visitor surge in progress.", YELLOW)
    for _ in range(8):
        sav.add_visitor()
    feeder.feed_animals(sav)
    for animal in sav.animals:
        animal.make_sound()
    if sav.utilization() > 60:
        security.control_crowd(sav)
    time.sleep(0.3)

    # ── 8. VISITOR JOURNEYS ────────────────────────────────────────────────────
    section("8. VISITOR JOURNEYS")
    for visitor in all_visitors:
        blank()
        rule()
        log("JOURNEY", f"Visitor: {visitor.name}   Subtype: {visitor.subtype}   Age: {visitor.age}   "
            f"Energy: {visitor.energy:.2f}   Balance: EUR {visitor.money:.2f}", WHITE)
        rule()
        ranked = sorted(zoo.exhibits,
                        key=lambda e: e.popularity + random.uniform(0, 3),
                        reverse=True)[:3]
        for exhibit in ranked:
            if exhibit.is_full():
                log("QUEUE", f"{visitor.name:<10}  Exhibit at capacity -- skipping: {exhibit.name}", RED)
                continue
            visitor.move(exhibit.name)
            exhibit.add_visitor()
            visitor.watch_exhibit(exhibit.name)
            exhibit.remove_visitor()
            if random.random() < 0.35:
                visitor.move("Food Court")
                visitor.buy_food()
                zoo.revenue += random.uniform(5, 15)
            if random.random() < 0.25:
                visitor.move("Gift Shop")
                shop_emp.sell_item(visitor)
                zoo.revenue += random.uniform(5, 25)
    time.sleep(0.3)

    # ── 9. MAINTENANCE ─────────────────────────────────────────────────────────
    section("9. MAINTENANCE ROUND")
    blank()
    for exhibit in zoo.exhibits:
        if exhibit.cleanliness < 0.80:
            cleaner.move(exhibit.name)
            cleaner.clean_exhibit(exhibit)
    cleaner.clean_restroom()
    cleaner.clean_path("Main Promenade")
    cleaner.clean_path("North Walkway")
    feeder.check_food_stock()
    time.sleep(0.3)

    # ── 10. AFTERNOON EXHIBIT STATUS ───────────────────────────────────────────
    section("10. EXHIBIT STATUS  --  AFTERNOON")
    blank()
    print(f"  {'Exhibit':<22}  {'Type':<8}  {'Occupancy':<14}  "
          f"{'Capacity Bar':<24}  {'Util':>5}  {'Clean Bar':<14}  Clean   Pop")
    print(f"  {'─' * 100}")
    for ex in zoo.exhibits:
        print(ex.status_line())
    time.sleep(0.3)

    # ── 11. ANIMAL STATUS ──────────────────────────────────────────────────────
    section("11. ANIMAL HEALTH & HUNGER STATUS")
    for cat in ["Mammal", "Bird", "Reptile", "Amphibian", "Fish"]:
        group = [a for a in all_animals if a.category == cat]
        if not group:
            continue
        blank()
        print(f"  {BOLD}{cat.upper()}{RESET}")
        print(f"  {'ID':<6}  {'Name':<14}  {'Species':<14}  {'Age':>4}   "
              f"{'Hunger Bar':<14}  {'Hunger':>7}   Health")
        print(f"  {'─' * 72}")
        for animal in group:
            print(animal.status_line())
            if animal.hunger_level > 0.5:
                for ex in zoo.exhibits:
                    if animal in ex.animals:
                        feeder.feed_animals(ex)
                        break
    time.sleep(0.3)

    # ── 12. SECURITY ───────────────────────────────────────────────────────────
    section("12. SECURITY OPERATIONS")
    blank()
    for zone in ["North Zone", "East Zone", "South Zone", "West Zone", "Central Plaza"]:
        security.patrol(zone)
    if random.random() < 0.65:
        security.handle_incident(random.choice([
            "Unattended baggage near Reptile House entrance",
            "Visitor attempting to feed restricted animals",
            "Crowd disturbance near Aquarium exit",
            "Lost child reported near Primate Zone",
        ]))
    shop_emp.restock_shop()
    time.sleep(0.3)

    # ── 13. VISITOR EXITS ──────────────────────────────────────────────────────
    section("13. VISITOR EXITS")
    blank()
    for visitor in all_visitors:
        visitor.leave_zoo()
    time.sleep(0.3)

    # ── 14. CLOSE ZOO ──────────────────────────────────────────────────────────
    section("14. END OF DAY  --  CLOSING PROCEDURES")
    blank()
    for w in all_workers:
        w.end_shift()
    zoo.close_zoo()
    time.sleep(0.3)

    # ── 15. KPI REPORT ─────────────────────────────────────────────────────────
    zoo.kpi_report()

    header("SIMULATION COMPLETE")
    print(f"  End: {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}")
    blank()


if __name__ == "__main__":
    run_simulation()