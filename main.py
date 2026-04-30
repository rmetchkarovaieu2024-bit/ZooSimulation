# main.py
# ─────────────────────────────────────────────────────────────────────────────
#  ZOO OPERATIONS SYSTEM SIMULATION  |  ENTRY POINT
#  Run: python3 main.py
#
#  Simulation runs from 09:00 to 18:00.
#  Visitors are generated via VisitorFactory (Prototype pattern) —
#  no manual initialisation needed.  Edit the counts dict to change the mix.
#
#  Design patterns are in their natural files, not in a separate patterns.py:
#    animals.py  — Factory Method, Prototype, Bridge, Visitor Pattern
#    exhibits.py — Abstract Factory, Composite, Iterator
#    workers.py  — Chain of Responsibility
#    zoo.py      — Singleton, Builder, Facade
# ─────────────────────────────────────────────────────────────────────────────

import random
import math
import time
from datetime import datetime

from utils    import header, section, log, blank, GREEN, RED, BOLD, RESET, CYAN, YELLOW, rule
from animals  import (
    AnimalFactory,                              # Pattern 1 — Factory Method
    clone_animal,                               # Pattern 4 — Prototype
    SoundSystem, TerminalSoundRenderer,         # Pattern 7 — Bridge
    LogFileSoundRenderer,
    HealthInspector, HungerAuditor,             # Pattern 11 — Visitor Pattern
    )
from exhibits import (
    SavannahFactory, AquaticFactory,            # Pattern 2 — Abstract Factory
    PrimateFactory, ElephantFactory, BirdHouseFactory, ReptileFactory, AmphibianFactory,
    ExhibitGroup,                               # Pattern 6 — Composite
    ExhibitIterator,                            # Pattern 10 — Iterator
)
from visitors import VisitorFactory
from workers  import (
    Cleaner, Feeder, Ticketero, ShopEmployee, Security,
    build_incident_chain, dispatch_incident,    # Pattern 9 — Chain of Responsibility
)

# from ticket   import Ticket
from zoo      import (
    SimulationConfig,                           # Pattern 5 — Singleton
    ZooBuilder,                                 # Pattern 3 — Builder
    # ZooFacade,                                  # Pattern 8 — Facade
)
from threads  import ZooSimulation
from database import Database

# START ─────────────────────────────────────────────────────────────────────────────

AnimalFactory.register_all()   # Pattern 1: populate the factory registry

t_thresholds = [
    (0, 60, 0.10),  # 09:00-10:00  early openers       10 %
    (60, 150, 0.28),  # 10:00-11:30  morning rush         28 %
    (150, 240, 0.18),  # 11:30-13:00  late morning         18 %
    (240, 330, 0.08),  # 13:00-14:30  post-lunch dip        8 %
    (330, 420, 0.24),  # 14:30-16:00  afternoon peak        24 %
    (420, 510, 0.12),  # 16:00-17:30  wind-down             12 %
]
tiket_booths = 3
processing_m= 2  # minutes per visitor per booth
m_gap = processing_m / tiket_booths  # 0.667 min

def generate_arrival_schedule(n_visitors: int) -> list:
    total_weight = sum(w for _, _, w in t_thresholds)
    normalised = [(s, e, w / total_weight) for s, e, w in t_thresholds]

    raw = []
    for _ in range(n_visitors):
        r = random.random()
        cumulative = 0.0
        for start, end, prob in normalised:
            cumulative += prob
            if r <= cumulative:
                raw.append(random.uniform(start, end))
                break
        else:
            raw.append(random.uniform(420, 510))  # fallback: wind-down

    raw.sort()
    enforced = [raw[0]]
    for t in raw[1:]:
        earliest_possible = enforced[-1] + m_gap
        enforced.append(max(t, earliest_possible))

    # Convert to integer minutes and cap at last-admissions (510 = 17:30)
    return [min(510, int(t)) for t in enforced]


def generate_visitor_counts(n_visitors: int) -> dict:
    adult_frac = random.uniform(0.40, 0.50)
    child_frac = random.uniform(0.20, 0.30)
    senior_frac = random.uniform(0.10, 0.18)
    # students fill the remainder
    student_frac = max(0.05, 1.0 - adult_frac - child_frac - senior_frac)

    adults = round(n_visitors * adult_frac)
    children = round(n_visitors * child_frac)
    seniors = round(n_visitors * senior_frac)
    students = n_visitors - adults - children - seniors  # exact remainder

    return {"Adult": adults, "Child": children,
            "Senior": seniors, "Student": max(1, students)}


def print_exhibit_status(zoo, label):
    section(label)
    blank()
    print(f"  {'Exhibit':<22}  {'Type':<8}  {'Now':>7}  {'Current Bar':<24}  "
          f"{'Util':>5}  {'Peak':>7}  {'Peak Bar':<24}  {'Peak%':>6}  Clean   Pop")
    print(f"  {'─' * 130}")
    for ex in zoo.exhibits:
        print(ex.status_line())


