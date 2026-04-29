# Zoo Operations System Simulation

A terminal-based simulation of a full zoological park operating day (09:00 – 18:00), built in Python using Agent-Based and Discrete-Event principles with native threading.

---

## How to Run

```bash
python3 main.py
```

No external dependencies. Requires **Python 3.8+**.

Every run is different — daily visitor count is drawn randomly between 200 and 600, arrival times are generated dynamically, and exhibit popularity varies within realistic ranges.

---

## Project Structure

```
zoo_project/
├── main.py        Entry point — builds the zoo, generates the day, runs simulation
├── animals.py     Animal hierarchy + Factory Method, Prototype, Bridge, Visitor Pattern
├── exhibits.py    Exhibit + Abstract Factory (7 zone factories), Composite, Iterator
├── visitors.py    Visitor hierarchy + Prototype (clone_visitor), Factory Method (VisitorFactory)
├── workers.py     Worker hierarchy + Chain of Responsibility
├── zoo.py         Zoo container + Singleton, Builder, Facade
├── threads.py     All simulation threads
├── ticket.py      Ticket class
└── utils.py       Terminal colour codes and shared formatting helpers
```

---

## Class Hierarchy

### Animal (`animals.py`)

```
Animal
├── Mammal
│   ├── Lion
│   ├── Elephant
│   ├── Tiger
│   ├── Monkey
│   └── Zebra
├── Bird
│   ├── Parrot
│   ├── Eagle
│   ├── Penguin
│   ├── Flamingo
│   └── Owl
├── Reptile
│   ├── Snake
│   ├── Crocodile
│   ├── Turtle
│   ├── Lizard
│   └── Chameleon
├── Amphibian
│   ├── Frog
│   ├── Toad
│   ├── Salamander
│   ├── Newt
│   └── Axolotl
└── Fish
    ├── Shark
    ├── Clownfish
    ├── Goldfish
    ├── Stingray
    └── Seahorse
```

25 registered species across 5 categories.

### Visitor (`visitors.py`)

```
Visitor
├── RegularVisitor   (Adult)
├── KidsVisitor      (Child)
├── SeniorVisitor    (Senior)
└── StudentVisitor   (Student)
```

### Worker (`workers.py`)

```
Worker
├── Cleaner
├── Feeder
├── Ticketero
├── ShopEmployee
└── Security
```

---

## Exhibits & Zone Factories

Every exhibit is created by a dedicated `AbstractZoneFactory` subclass. Popularity is randomised within a realistic range each run — so some days lions are a 10, some days a 7.

| Factory | Exhibit | Capacity | Type | Popularity Range |
|---------|---------|----------|------|-----------------|
| `SavannahFactory` | Savannah Enclosure | 25 | Outdoor | 7 – 10 |
| `PrimateFactory` | Primate Zone | 18 | Outdoor | 6 – 9 |
| `ElephantFactory` | Elephant Grounds | 30 | Outdoor | 6 – 9 |
| `AquaticFactory` | Aquarium | 15 | Indoor | 5 – 8 |
| `BirdHouseFactory` | Tropical Bird House | 12 | Indoor | 5 – 8 |
| `ReptileFactory` | Reptile House | 8 | Indoor | 4 – 7 |
| `AmphibianFactory` | Amphibian Centre | 7 | Indoor | 3 – 6 |

---

## Behavioural Rules

### Visitor Subtypes

| Subtype | Age     | Move Penalty | Dwell Multiplier | Can Revisit | Energy (start) |
|---------|---------|-------------|-----------------|-------------|----------------|
| Child   | < 12    | 0.03        | 0.8×            | Yes         | 0.50 – 1.00    |
| Student | 12–21   | 0.05        | 1.0×            | No          | 0.50 – 1.00    |
| Adult   | 22–60   | 0.05        | 1.0×            | No          | 0.50 – 1.00    |
| Senior  | > 60    | 0.08        | 1.6×            | No          | 0.50 – 1.00    |

Every visitor starts with a randomly cloned energy (0.50–1.00), money (€10–€100), and satisfaction (0.50–0.90) — no two visitors are identical.

**Number of exhibits visited** scales with arrival energy:
```python
n_visits = max(2, min(7, int(energy * 6) + random.randint(0, 2)))
```
A tired visitor (energy 0.55) plans 2–4 exhibits. A fresh one (energy 1.00) plans 6–7.

### Exhibit Selection

Visitors pick exhibits via weighted random selection proportional to popularity:
```python
chosen = random.choices(exhibits, weights=[e.popularity for e in exhibits], k=1)[0]
```
A popularity-9 exhibit is 3× more likely to be chosen than a popularity-3 exhibit.

### Dwell Time

