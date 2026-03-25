# main.py
# ─────────────────────────────────────────────────────────────────────────────
#  ZOO OPERATIONS SYSTEM SIMULATION  |  ENTRY POINT
#  Run: python3 main.py
# ─────────────────────────────────────────────────────────────────────────────

import random
import time
from datetime import datetime

from utils    import header, section, log, blank, GREEN, RED, BOLD, RESET, CYAN
from animals  import (Lion, Elephant, Tiger, Monkey, Zebra,
                      Parrot, Eagle, Penguin, Flamingo, Owl,
                      Snake, Crocodile, Turtle, Lizard, Chameleon,
                      Frog, Toad, Salamander, Newt, Axolotl,
                      Shark, Clownfish, Goldfish, Stingray, Seahorse)
from exhibits import Exhibit
from visitors import RegularVisitor, KidsVisitor, SeniorVisitor, StudentVisitor
from workers  import Cleaner, Feeder, Ticketero, ShopEmployee, Security
from ticket   import Ticket
from zoo      import Zoo
from threads  import ZooSimulation


# ─────────────────────────────────────────────────────────────────────────────

def build_exhibits(zoo):
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
    return exs


def build_animals(exs):
    animals_config = [
        # Savannah — mix of young and old
        (Lion,        "Simba",    5,  "Savannah Enclosure"),
        (Lion,        "Nala",     4,  "Savannah Enclosure"),
        (Tiger,       "Raja",    18,  "Savannah Enclosure"),   # old tiger — frail
        (Zebra,       "Stripes",  3,  "Savannah Enclosure"),
        # Elephant Grounds
        (Elephant,    "Dumbo",   30,  "Elephant Grounds"),     # old elephant — aging
        (Elephant,    "Nandita",  8,  "Elephant Grounds"),
        # Bird House
        (Parrot,      "Polly",    3,  "Tropical Bird House"),
        (Eagle,       "Aquila",  22,  "Tropical Bird House"),  # old eagle
        (Penguin,     "Pebble",   4,  "Tropical Bird House"),
        (Flamingo,    "Rosa",     5,  "Tropical Bird House"),
        (Owl,         "Hoot",     6,  "Tropical Bird House"),
        # Reptile House
        (Snake,       "Viper",    4,  "Reptile House"),
        (Crocodile,   "Crunch",  25,  "Reptile House"),        # very old croc — critical
        (Turtle,      "Shell",   40,  "Reptile House"),        # ancient turtle
        (Lizard,      "Gecko",    2,  "Reptile House"),
        (Chameleon,   "Kali",     3,  "Reptile House"),
        # Amphibian Centre
        (Frog,        "Ribbit",   2,  "Amphibian Centre"),
        (Toad,        "Bumpy",    3,  "Amphibian Centre"),
        (Salamander,  "Sal",      4,  "Amphibian Centre"),
        (Newt,        "Newton",   2,  "Amphibian Centre"),
        (Axolotl,     "Axel",     1,  "Amphibian Centre"),
        # Aquarium
        (Shark,       "Jaws",    15,  "Aquarium"),
        (Clownfish,   "Nemo",     2,  "Aquarium"),
        (Goldfish,    "Goldie",   1,  "Aquarium"),
        (Stingray,    "Ray",      5,  "Aquarium"),
        (Seahorse,    "Poseidon", 3,  "Aquarium"),
        # Primate Zone
        (Monkey,      "Chico",    4,  "Primate Zone"),
        (Monkey,      "Coco",    14,  "Primate Zone"),          # aging monkey
    ]
    all_animals = []
    for AnimalClass, name, age, ex_name in animals_config:
        animal = AnimalClass(name, age, ex_name)
        exs[ex_name].add_animal(animal)
        all_animals.append(animal)
    return all_animals


def build_workers():
    return [
        Cleaner      ("Maria"  ),
        Feeder       ("Carlos" ),
        Ticketero    ("Ana"    ),
        ShopEmployee ("Pedro"  ),
        Security     ("Marcos" ),
    ]


def build_visitors():
    return [
        RegularVisitor ("Lucas",    10),   # Child  — fast, revisits
        RegularVisitor ("Sofia",    35),   # Adult
        SeniorVisitor  ("Javier",   68),   # Senior — slow, long dwell
        StudentVisitor ("Mia",      20),   # Student
        KidsVisitor    ("Elena",     8),   # Child  — fast, revisits
        RegularVisitor ("Marco",    42),   # Adult
        SeniorVisitor  ("Beatriz",  72),   # Senior — slow, long dwell
        StudentVisitor ("Daniel",   19),   # Student
        RegularVisitor ("Carmen",   31),   # Adult
        KidsVisitor    ("Pablo",    11),   # Child  — fast, revisits
    ]


# ─────────────────────────────────────────────────────────────────────────────

def print_exhibit_status(zoo, label):
    section(label)
    blank()
    print(f"  {'Exhibit':<22}  {'Type':<8}  {'Visitors':<14}  "
          f"{'Capacity Bar':<24}  {'Util':>5}  {'Clean Bar':<14}  Clean   Pop  Dwell")
    print(f"  {'─' * 105}")
    for ex in zoo.exhibits:
        print(ex.status_line())