def print_animal_status(all_animals, feeder, exhibits):
    section("ANIMAL HEALTH & HUNGER STATUS")
    for cat in ["Mammal", "Bird", "Reptile", "Amphibian", "Fish"]:
        group = [a for a in all_animals if a.category == cat]
        if not group:
            continue
        blank()
        print(f"  {BOLD}{cat.upper()}{RESET}")
        print(f"  {'ID':<6}  {'Name':<14}  {'Species':<14}  {'Age':>4}   "
              f"{'Health Bar':<14}  {'Health':>7}  {'Status':<10}   "
              f"{'Hunger Bar':<14}  Hunger")
        print(f"  {'─' * 92}")
        for animal in group:
            print(animal.status_line())
            if animal.hunger_level > 0.6:
                for ex in exhibits.values():
                    if animal in ex.animals:
                        feeder.feed_animals(ex)
                        break


# ─────────────────────────────────────────────────────────────────────────────
    # ─────────────────────────────────────────────────────────────────────────────
def main():
        # ── Daily visitor count — random between 200 and 600 ─────────────────────
    n_visitors = random.randint(200, 600)

    header("ZOO OPERATIONS SYSTEM SIMULATION  |  09:00 – 18:00")
    print(f"  Date   : {datetime.now().strftime('%Y-%m-%d')}")
    print(f"  Engine : Agent-Based + Discrete-Event  |  Language: Python")
    print(f"  Day    : 09:00 open  ->  18:00 close  |  {n_visitors} visitors expected  ({tiket_booths} ticket booths)")
        # SimulationConfig  in zoo.py
    blank()
    cfg = SimulationConfig()
    log("SINGLETON", f"{cfg}  —  same instance every call: {cfg is SimulationConfig()}", CYAN)

        # ── DATABASE ─────────────────────────────────────────────────────────────
    db = Database("zoo.db")

    arrival_mins = generate_arrival_schedule(n_visitors)
    visitor_counts = generate_visitor_counts(n_visitors)



        # ── Pattern 1: FACTORY METHOD (animals.py) ────────────────────────────────
    blank()
    log("FACTORY",f"Registered species: {AnimalFactory.available_species()}", GREEN)

    # ── Patterns 2+3: ABSTRACT FACTORY (exhibits.py) + BUILDER (zoo.py) ──────
    blank()
    workers = [Cleaner("Maria"), Feeder("Carlos"), Ticketero("Ana"),
               ShopEmployee("Pedro"), Security("Marcos")]

    zoo, exs, all_animals, _ = (
        ZooBuilder("Safari World Zoo")
        .with_zone(SavannahFactory())
        .with_zone(AquaticFactory())
        .with_zone(PrimateFactory())
        .with_zone(ElephantFactory())
        .with_zone(BirdHouseFactory())
        .with_zone(ReptileFactory())
        .with_zone(AmphibianFactory())
        .with_animals([  # Factory Method inside Builder
            ("Elephant", "Dumbo", 30, "Elephant Grounds"),
            ("Elephant", "Nandita", 8, "Elephant Grounds"),
            ("Parrot", "Polly", 3, "Tropical Bird House"),
            ("Eagle", "Aquila", 22, "Tropical Bird House"),
            ("Penguin", "Pebble", 4, "Tropical Bird House"),
            ("Flamingo", "Rosa", 5, "Tropical Bird House"),
            ("Owl", "Hoot", 6, "Tropical Bird House"),
            ("Snake", "Viper", 4, "Reptile House"),
            ("Crocodile", "Crunch", 25, "Reptile House"),
            ("Turtle", "Shell", 40, "Reptile House"),
            ("Lizard", "Gecko", 2, "Reptile House"),
            ("Chameleon", "Kali", 3, "Reptile House"),
            ("Frog", "Ribbit", 2, "Amphibian Centre"),
            ("Toad", "Bumpy", 3, "Amphibian Centre"),
            ("Salamander", "Sal", 4, "Amphibian Centre"),
            ("Newt", "Newton", 2, "Amphibian Centre"),
            ("Axolotl", "Axel", 1, "Amphibian Centre"),
            ("Goldfish", "Goldie", 1, "Aquarium"),
        ])
        .with_workers(workers)
        .build()
    )

    # ── Pattern 4: PROTOTYPE (animals.py) ─────────────────────────────────────
    blank()
    original = next(a for a in all_animals if a.species == "Lion")
    baby_lion = clone_animal(original, new_name="Mufasa", new_age=1)
    exs["Savannah Enclosure"].add_animal(baby_lion)
    all_animals.append(baby_lion)

    all_visitors = VisitorFactory.generate(visitor_counts)
    log("SCHEDULE",
        f"Today: {n_visitors} visitors   "
        f"Adult {visitor_counts['Adult']}  "
        f"Child {visitor_counts['Child']}  "
        f"Senior {visitor_counts['Senior']}  "
        f"Student {visitor_counts['Student']}  "
        f"|  First arrival: {arrival_mins[0]} min after 09:00  "
        f"Last: {arrival_mins[-1]} min", CYAN)

    # ── Pattern 6: COMPOSITE (exhibits.py) ────────────────────────────────────
    blank()
    indoor_group = ExhibitGroup("All Indoor Exhibits")
    outdoor_group = ExhibitGroup("All Outdoor Exhibits")
    for ex in zoo.exhibits:
        (indoor_group if ex.indoor else outdoor_group).add(ex)
    log("COMPOSITE", f"Indoor  group: {len(indoor_group)} exhibits", GREEN)
    log("COMPOSITE", f"Outdoor group: {len(outdoor_group)} exhibits", GREEN)

    # ── Pattern 7: BRIDGE (animals.py) ────────────────────────────────────────
    blank()
    sav = exs["Savannah Enclosure"]
    sound = SoundSystem(TerminalSoundRenderer())
    log("BRIDGE", "Playing via TerminalSoundRenderer:", YELLOW)
    sound.play_all(sav)
    log("BRIDGE", "Switching to LogFileSoundRenderer:", YELLOW)
    sound.set_renderer(LogFileSoundRenderer())
    sound.play_all(sav)

    # ── Worker shifts + open ──────────────────────────────────────────────────
    section("WORKER SHIFT REGISTRATION")
    blank()
    for w in workers:
        w.start_shift()
    zoo.open_zoo()
    db.start_run(n_visitors)
    print_exhibit_status(zoo, "EXHIBIT STATUS  --  09:00  (before visitors)")

 # ExhibitIterator  in exhibits.py
    blank()
    ExhibitIterator(zoo.exhibits, order="popularity", reverse=True).print_order()

    feeder = next(w for w in workers if w.role == "Feeder")
    security = next(w for w in workers if w.role == "Security")
    section("SCHEDULED EVENT  --  FEEDING SHOW  (Savannah Enclosure)")
    blank()
    log("EVENT", "Feeding show commencing. Visitor surge in progress.", CYAN)
    feeder.feed_animals(sav)
    for animal in sav.animals:
        animal.make_sound()


    # ── Simulation threads ────────────────────────────────────────────────────
    sim = ZooSimulation(
        zoo=zoo,
        exhibits=zoo.exhibits,
        all_animals=all_animals,
        all_visitors= all_visitors,
        all_workers=workers,
        arrival_minutes=arrival_mins,
        real_duration_seconds=cfg.real_duration_seconds,
        db = db,
    )
    sim.run()

    print_exhibit_status(zoo," EXHIBIT STATUS  --  18:00  (end of day)")
    print_animal_status(all_animals, feeder, exs)

    # ── Pattern 11: VISITOR PATTERN (animals.py) ──────────────────────────────
    blank()
    inspector = HealthInspector()
    for animal in all_animals:
        animal.accept(inspector)
    inspector.print_report(db=db,all_animals=all_animals)

    blank()
    auditor = HungerAuditor()
    for animal in all_animals:
        animal.accept(auditor)
    auditor.print_report()

    # ── Pattern 9: CHAIN OF RESPONSIBILITY (workers.py) ───────────────────────
    blank()
    chain = build_incident_chain()
    dispatch_incident(chain, "crowd",
                      "Overcrowding at Savannah after feeding show",db=db)
    blank()
    dispatch_incident(chain, "sick_animal",
                      "Dumbo (Elephant, age 30) showing signs of fatigue",db=db)
    blank()
    dispatch_incident(chain, "infrastructure",
                      "Main gate turnstile malfunction — manual override needed",db=db)

    # ── Pattern 6 bulk action via Composite ───────────────────────────────────
    blank()
    indoor_group.clean()

    # ── Maintenance + close ───────────────────────────────────────────────────
    cleaner = next(w for w in workers if w.role == "Cleaner")
    section("MAINTENANCE ROUND")
    blank()
    for ex in zoo.exhibits:
        if ex.cleanliness < 0.80:
            cleaner.move(ex.name)
            cleaner.clean_exhibit(ex)
    cleaner.clean_restroom()
    cleaner.clean_path("Main Promenade")
    feeder.check_food_stock()

    section("SECURITY OPERATIONS")
    blank()
    for zone in ["North Zone", "East Zone", "South Zone", "West Zone"]:
        security.patrol(zone)

    section("END OF DAY  --  CLOSING PROCEDURES")
    blank()
    for w in workers:
        w.end_shift()
    zoo.close_zoo()
    zoo.kpi_report(db=db)

    db.print_history()
    db.close()

    header("SIMULATION COMPLETE  —  18:00  ZOO CLOSED")
    print(f"  Real finish: {datetime.now().strftime('%H:%M:%S')}")
    blank()

if __name__ == "__main__":
    main()