```
base_dwell = 3 + popularity × 1.5   minutes  (± random variation)
actual_dwell = base_dwell × subtype_multiplier
```

| Popularity | Base Dwell | Senior Dwell (×1.6) |
|-----------|-----------|---------------------|
| 4         | ~7 min    | ~11 min             |
| 6         | ~11 min   | ~18 min             |
| 8         | ~15 min   | ~24 min             |
| 10        | ~17 min   | ~27 min             |

### Animal Health (Age-Based)

```python
health = max(0.1, 1.0 - age * 0.025)
```

| Health    | Status   | Example                    |
|-----------|----------|----------------------------|
| 0.80–1.00 | Healthy  | Simba (Lion, age 5)        |
| 0.50–0.79 | Aging    | Raja (Tiger, age 18)       |
| 0.30–0.49 | Frail    | Crunch (Crocodile, age 25) |
| 0.00–0.29 | Critical | Shell (Turtle, age 40)     |

Older animals also get hungry faster:
```python
hunger_rate = BASE_RATE × (2.0 - health)
```
A Critical animal accumulates hunger roughly twice as fast as a Healthy one.

---

## Arrival Schedule

Visitors do not all arrive at once. Each day an arrival schedule is generated dynamically based on:

- **Daily count**: random between 200 and 600
- **Time bands**: weighted to model real-world zoo attendance peaks

| Window | Weight | Pattern |
|--------|--------|---------|
| 09:00–10:00 | 10% | Early openers |
| 10:00–11:30 | 28% | Morning rush |
| 11:30–13:00 | 18% | Late morning |
| 13:00–14:30 | 8% | Post-lunch dip |
| 14:30–16:00 | 24% | Afternoon peak |
| 16:00–17:30 | 12% | Wind-down |

**3 ticket booths**, each processing one visitor every 2 minutes, give a combined throughput of one arrival every 0.67 minutes. The schedule enforces this minimum gap so the queue never exceeds booth capacity.

Each `VisitorThread` sleeps internally until the simulation clock reaches its assigned arrival minute, then wakes up and enters the zoo — no batching, no manual scheduling.

---

## Thread Architecture

```
ZooSimulation
├── ClockThread              Maps real elapsed time → simulation time (09:00–18:00)
│                            Announces milestones: 10:00, 12:00, 15:00, 16:00, 17:30, 18:00
├── ExhibitThread  (× 7)     One per exhibit — cleanliness decays with visitor count each tick
├── AnimalThread   (× 29)    One per animal — hunger increases; rate scales with age
├── VisitorThread  (× N)     One per visitor — waits for arrival time, then journeys
└── WorkerThread
    ├── CleanerThread        Cleans exhibits below cleanliness threshold 0.60 every 3 ticks
    ├── FeederThread         Feeds animals with hunger above 0.65 every 2 ticks
    ├── TicketSellerThread   Opens gate and logs expected visitor count
    ├── ShopEmployeeThread   Restocks shop at end of day
    └── SecurityThread       Patrols a zone every 5 ticks; crowd-manages busy exhibits
```

The `ClockThread` reference is injected into `utils.py` so every `log()` call prints `[SIM HH:MM]` during the simulation and real time `[HH:MM:SS]` during setup and post-sim reporting.

---

## Simulation Flow

| Stage | What happens |
|-------|-------------|
| Singleton check | Proves `SimulationConfig` returns the same instance every call |
| Factory Method | Registers all 25 species in `AnimalFactory` |
| Abstract Factory + Builder | All 7 zone factories build exhibit + animals; Zoo assembled fluently |
| Prototype — animals | Baby lion Mufasa cloned from Simba |
| Prototype — visitors | `VisitorFactory` generates N visitors via cloning; each gets randomised stats |
| Composite | Exhibits grouped into Indoor / Outdoor `ExhibitGroup` objects |
| Bridge | Animal sounds played via `TerminalSoundRenderer` then `LogFileSoundRenderer` |
| Worker shifts | All 5 workers start; zoo opens |
| Morning status | Exhibit snapshot before any visitors |
| Iterator | Exhibits printed by popularity and by utilization |
| Feeding show | Savannah animals fed; sounds triggered |
| Visitor journeys | All N visitor threads start; each waits for its arrival minute |
| Afternoon status | Exhibit snapshot after peak hours |
| Animal status | Health and hunger bars grouped by category |
| Visitor Pattern | `HealthInspector` and `HungerAuditor` scan every animal via `animal.accept()` |
| Chain of Responsibility | 3 incidents dispatched: Security → Vet → Manager |
| Composite bulk clean | All indoor exhibits cleaned in one `group.clean()` call |
| Maintenance | Remaining dirty exhibits swept; food stock checked |
| Security | End-of-day zone patrols |
| Close | Workers end shifts; zoo closes; KPI report printed |

