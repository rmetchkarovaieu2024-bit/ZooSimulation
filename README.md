# Zoo Operations System Simulation

A terminal-based simulation of a full zoological park operating day (09:00 – 18:00), built in Python using Agent-Based and Discrete-Event principles with native threading. The zoo **persists state across runs** — animals age, get sick, reproduce, and die over time, and every run's KPIs are stored in a SQLite database.

---

## How to Run

```bash
python3 main.py          # single run
python3 run_batch.py     # N runs back-to-back (default: 10)
rm zoo.db                # reset the database and start fresh
```

No external dependencies. Requires **Python 3.8+**.

Every run is different — daily visitor count is drawn randomly between 200 and 600, arrival times are generated dynamically, exhibit popularity varies within realistic ranges, and incidents are randomly selected from a typed pool.

To suppress terminal output during batch runs, set in `utils.py`:
```python
SILENT = True
```

---

## Project Structure

```
zoo_project/
├── main.py          Entry point — builds the zoo, generates the day, runs simulation
├── animals.py       Animal hierarchy + Factory Method, Prototype, Bridge, Visitor Pattern + lifecycle
├── exhibits.py      Exhibit + Abstract Factory (7 zone factories), Composite, Iterator
├── visitors.py      Visitor hierarchy + Prototype (clone_visitor), VisitorFactory
├── workers.py       Worker hierarchy + Chain of Responsibility
├── zoo.py           Zoo container + Singleton, Builder, Facade
├── threads.py       All simulation threads + LifecycleThread + semaphore concurrency control
├── database.py      Full SQLite persistence layer — 6 tables, thread-safe with Lock()
├── utils.py         Terminal colour codes, log(), sim clock, SILENT flag
├── run_batch.py     Batch runner — executes main.py N times sequentially
└── zoo.db           SQLite database (auto-generated on first run)
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

Every exhibit is created by a dedicated `AbstractZoneFactory` subclass. Popularity is randomised within a realistic range each run.

| Factory | Exhibit | Capacity | Type | Popularity Range |
|---------|---------|----------|------|-----------------|
| `SavannahFactory` | Savannah Enclosure | 25 | Outdoor | 7 – 10 |
| `PrimateFactory` | Primate Zone | 20 | Outdoor | 6 – 9 |
| `ElephantFactory` | Elephant Grounds | 30 | Outdoor | 6 – 9 |
| `AquaticFactory` | Aquarium | 15 | Indoor | 5 – 8 |
| `BirdHouseFactory` | Tropical Bird House | 12 | Indoor | 5 – 8 |
| `ReptileFactory` | Reptile House | 8 | Indoor | 4 – 7 |
| `AmphibianFactory` | Amphibian Centre | 7 | Indoor | 3 – 6 |

---

## Animal Lifecycle

Each run represents one simulated day. Animal state **persists across runs** via the SQLite `animals` table.

### Ageing & Health

```python
health = max(0.1, 1.0 - age * 0.025)
```

| Health | Status | Example |
|--------|--------|---------|
| 0.80–1.00 | Healthy | Simba (Lion, age 5) |
| 0.50–0.79 | Aging | Raja (Tiger, age 18) |
| 0.30–0.49 | Frail | Crunch (Crocodile, age 25) |
| 0.00–0.29 | Critical | Shell (Turtle, age 40+) |

Older animals get hungry faster:
```python
hunger_rate = BASE_RATE × (2.0 - health)
```
A Critical animal accumulates hunger roughly twice as fast as a Healthy one.

### Death System

Three independent death paths run every tick per animal:

| Cause | Condition | Probability |
|-------|-----------|-------------|
| Starvation | hunger > 0.85 for 8+ consecutive ticks | Deterministic |
| Old age | health < 0.15 | 0.02% per tick (~6% per run) |
| Accident | any living animal | 0.0005% per tick (very rare) |

The feeder intervenes when `hunger_level > 0.78`, giving animals a realistic
chance of starving if feeding is delayed. All deaths are recorded in the database
with cause and run number.

### Birth System

`LifecycleThread` runs after every simulated day:
- Scans all exhibits for living same-species pairs where both animals are `Healthy`
- **15% procreation chance** per compatible pair
- Offspring created via `clone_animal()` with `age=0`, `health=1.0`, `hunger=0.1`
- Name drawn from a species-specific pool (e.g. Lions: Kion, Kiara, Nuka, Vitani, Taka)
- Health degrades naturally on subsequent runs following the age formula
- Birth recorded in `animals` and `animal_state` tables with `mother_id` and `father_id`

---

## Behavioural Rules

### Visitor Subtypes

| Subtype | Age | Move Penalty | Dwell Multiplier | Can Revisit | Energy (start) |
|---------|-----|-------------|-----------------|-------------|----------------|
| Child | < 12 | 0.03 | 0.8× | Yes | 0.50–1.00 |
| Student | 12–21 | 0.05 | 1.0× | No | 0.50–1.00 |
| Adult | 22–60 | 0.05 | 1.0× | No | 0.50–1.00 |
| Senior | > 60 | 0.08 | 1.6× | No | 0.50–1.00 |

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
base_dwell = 3 + popularity × 1.5   minutes (± random variation)
actual_dwell = base_dwell × subtype_multiplier
```

