# zoo.py
# ─────────────────────────────────────────────────────────────────────────────
#  ZOO  —  top-level container
#
#  Design patterns housed here (zoo orchestration owns these concepts):
#    Pattern 3 — Builder   : ZooBuilder (fluent construction of the whole zoo)
#    Pattern 5 — Singleton : SimulationConfig (one global config object)
#    Pattern 8 — Facade    : ZooFacade (single entry point for the simulation)
# ─────────────────────────────────────────────────────────────────────────────

from utils import log, section, blank, GREEN, RED, BOLD, RESET, CYAN


class Zoo:
    def __init__(self, name):
        self.name     = name
        self.exhibits = []
        self.workers  = []
        self.visitors = []
        self.revenue  = 0.0

    def add_exhibit(self, exhibit):
        self.exhibits.append(exhibit)
        log("ZOO",
            f"Registered: {exhibit.name:<22}  Capacity: {exhibit.capacity:<4}  "
            f"Popularity: {exhibit.popularity}/10  "
            f"{'Indoor' if exhibit.indoor else 'Outdoor'}", GREEN)

    def open_zoo(self):
        log("ZOO", f"{self.name}  --  STATUS: OPEN", GREEN)

    def close_zoo(self):
        log("ZOO", f"{self.name}  --  STATUS: CLOSED", RED)

    def kpi_report(self, db=None):
        section("END-OF-DAY KPI REPORT")
        blank()

        total    = len(self.visitors)
        avg_sat  = round(sum(v.satisfaction for v in self.visitors) / max(1, total), 2)
        avg_nrg  = round(sum(v.energy       for v in self.visitors) / max(1, total), 2)
        lost     = sum(1 for v in self.visitors if v.energy < 0.2)
        busiest  = max(self.exhibits, key=lambda e: e.current_visitors) if self.exhibits else None
        util_avg = round(
            sum(e.peak_utilization() for e in self.exhibits) / max(1, len(self.exhibits)), 1)

        # Subtype breakdown
        subtypes = {}
        for v in self.visitors:
            subtypes[v.subtype] = subtypes.get(v.subtype, 0) + 1

        rows = [
            ("Total Visitors",               str(total)),
            ("Avg Satisfaction Score",        f"{avg_sat:.2f} / 1.00"),
            ("Avg Energy at Exit",            f"{avg_nrg:.2f} / 1.00"),
            ("Lost Visitors (energy < 0.2)",  str(lost)),
            ("Avg Peak Exhibit Utilization",       f"{util_avg} %"),
            ("Total Revenue (EUR)",           f"{self.revenue:.2f}"),
            ("Busiest Exhibit",               busiest.name if busiest else "N/A"),
        ]
        for subtype, count in subtypes.items():
            rows.append((f"  Visitors: {subtype}", str(count)))

        print(f"  {'Metric':<36}  Value")
        print(f"  {'─' * 36}  {'─' * 20}")
        for label, value in rows:
            print(f"  {label:<36}  {value}")
        blank()

        if db:
            db.save_run({
                "avg_satisfaction": avg_sat,
                "avg_energy": avg_nrg,
                "lost_visitors": lost,
                "avg_peak_util": util_avg,
                "total_revenue": round(self.revenue, 2),
                "busiest_exhibit": busiest.name if busiest else "N/A",
                **{f"{s.lower()}_count": c for s, c in subtypes.items()},
            })


#─#─ Pattern 5 ───────────────────────────────────────────────────────────────────
class SimulationConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance .real_duration_seconds = 15 # 15 second simulate the full 9 hours of a zoo day (9:00-18:00)
            cls._instance.hunger_threshold = 0.60
            cls._instance.clean_threshold = 0.65
            cls._instance.food_prob_senior = 0.45
            cls._instance.food_prob_other = 0.30
            cls._instance.shop_prob = 0.25
            log("SINGLETON",
                "SimulationConfig created (first and only instance).", CYAN)
        return cls._instance

    def __repr__(self):
        return (f"SimulationConfig(real_duration={self.real_duration_seconds}s, "
                f"hunger_threshold={self.hunger_threshold})")


