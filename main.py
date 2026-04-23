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
    PrimateFactory,
    ExhibitGroup,                               # Pattern 6 — Composite
    ExhibitIterator,                            # Pattern 10 — Iterator
)
from visitors import VisitorFactory
from workers  import (
    Cleaner, Feeder, Ticketero, ShopEmployee, Security,
    build_incident_chain, dispatch_incident,    # Pattern 9 — Chain of Responsibility
)

from ticket   import Ticket
from zoo      import (
    SimulationConfig,                           # Pattern 5 — Singleton
    ZooBuilder,                                 # Pattern 3 — Builder
    # ZooFacade,                                  # Pattern 8 — Facade
)
from threads  import ZooSimulation

# START ─────────────────────────────────────────────────────────────────────────────

AnimalFactory.register_all()   # Pattern 1: populate the factory registry

ARRIVAL_MINUTES = sorted([
    # 09:00-10:00  (10 visitors)
    5, 12, 19, 27, 34, 42, 49, 53, 57, 60,
    # 10:00-11:30  (20 visitors — morning rush)
    63, 67, 71, 75, 79, 83, 87, 91, 95, 99,
    103, 107, 111, 115, 119, 123, 127, 133, 139, 145,
    # 11:30-13:00  (15 visitors)
    150, 156, 162, 168, 174, 180, 188, 196, 204, 212,
    220, 228, 236, 244, 252,
    # 13:00-14:30  (10 visitors — post-lunch dip)
    260, 270, 280, 290, 300, 310, 320, 330, 340, 350,
    # 14:30-16:00  (15 visitors — afternoon peak)
    358, 366, 374, 382, 390, 398, 406, 414, 420, 426,
    432, 438, 444, 450, 456,
    # 16:00-17:30  (10 visitors — wind-down)
    462, 470, 478, 486, 494, 500, 506, 510, 514, 518,
])  # exactly 80 values


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
def main():
    header("ZOO OPERATIONS SYSTEM SIMULATION  |  09:00 – 18:00")
    print(f"  Date   : {datetime.now().strftime('%Y-%m-%d')}")
    print(f"  Engine : Agent-Based + Discrete-Event  |  Language: Python")
    print(f"  Day    : 09:00 open  ->  18:00 close  |  80 visitors expected")

   # SimulationConfig  in zoo.py
    blank()
    cfg = SimulationConfig()
    cfg2 = SimulationConfig()
    log("SINGLETON", f"cfg  id={id(cfg)}", CYAN)
    log("SINGLETON", f"cfg2 id={id(cfg2)}  same instance: {cfg is cfg2}", CYAN)
    log("SINGLETON", f"Config: {cfg}", CYAN)

    # ── Pattern 1: FACTORY METHOD (animals.py) ────────────────────────────────
    blank()
    log("FACTORY",
        f"Registered species: {AnimalFactory.available_species()}", GREEN)

    # ── Patterns 2+3: ABSTRACT FACTORY (exhibits.py) + BUILDER (zoo.py) ──────
    blank()
    workers = [Cleaner("Maria"), Feeder("Carlos"), Ticketero("Ana"),
               ShopEmployee("Pedro"), Security("Marcos")]

    zoo, exs, all_animals, _ = (
        ZooBuilder("Safari World Zoo")
        .with_zone(SavannahFactory())  # Abstract Factory: exhibit + animals
        .with_zone(AquaticFactory())
        .with_zone(PrimateFactory())
        .with_exhibits([  # Builder: remaining exhibits
            ("Elephant Grounds", 200, 8, False),
            ("Tropical Bird House", 60, 7, True),
            ("Reptile House", 40, 6, True),
            ("Amphibian Centre", 35, 6, True),
        ])
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

    all_visitors = VisitorFactory.generate({
        "Adult": 30,
        "Senior": 15,
        "Student": 15,
        "Child": 20,
    })

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

    """# ── Visitors — 80 visitors to stress exhibit capacities ───────────────────
    all_visitors = [
        # Adults (30)
        RegularVisitor("Sofia", 35), RegularVisitor("Marco", 42),
        RegularVisitor("Carmen", 31), RegularVisitor("Andres", 28),
        RegularVisitor("Isabella", 33), RegularVisitor("Rafael", 45),
        RegularVisitor("Valentina", 29), RegularVisitor("Santiago", 38),
        RegularVisitor("Camila", 26), RegularVisitor("Nicolas", 41),
        RegularVisitor("Lucia", 34), RegularVisitor("Diego", 47),
        RegularVisitor("Ana", 30), RegularVisitor("Jorge", 52),
        RegularVisitor("Monica", 39), RegularVisitor("Carlos", 44),
        RegularVisitor("Patricia", 36), RegularVisitor("Fernando", 49),
        RegularVisitor("Daniela", 27), RegularVisitor("Alberto", 55),
        RegularVisitor("Rosa", 31), RegularVisitor("Miguel", 43),
        RegularVisitor("Claudia", 37), RegularVisitor("Eduardo", 46),
        RegularVisitor("Natalia", 32), RegularVisitor("Roberto", 50),
        RegularVisitor("Laura", 28), RegularVisitor("Victor", 53),
        RegularVisitor("Gabriela", 40), RegularVisitor("Sergio", 35),
        # Seniors (15)
        SeniorVisitor("Javier", 68), SeniorVisitor("Beatriz", 72),
        SeniorVisitor("Manuel", 65), SeniorVisitor("Esperanza", 70),
        SeniorVisitor("Antonio", 67), SeniorVisitor("Pilar", 74),
        SeniorVisitor("Francisco", 63), SeniorVisitor("Mercedes", 69),
        SeniorVisitor("Jose", 71), SeniorVisitor("Dolores", 66),
        SeniorVisitor("Ramon", 75), SeniorVisitor("Consuelo", 64),
        SeniorVisitor("Alfredo", 73), SeniorVisitor("Rosario", 62),
        SeniorVisitor("Enrique", 78),
        # Students (15)
        StudentVisitor("Mia", 20), StudentVisitor("Daniel", 19),
        StudentVisitor("Alejandro", 21), StudentVisitor("Valeria", 18),
        StudentVisitor("Mateo", 20), StudentVisitor("Sara", 19),
        StudentVisitor("Sebastian", 22), StudentVisitor("Paula", 18),
        StudentVisitor("Tomas", 21), StudentVisitor("Andrea", 20),
        StudentVisitor("Julian", 19), StudentVisitor("Mariana", 22),
        StudentVisitor("Nicolas", 18), StudentVisitor("Fernanda", 21),
        StudentVisitor("Samuel", 19),
        # Children (20)
        KidsVisitor("Lucas", 10), KidsVisitor("Elena", 8),
        KidsVisitor("Pablo", 11), KidsVisitor("Sofia", 9),
        KidsVisitor("Matias", 7), KidsVisitor("Valentina", 10),
        KidsVisitor("Emilio", 8), KidsVisitor("Isabela", 11),
        KidsVisitor("Diego", 6), KidsVisitor("Lucia", 9),
        KidsVisitor("Andres", 10), KidsVisitor("Camila", 7),
        KidsVisitor("Juan", 8), KidsVisitor("Maria", 11),
        KidsVisitor("Pedro", 9), KidsVisitor("Ana", 6),
        KidsVisitor("Carlos", 10), KidsVisitor("Rosa", 8),
        KidsVisitor("Luis", 7), KidsVisitor("Carla", 11),
    ]
    for v in all_visitors:
        random.choice(zoo.exhibits).add_visitor()
"""
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
        arrival_minutes=ARRIVAL_MINUTES,
        real_duration_seconds=cfg.real_duration_seconds,
    )
    sim.run()

    print_exhibit_status(zoo," EXHIBIT STATUS  --  18:00  (end of day)")
    print_animal_status(all_animals, feeder, exs)

    # ── Pattern 11: VISITOR PATTERN (animals.py) ──────────────────────────────
    blank()
    inspector = HealthInspector()
    for animal in all_animals:
        animal.accept(inspector)
    inspector.print_report()

    blank()
    auditor = HungerAuditor()
    for animal in all_animals:
        animal.accept(auditor)
    auditor.print_report()

    # ── Pattern 9: CHAIN OF RESPONSIBILITY (workers.py) ───────────────────────
    blank()
    chain = build_incident_chain()
    dispatch_incident(chain, "crowd",
                      "Overcrowding at Savannah after feeding show")
    blank()
    dispatch_incident(chain, "sick_animal",
                      "Dumbo (Elephant, age 30) showing signs of fatigue")
    blank()
    dispatch_incident(chain, "infrastructure",
                      "Main gate turnstile malfunction — manual override needed")

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
    zoo.kpi_report()

    header("SIMULATION COMPLETE  —  18:00  ZOO CLOSED")
    print(f"  Real finish: {datetime.now().strftime('%H:%M:%S')}")
    blank()

if __name__ == "__main__":
    main()