| Popularity | Base Dwell | Senior Dwell (×1.6) |
|-----------|-----------|---------------------|
| 4 | ~7 min | ~11 min |
| 6 | ~11 min | ~18 min |
| 8 | ~15 min | ~24 min |
| 10 | ~17 min | ~27 min |

---

## Arrival Schedule

| Window | Weight | Pattern |
|--------|--------|---------|
| 09:00–10:00 | 10% | Early openers |
| 10:00–11:30 | 28% | Morning rush |
| 11:30–13:00 | 18% | Late morning |
| 13:00–14:30 | 8% | Post-lunch dip |
| 14:30–16:00 | 24% | Afternoon peak |
| 16:00–17:30 | 12% | Wind-down |

**3 ticket booths**, each processing one visitor every 2 minutes, give a combined throughput of one arrival every 0.67 minutes. Each `VisitorThread` sleeps until its assigned arrival minute, then enters the zoo — no batching, no manual scheduling.

---

## Thread Architecture

```
ZooSimulation
├── ClockThread              Maps real elapsed time → sim time (09:00–18:00)
│                            Announces milestones: 10:00, 12:00, 15:00, 16:00, 17:30, 18:00
├── ExhibitThread  (×7)      One per exhibit — cleanliness decays with visitor count each tick
├── AnimalThread   (×N)      One per animal — hunger increases + all 3 death checks per tick
├── VisitorThread  (×N)      One per visitor — arrival wait → semaphore → full journey
│   └── _semaphore(50)       Hard cap on 50 concurrent active journeys (prevents SIGSEGV)
└── WorkerThread
    ├── CleanerThread        Cleans exhibits below 0.60 cleanliness every 3 ticks
    ├── FeederThread         Feeds any exhibit with an animal above 0.78 hunger every 2 ticks
    ├── TicketSellerThread   Opens gate, logs expected visitor count
    ├── ShopEmployeeThread   Restocks shop at end of day
    └── SecurityThread       Patrols zones every 5 ticks; manages crowd; fires end-of-day incident

LifecycleThread              Runs after all visitors leave — procreation + death confirmation
```

The semaphore allows all visitor threads to start immediately (so arrival-time
sleeping works correctly) but limits how many can actively run their journey
at once. Without this cap, 400+ simultaneous threads cause a SIGSEGV (signal 11)
on macOS.

---

## Incident System

Incidents are typed and drawn randomly each run from three dedicated pools:

**crowd** (15 scenarios) — visitor misbehaviour:
> *"Visitor tried to ride Dumbo — cited 'the movie' as legal precedent"*
> *"Child stuck head through Primate Zone fence — monkeys are grooming it"*
> *"Influencer setting up ring light inside Aquarium — disrupting fish circadian rhythms"*