def print_animal_status(all_animals, feeder, exhibits):
    section("11. ANIMAL HEALTH & HUNGER STATUS")
    for cat in ["Mammal", "Bird", "Reptile", "Amphibian", "Fish"]:
        group = [a for a in all_animals if a.category == cat]
        if not group:
            continue
        blank()
        print(f"  {BOLD}{cat.upper()}{RESET}")
        print(f"  {'ID':<6}  {'Name':<14}  {'Species':<14}  {'Age':>4}   "
              f"{'Health Bar':<14}  {'Health':>7}  {'Status':<10}   "
              f"{'Hunger Bar':<14}  Hunger")
        print(f"  {'─' * 90}")
        for animal in group:
            print(animal.status_line())
            if animal.hunger_level > 0.6:
                for ex in exhibits.values():
                    if animal in ex.animals:
                        feeder.feed_animals(ex)
                        break


# ─────────────────────────────────────────────────────────────────────────────

def main():
    header("ZOO OPERATIONS SYSTEM SIMULATION  |  TERMINAL MODE")
    print(f"  Start  : {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}")
    print(f"  Engine : Agent-Based + Discrete-Event  |  Language: Python")
    blank()
    time.sleep(0.2)

    # ── 1. INITIALISE ZOO ──────────────────────────────────────────────────────
    section("1. INITIALISING ZOO")
    zoo = Zoo("Safari World Zoo")
    exs = build_exhibits(zoo)

    # ── 2. POPULATE ANIMALS ────────────────────────────────────────────────────
    section("2. POPULATING ANIMAL EXHIBITS")
    blank()
    print(f"  {'ID':<6}  {'Name':<14}  {'Species':<14}  {'Category':<12}  "
          f"{'Age':>4}   {'Health':>7}  Status        Exhibit")
    print(f"  {'─' * 90}")
    all_animals = build_animals(exs)
    for a in all_animals:
        print(f"  {a.id:<6}  {a.name:<14}  {a.species:<14}  {a.category:<12}  "
              f"Age {a.age:>3}   {a.health:.2f}    {a.health_status:<12}  {a.exhibit_name}")

    # ── 3. HIRE WORKERS ────────────────────────────────────────────────────────
    section("3. WORKER SHIFT REGISTRATION")
    blank()
    all_workers = build_workers()
    zoo.workers = all_workers
    for w in all_workers:
        w.start_shift()

    # ── 4. OPEN ZOO ────────────────────────────────────────────────────────────
    section("4. ZOO OPERATIONS")
    blank()
    zoo.open_zoo()

    # ── 5. BUILD VISITORS (arrivals handled inside TicketSellerThread) ─────────
    all_visitors = build_visitors()

    # ── 6. MORNING EXHIBIT STATUS ──────────────────────────────────────────────
    # Seed a few visitors into exhibits before simulation starts
    for v in all_visitors:
        random.choice(zoo.exhibits).add_visitor()
    print_exhibit_status(zoo, "6. EXHIBIT STATUS  --  MORNING")

    # ── 7. FEEDING SHOW ────────────────────────────────────────────────────────
    feeder   = next(w for w in all_workers if w.role == "Feeder")
    security = next(w for w in all_workers if w.role == "Security")
    sav      = exs["Savannah Enclosure"]

    section("7. SCHEDULED EVENT  --  FEEDING SHOW  (Savannah Enclosure)")
    blank()
    log("EVENT", "Feeding show commencing. Visitor surge in progress.", CYAN)
    for _ in range(8):
        sav.add_visitor()
    feeder.feed_animals(sav)
    for animal in sav.animals:
        animal.make_sound()
    if sav.utilization() > 60:
        security.control_crowd(sav)

    # ── 8-9. RUN SIMULATION (threads) ─────────────────────────────────────────
    sim = ZooSimulation(
        zoo         = zoo,
        exhibits    = zoo.exhibits,
        all_animals = all_animals,
        all_visitors= all_visitors,
        all_workers = all_workers,
        total_ticks = 14,
        tick_interval= 0.04,
    )
    sim.run()

    # ── 10. AFTERNOON EXHIBIT STATUS ───────────────────────────────────────────
    print_exhibit_status(zoo, "10. EXHIBIT STATUS  --  AFTERNOON")

    # ── 11. ANIMAL STATUS ──────────────────────────────────────────────────────
    print_animal_status(all_animals, feeder, exs)

    # ── 12. MAINTENANCE ────────────────────────────────────────────────────────
    cleaner = next(w for w in all_workers if w.role == "Cleaner")
    section("12. MAINTENANCE ROUND")
    blank()
    for ex in zoo.exhibits:
        if ex.cleanliness < 0.80:
            cleaner.move(ex.name)
            cleaner.clean_exhibit(ex)
    cleaner.clean_restroom()
    cleaner.clean_path("Main Promenade")
    feeder.check_food_stock()

    # ── 13. SECURITY ───────────────────────────────────────────────────────────
    section("13. SECURITY OPERATIONS")
    blank()
    for zone in ["North Zone", "East Zone", "South Zone", "West Zone"]:
        security.patrol(zone)
    if random.random() < 0.65:
        security.handle_incident(random.choice([
            "Unattended baggage near Reptile House entrance",
            "Visitor attempting to feed restricted animals",
            "Crowd disturbance near Aquarium exit",
            "Lost child reported near Primate Zone",
        ]))

    # ── 14. CLOSE ZOO ──────────────────────────────────────────────────────────
    section("14. END OF DAY  --  CLOSING PROCEDURES")
    blank()
    for w in all_workers:
        w.end_shift()
    zoo.close_zoo()

    # ── 15. KPI REPORT ─────────────────────────────────────────────────────────
    zoo.kpi_report()

    header("SIMULATION COMPLETE")
    print(f"  End: {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}")
    blank()


if __name__ == "__main__":
    main()