---

## Design Patterns

Each pattern lives in the file that owns those concepts — there is no `patterns.py`.

### Creational

| # | Pattern | File | Class / Function |
|---|---------|------|-----------------|
| 1 | **Factory Method** | `animals.py` | `AnimalFactory.create("Lion", ...)` — creates any of 25 species by name string |
| 2 | **Abstract Factory** | `exhibits.py` | 7 zone factories — each produces a complete themed exhibit + animals as a unit |
| 3 | **Builder** | `zoo.py` | `ZooBuilder(...).with_zone().with_workers().build()` — fluent zoo construction |
| 4 | **Prototype** | `animals.py` `visitors.py` | `clone_animal()` for breeding; `clone_visitor()` + `VisitorFactory` for visitor generation |
| 5 | **Singleton** | `zoo.py` | `SimulationConfig` — `__new__` guarantees one global config instance |

### Structural

| # | Pattern | File | Class / Function |
|---|---------|------|-----------------|
| 6 | **Composite** | `exhibits.py` | `ExhibitGroup` — `group.clean()` cleans all members; `group.utilization()` returns average |
| 7 | **Bridge** | `animals.py` | `SoundSystem(renderer)` — swap `TerminalSoundRenderer` ↔ `LogFileSoundRenderer` at runtime |

### Behavioural

| # | Pattern | File | Class / Function |
|---|---------|------|-----------------|
| 8 | **Facade** | `zoo.py` | `ZooFacade("Zoo Name").run()` — single entry point hiding all subsystem complexity |
| 9 | **Chain of Responsibility** | `workers.py` | `SecurityHandler → VetHandler → ZooManagerHandler` — incident escalation chain |
| 10 | **Iterator** | `exhibits.py` | `ExhibitIterator(exhibits, order="popularity")` — ordered traversal via `__iter__` / `__next__` |
| 11 | **Visitor Pattern** | `animals.py` | `HealthInspector`, `HungerAuditor` — new operations on animals via `animal.accept(visitor)` |

### Terminal Log Tags per Pattern

| Tag | Pattern |
|-----|---------|
| `[SINGLETON  ]` | Singleton |
| `[FACTORY    ]` | Factory Method |
| `[ABSTRACT_F ]` | Abstract Factory |
| `[BUILDER    ]` | Builder |
| `[PROTOTYPE  ]` | Prototype |
| `[VISITOR_F  ]` | Visitor Factory (Prototype) |
| `[COMPOSITE  ]` | Composite |
| `[SOUND      ]` / `[BRIDGE    ]` | Bridge |
| `[FACADE     ]` | Facade |
| `[CHAIN      ]` | Chain of Responsibility |
| `[ITERATOR   ]` | Iterator |
| `[INSPECTOR  ]` / `[AUDITOR   ]` | Visitor Pattern |

---

## Key Performance Indicators

Printed at the end of every run:

| KPI | Description |
|-----|-------------|
| Total Visitors | Number who entered |
| Avg Satisfaction Score | Mean satisfaction at exit (0.00–1.00) |
| Avg Energy at Exit | Mean remaining energy at exit |
| Lost Visitors | Visitors who exited with energy < 0.20 |
| Avg Peak Exhibit Utilization | Mean peak occupancy % across all 7 exhibits |
| Total Revenue (EUR) | Tickets + food + gift shop |
| Busiest Exhibit | Exhibit with highest peak visitor count |
| Visitor Breakdown | Count per subtype |

---

## How to Extend

| Goal | File to edit |
|------|-------------|
| Add a new animal species | `animals.py` — subclass the right category; add to `AnimalFactory.register_all()` |
| Add a new exhibit zone | `exhibits.py` — subclass `AbstractZoneFactory`; add `.with_zone()` in `main.py` |
| Change visitor count range | `main.py` — edit `random.randint(200, 600)` |
| Change visitor subtype ratios | `main.py` — edit fractions in `generate_visitor_counts()` |
| Change ticket booth count | `main.py` — edit `_TICKET_BOOTHS = 3` |
| Change simulation day length | `zoo.py` — `SimulationConfig.real_duration_seconds` |
| Add a new worker role | `workers.py` + `threads.py` — new class + new thread |
| Add a new KPI | `zoo.py` — `Zoo.kpi_report()` |
| Add a new animal inspection | `animals.py` — subclass `AnimalVisitor`, implement `visit_*` methods |
| Add a new incident type | `workers.py` — add to the relevant `IncidentHandler.HANDLES` set |
| Change exhibit capacities | Each factory's `create_exhibit()` method in `exhibits.py` |
