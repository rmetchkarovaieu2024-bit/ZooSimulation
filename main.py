# main.py
# ─────────────────────────────────────────────────────────────────────────────
#  ZOO OPERATIONS SYSTEM SIMULATION  |  ENTRY POINT
#  Run: python3 main.py
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

from utils    import header, section, log, blank, GREEN, RED, BOLD, RESET, CYAN, YELLOW
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
from visitors import RegularVisitor, KidsVisitor, SeniorVisitor, StudentVisitor
from workers  import (
    Cleaner, Feeder, Ticketero, ShopEmployee, Security,
    build_incident_chain, dispatch_incident,    # Pattern 9 — Chain of Responsibility
)

from ticket   import Ticket
from zoo      import (
    SimulationConfig,                           # Pattern 5 — Singleton
    ZooBuilder,                                 # Pattern 3 — Builder
    ZooFacade,                                  # Pattern 8 — Facade
)
from threads  import ZooSimulation

# START ─────────────────────────────────────────────────────────────────────────────

AnimalFactory.register_all()   # Pattern 1: populate the factory registry


def print_exhibit_status(zoo, label):
    section(label)
    blank()
    print(f"  {'Exhibit':<22}  {'Type':<8}  {'Visitors':<14}  "
          f"{'Capacity Bar':<24}  {'Util':>5}  {'Clean Bar':<14}  Clean   Pop  Dwell")
    print(f"  {'─' * 108}")
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
    header("ZOO OPERATIONS SYSTEM SIMULATION  |  TERMINAL MODE")
    print(f"  Start  : {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}")
    print(f"  Engine : Agent-Based + Discrete-Event  |  Language: Python")
    blank()

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

    # ── Visitors ──────────────────────────────────────────────────────────────
    all_visitors = [
        RegularVisitor("Lucas", 10), RegularVisitor("Sofia", 35),
        SeniorVisitor("Javier", 68), StudentVisitor("Mia", 20),
        KidsVisitor("Elena", 8), RegularVisitor("Marco", 42),
        SeniorVisitor("Beatriz", 72), StudentVisitor("Daniel", 19),
        RegularVisitor("Carmen", 31), KidsVisitor("Pablo", 11),
    ]
    for v in all_visitors:
        random.choice(zoo.exhibits).add_visitor()

    print_exhibit_status(zoo, "EXHIBIT STATUS  --  MORNING")

    feeder = next(w for w in workers if w.role == "Feeder")
    security = next(w for w in workers if w.role == "Security")
    section("SCHEDULED EVENT  --  FEEDING SHOW  (Savannah Enclosure)")
    blank()
    log("EVENT", "Feeding show commencing. Visitor surge in progress.", CYAN)
    for _ in range(8):
        sav.add_visitor()
    feeder.feed_animals(sav)
    for animal in sav.animals:
        animal.make_sound()
    if sav.utilization() > 60:
        security.control_crowd(sav)

    # ── Pattern 10: ITERATOR (exhibits.py) ────────────────────────────────────
    blank()
    ExhibitIterator(zoo.exhibits, order="popularity", reverse=True).print_order()
    blank()
    log("ITERATOR", "Traversal by utilization (highest first):", CYAN)
    for ex in ExhibitIterator(zoo.exhibits, order="utilization", reverse=True):
        log("ITERATOR",
            f"{ex.name:<26}  util: {ex.utilization()}%  pop: {ex.popularity}/10", CYAN)

    # ── Simulation threads ────────────────────────────────────────────────────
    sim = ZooSimulation(
        zoo=zoo,
        exhibits=zoo.exhibits,
        all_animals=all_animals,
        all_visitors=all_visitors,
        all_workers=workers,
        total_ticks=cfg.total_ticks,
        tick_interval=cfg.tick_interval,
    )
    sim.run()

    print_exhibit_status(zoo, "EXHIBIT STATUS  --  AFTERNOON")
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

    header("SIMULATION COMPLETE")
    print(f"  End: {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}")
    blank()


if __name__ == "__main__":
    main()