**sick_animal** (11 scenarios) — animal escapes and wildlife chaos:
> *"Tortoise Shell escaped — spotted moving at 0.02 km/h toward the car park"*
> *"Chameleon Kali missing — exhibit appears empty but 'something keeps breathing'"*
> *"Parrot learned to say 'FIRE' and is screaming it repeatedly near the Aquarium"*

**infrastructure** (10 scenarios) — operational failures:
> *"Ticket machine printing in Latin — IT unable to explain why"*
> *"Staff WhatsApp group accidentally added a parrot — it keeps replying"*
> *"Exhibit lighting in Reptile House set to 'disco mode' — reptiles unbothered"*

Between 1 and 5 typed incidents fire via Chain of Responsibility during the day
(count randomised per run). One additional random incident fires at end-of-day
with 65% probability.

---

## Database Schema (`zoo.db`)

All SQLite writes are wrapped in `threading.Lock()` to prevent concurrent write errors across visitor threads.

| Table | Contents |
|-------|----------|
| `animals` | Persistent registry — name, species, age, health, hunger, `is_alive`, `mother_id`, `father_id`, `cause_of_death` |
| `animal_state` | Per-run snapshot per animal — event type: `snapshot`, `born`, or `died` |
| `simulation_runs` | KPIs per run — visitors, satisfaction, revenue, busiest exhibit, died, born |
| `visitor_log` | One row per visitor — unique exhibits, total visits, satisfaction, money spent |
| `animal_health_log` | End-of-day health audit — all animals, flagged for vet attention if health < 0.5 |
| `incident_log` | Every resolved incident — type, description, resolver, escalation steps, sim time |

---

## Simulation Flow

| Stage | What happens |
|-------|-------------|
| Singleton check | Proves `SimulationConfig` returns the same instance every call |
| Factory Method | Registers all 25 species in `AnimalFactory` |
| Abstract Factory + Builder | All 7 zone factories build exhibits + animals; Zoo assembled fluently |
| Database | `register_animals()` loads saved hunger/health from previous run; ages animals +1 |
| Prototype — animals | Baby lion Mufasa cloned from Simba |
| Prototype — visitors | `VisitorFactory` generates N visitors via cloning with randomised stats |
| Composite | Exhibits grouped into Indoor / Outdoor `ExhibitGroup` objects |
| Bridge | Animal sounds played via `TerminalSoundRenderer` then `LogFileSoundRenderer` |
| Worker shifts | All 5 workers start; zoo opens |
| Morning status | Exhibit snapshot before any visitors |
| Iterator | Exhibits printed by popularity |
| Feeding show | Savannah animals fed; sounds triggered |
| Visitor journeys | All N visitor threads start; each waits for its arrival minute |
| Animal threads | Hunger + death checks run concurrently throughout the day |
| Visitor Pattern | `HealthInspector` and `HungerAuditor` scan every animal via `animal.accept()` |
| Chain of Responsibility | 1–5 random typed incidents dispatched: Security → Vet → Manager |
| Lifecycle | `LifecycleThread` — procreation, births recorded, deaths confirmed |
| Database | Animal state, visitor log, health audit, KPIs all saved |
| History | `print_history()` shows last N runs with died/born counts |

---

## Design Patterns

### Creational

| # | Pattern | File | Class / Function |
|---|---------|------|-----------------|
| 1 | **Factory Method** | `animals.py` | `AnimalFactory.create("Lion", ...)` — creates any of 25 species by name string |
| 2 | **Abstract Factory** | `exhibits.py` | 7 zone factories — each produces a complete themed exhibit as a unit |
| 3 | **Builder** | `zoo.py` | `ZooBuilder(...).with_zone().with_workers().build()` — fluent zoo construction |
| 4 | **Prototype** | `animals.py` `visitors.py` | `clone_animal()` for breeding + visitor generation via `VisitorFactory` |
| 5 | **Singleton** | `zoo.py` | `SimulationConfig` — `__new__` guarantees one global config instance |