#─#─ Pattern 3 ───────────────────────────────────────────────────────────────────
class ZooBuilder:
    def __init__(self, name):
        self._zoo = Zoo(name)
        self._exhibits = {}
        self._animals = []
        self._workers = []
        log("BUILDER", f"ZooBuilder initialised for '{name}'", CYAN)

    def with_zone(self, zone_factory):
        exhibit, animals = zone_factory.create_zone()
        self._zoo.add_exhibit(exhibit)
        self._exhibits[exhibit.name] = exhibit
        for animal in animals:
            exhibit.add_animal(animal)
            self._animals.append(animal)
        return self

    def with_exhibits(self, exhibits_config):
        from exhibits import Exhibit
        for name, cap, pop, indoor in exhibits_config:
            e = Exhibit(name, cap, pop, indoor)
            self._zoo.add_exhibit(e)
            self._exhibits[name] = e
        log("BUILDER", f"Exhibits registered: {len(self._exhibits)}", CYAN)
        return self

    def with_animals(self, animals_config):
        from animals import AnimalFactory
        for species, name, age, ex_name in animals_config:
            animal = AnimalFactory.create(species, name, age, ex_name)
            self._exhibits[ex_name].add_animal(animal)
            self._animals.append(animal)
        log("BUILDER", f"Animals placed: {len(self._animals)}", CYAN)
        return self

    def with_workers(self, worker_instances):
        self._zoo.workers = worker_instances
        self._workers = worker_instances
        log("BUILDER", f"Workers registered: {len(self._workers)}", CYAN)
        return self

    def build(self):
        log("BUILDER", f"Zoo '{self._zoo.name}' construction complete.", CYAN)
        return self._zoo, self._exhibits, self._animals, self._workers

#─#─ Pattern 8 ───────────────────────────────────────────────────────────────────

class ZooFacade: # Single entry point to run the entire simulation with a simple interface
    def __init__(self, zoo_name="Safari World Zoo"):
        self._zoo_name = zoo_name
        self._cfg = SimulationConfig()

    def _build(self):
        from workers import Cleaner, Feeder, Ticketero, ShopEmployee, Security
        from visitors import RegularVisitor, KidsVisitor, SeniorVisitor, StudentVisitor
        from exhibits import SavannahFactory, AquaticFactory, PrimateFactory
        from threads import ZooSimulation

        workers = [Cleaner("Maria"), Feeder("Carlos"), Ticketero("Ana"),
                   ShopEmployee("Pedro"), Security("Marcos")]

        zoo, exs, animals, _ = (
            ZooBuilder(self._zoo_name)
            .with_zone(SavannahFactory())
            .with_zone(AquaticFactory())
            .with_zone(PrimateFactory())
            .with_exhibits([
                ("Elephant Grounds", 200, 8, False),
                ("Tropical Bird House", 60, 7, True),
                ("Reptile House", 40, 6, True),
                ("Amphibian Centre", 35, 6, True),
            ])
            .with_animals([
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

        visitors = [
            RegularVisitor("Lucas", 10), RegularVisitor("Sofia", 35),
            SeniorVisitor("Javier", 68), StudentVisitor("Mia", 20),
            KidsVisitor("Elena", 8), RegularVisitor("Marco", 42),
            SeniorVisitor("Beatriz", 72), StudentVisitor("Daniel", 19),
            RegularVisitor("Carmen", 31), KidsVisitor("Pablo", 11),
        ]

        sim = ZooSimulation(
            zoo=zoo,
            exhibits=zoo.exhibits,
            all_animals=animals,
            all_visitors=visitors,
            all_workers=workers,
            total_ticks=self._cfg.total_ticks,
            tick_interval=self._cfg.tick_interval,
        )
        return zoo, exs, animals, visitors, workers, sim

    def run(self):
        section("FACADE — ZooFacade.run()")
        log("FACADE", f"Building '{self._zoo_name}' via subsystems...", CYAN)
        zoo, exs, animals, visitors, workers, sim = self._build()
        zoo.open_zoo()
        sim.run()
        zoo.close_zoo()
        zoo.kpi_report()
        log("FACADE", "Simulation complete.", CYAN)