### Structural

| # | Pattern | File | Class / Function |
|---|---------|------|-----------------|
| 6 | **Composite** | `exhibits.py` | `ExhibitGroup` — group operations on Indoor / Outdoor exhibit sets |
| 7 | **Bridge** | `animals.py` | `SoundSystem(renderer)` — swap renderers at runtime without touching animals |

### Behavioural

| # | Pattern | File | Class / Function |
|---|---------|------|-----------------|
| 8 | **Facade** | `zoo.py` | `ZooFacade` — single entry point hiding all subsystem complexity |
| 9 | **Chain of Responsibility** | `workers.py` | `SecurityHandler → VetHandler → ZooManagerHandler` — incident escalation |
| 10 | **Iterator** | `exhibits.py` | `ExhibitIterator(exhibits, order="popularity")` — ordered traversal |
| 11 | **Visitor Pattern** | `animals.py` | `HealthInspector`, `HungerAuditor` — new operations without modifying animal classes |

### Terminal Log Tags

| Tag | Pattern |
|-----|---------|
| `[SINGLETON  ]` | Singleton |
| `[FACTORY    ]` | Factory Method |
| `[ABSTRACT_F ]` | Abstract Factory |
| `[BUILDER    ]` | Builder |
| `[PROTOTYPE  ]` | Prototype |
| `[VISITOR_F  ]` | Visitor Factory (Prototype) |
| `[COMPOSITE  ]` | Composite |
| `[SOUND]` / `[BRIDGE]` | Bridge |
| `[FACADE     ]` | Facade |
| `[CHAIN      ]` | Chain of Responsibility |
| `[ITERATOR   ]` | Iterator |
| `[INSPECTOR]` / `[AUDITOR]` | Visitor Pattern |
| `[DATABASE   ]` | Persistence |
| `[LIFECYCLE  ]` | Birth / Death |

---

## Workers

| Name | Role | Salary | Shift |
|------|------|--------|-------|
| Maria | Cleaner | EUR 1,200/mo | 08:00–16:00 |
| Carlos | Feeder | EUR 1,400/mo | 07:00–15:00 |
| Ana | Ticketero | EUR 1,300/mo | 09:00–18:00 |
| Pedro | Shop Employee | EUR 1,100/mo | 10:00–19:00 |
| Marcos | Security | EUR 1,500/mo | 08:00–20:00 |

---

## Key Performance Indicators

Printed at the end of every run and saved to `simulation_runs`:

| KPI | Description |
|-----|-------------|
| Total Visitors | Number who entered |
| Avg Satisfaction Score | Mean satisfaction at exit (0.00–1.00) |
| Avg Energy at Exit | Mean remaining energy at exit |
| Lost Visitors | Visitors who exited with energy < 0.20 |
| Avg Peak Exhibit Utilization | Mean peak occupancy % across all 7 exhibits |
| Total Revenue (EUR) | Tickets + food + gift shop combined |
| Busiest Exhibit | Exhibit with highest peak visitor count |
| Animals Died | Deaths this run (starvation / old age / accident) |
| Animals Born | Births from end-of-day lifecycle |
| Visitor Breakdown | Count per subtype (Adult / Child / Senior / Student) |

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
| Change death probabilities | `threads.py` — `AnimalThread.run()` probability constants |
| Change procreation rate | `threads.py` — `LifecycleThread.PROCREATION_CHANCE` |
| Add a new worker role | `workers.py` + `threads.py` — new class + new thread |
| Add a new KPI | `zoo.py` — `Zoo.kpi_report()` |
| Add a new animal inspection | `animals.py` — subclass `AnimalVisitor`, implement `visit_*` methods |
| Add a new incident | `threads.py` — add string to relevant key in `SecurityThread.INCIDENTS_BY_TYPE` |
| Add a new incident type | `threads.py` + `workers.py` — new key in `INCIDENTS_BY_TYPE` + handler logic |
| Run in silent batch mode | `utils.py` — set `SILENT = True`; run `python3 run_batch.py` |
