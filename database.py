# database.py
# =============================================================================
#  SQLITE DATABASE LAYER
#
#  Tables:
#    animals           — persistent animal registry (survives across runs)
#    animal_state      — per-run snapshot of every animal (hunger, health)
#    simulation_runs   — one row per run (KPIs)
#    visitor_log       — one row per visitor per run
#    animal_health_log — end-of-day health audit per run
#    incident_log      — one row per incident resolved
# =============================================================================

import sqlite3
import os
import threading
from datetime import datetime
from utils import log, GREEN, CYAN, GREY, RED, YELLOW


class Database:

    DB_FILE = "zoo.db"

    def __init__(self, path: str = None):
        self.path = path or self.DB_FILE
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        self._create_tables()
        self.current_run_id = None
        log("DATABASE",
            f"Connected to '{self.path}'  "
            f"({'existing' if os.path.exists(self.path) else 'new'} file)", CYAN)

    # ── schema ────────────────────────────────────────────────────────────────

    def _create_tables(self):
        with self._lock:
            self.conn.executescript("""
                CREATE TABLE IF NOT EXISTS animals (
                    animal_id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    name            TEXT    NOT NULL,
                    species         TEXT    NOT NULL,
                    category        TEXT    NOT NULL,
                    age             INTEGER NOT NULL,
                    exhibit_name    TEXT    NOT NULL,
                    is_alive        INTEGER NOT NULL DEFAULT 1,
                    hunger_level    REAL    NOT NULL DEFAULT 0.2,
                    health          REAL    NOT NULL DEFAULT 1.0,
                    health_status   TEXT    NOT NULL DEFAULT 'Healthy',
                    mother_id       INTEGER REFERENCES animals(animal_id),
                    father_id       INTEGER REFERENCES animals(animal_id),
                    born_run_id     INTEGER,
                    died_run_id     INTEGER,
                    cause_of_death  TEXT
                );

                CREATE TABLE IF NOT EXISTS animal_state (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id          INTEGER NOT NULL,
                    animal_id       INTEGER REFERENCES animals(animal_id),
                    name            TEXT,
                    species         TEXT,
                    age             INTEGER,
                    hunger_level    REAL,
                    health          REAL,
                    health_status   TEXT,
                    flagged         INTEGER DEFAULT 0,
                    event           TEXT DEFAULT 'snapshot'
                );

                CREATE TABLE IF NOT EXISTS simulation_runs (
                    run_id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_date         TEXT,
                    run_start        TEXT,
                    run_end          TEXT,
                    n_visitors       INTEGER,
                    avg_satisfaction REAL,
                    avg_energy       REAL,
                    lost_visitors    INTEGER,
                    avg_peak_util    REAL,
                    total_revenue    REAL,
                    busiest_exhibit  TEXT,
                    adult_count      INTEGER,
                    child_count      INTEGER,
                    senior_count     INTEGER,
                    student_count    INTEGER,
                    animals_died     INTEGER DEFAULT 0,
                    animals_born     INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS visitor_log (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id          INTEGER REFERENCES simulation_runs(run_id),
                    name            TEXT,
                    subtype         TEXT,
                    age             INTEGER,
                    arrival_minute  INTEGER,
                    unique_exhibits INTEGER,
                    total_visits    INTEGER,
                    satisfaction    REAL,
                    energy_at_exit  REAL,
                    money_spent     REAL
                );

                CREATE TABLE IF NOT EXISTS animal_health_log (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id          INTEGER REFERENCES simulation_runs(run_id),
                    animal_name     TEXT,
                    species         TEXT,
                    category        TEXT,
                    age             INTEGER,
                    health          REAL,
                    health_status   TEXT,
                    hunger          REAL,
                    flagged         INTEGER
                );

                CREATE TABLE IF NOT EXISTS incident_log (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id           INTEGER REFERENCES simulation_runs(run_id),
                    sim_time         TEXT,
                    incident_type    TEXT,
                    description      TEXT,
                    resolved_by      TEXT,
                    escalation_steps INTEGER
                );
            """)
            self.conn.commit()

    # ── run lifecycle ─────────────────────────────────────────────────────────

    def start_run(self, n_visitors: int) -> int:
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
                INSERT INTO simulation_runs (run_date, run_start, n_visitors)
                VALUES (?, ?, ?)
            """, (datetime.now().strftime("%Y-%m-%d"),
                  datetime.now().strftime("%H:%M:%S"),
                  n_visitors))
            self.conn.commit()
            self.current_run_id = c.lastrowid
        log("DATABASE",
            f"Run #{self.current_run_id} started  ({n_visitors} visitors expected)", CYAN)
        return self.current_run_id

    def save_run(self, kpis: dict):
        if not self.current_run_id:
            return
        with self._lock:
            self.conn.execute("""
                UPDATE simulation_runs SET
                    run_end=?, avg_satisfaction=?, avg_energy=?, lost_visitors=?,
                    avg_peak_util=?, total_revenue=?, busiest_exhibit=?,
                    adult_count=?, child_count=?, senior_count=?, student_count=?,
                    animals_died=?, animals_born=?
                WHERE run_id=?
            """, (
                datetime.now().strftime("%H:%M:%S"),
                kpis.get("avg_satisfaction"),  kpis.get("avg_energy"),
                kpis.get("lost_visitors"),     kpis.get("avg_peak_util"),
                kpis.get("total_revenue"),     kpis.get("busiest_exhibit"),
                kpis.get("adult_count", 0),    kpis.get("child_count", 0),
                kpis.get("senior_count", 0),   kpis.get("student_count", 0),
                kpis.get("animals_died", 0),   kpis.get("animals_born", 0),
                self.current_run_id,
            ))
            self.conn.commit()
        log("DATABASE", f"Run #{self.current_run_id} saved.", GREEN)

    # ── animal persistence ────────────────────────────────────────────────────

    def register_animals(self, animals: list):
        id_map = {}
        for a in animals:
            with self._lock:
                row = self.conn.execute("""
                    SELECT animal_id, hunger_level, health, health_status, is_alive
                    FROM animals
                    WHERE name=? AND species=? AND is_alive=1
                """, (a.name, a.species)).fetchone()

                if row:
                    a.hunger_level  = row["hunger_level"]
                    a.health        = row["health"]
                    a.health_status = row["health_status"]
                    animal_id = row["animal_id"]
                    self.conn.execute(
                        "UPDATE animals SET age=age+1 WHERE animal_id=?",
                        (animal_id,))
                    a.age += 1
                    a.health = round(max(0.1, 1.0 - a.age * 0.025), 2)
                    a.health_status = a._compute_health_status()
                    self.conn.commit()
                    log("DATABASE",
                        f"Loaded {a.species:<12} '{a.name}'  "
                        f"hunger={a.hunger_level:.2f}  health={a.health:.2f}", CYAN)
                else:
                    c = self.conn.cursor()
                    c.execute("""
                        INSERT INTO animals
                            (name, species, category, age, exhibit_name,
                             hunger_level, health, health_status, born_run_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (a.name, a.species, a.category, a.age, a.exhibit_name,
                          a.hunger_level, a.health, a.health_status,
                          self.current_run_id))
                    animal_id = c.lastrowid
                    self.conn.commit()
                    log("DATABASE",
                        f"Registered new {a.species:<12} '{a.name}'  "
                        f"id={animal_id}", GREEN)

            id_map[animal_id] = a
            a._db_id = animal_id

        return id_map

    def save_animal_state(self, animals: list, flagged_names: set):
        if not self.current_run_id:
            return
        with self._lock:
            for a in animals:
                db_id = getattr(a, "_db_id", None)
                self.conn.execute("""
                    INSERT INTO animal_state
                        (run_id, animal_id, name, species, age,
                         hunger_level, health, health_status, flagged, event)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'snapshot')
                """, (self.current_run_id, db_id, a.name, a.species, a.age,
                      round(a.hunger_level, 3), round(a.health, 3),
                      a.health_status, 1 if a.name in flagged_names else 0))
                if db_id:
                    self.conn.execute("""
                        UPDATE animals SET
                            hunger_level=?, health=?, health_status=?, age=?
                        WHERE animal_id=?
                    """, (round(a.hunger_level, 3), round(a.health, 3),
                          a.health_status, a.age, db_id))
            self.conn.commit()
        log("DATABASE",
            f"Animal state saved for {len(animals)} animals.", GREEN)

    def record_death(self, animal, cause: str = "starvation"):
        db_id = getattr(animal, "_db_id", None)
        if db_id and self.current_run_id:
            with self._lock:
                self.conn.execute("""
                    UPDATE animals SET is_alive=0, died_run_id=?, cause_of_death=?
                    WHERE animal_id=?
                """, (self.current_run_id, cause, db_id))
                self.conn.execute("""
                    INSERT INTO animal_state
                        (run_id, animal_id, name, species, age,
                         hunger_level, health, health_status, flagged, event)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 'died')
                """, (self.current_run_id, db_id, animal.name, animal.species,
                      animal.age, round(animal.hunger_level, 3),
                      round(animal.health, 3), animal.health_status))
                self.conn.commit()
            log("DATABASE",
                f"Death recorded: {animal.species} '{animal.name}'  "
                f"cause={cause}", RED)

    def record_birth(self, offspring, mother, father=None) -> int:
        mother_id = getattr(mother, "_db_id", None)
        father_id = getattr(father, "_db_id", None) if father else None
        with self._lock:
            c = self.conn.cursor()
            c.execute("""
                INSERT INTO animals
                    (name, species, category, age, exhibit_name,
                     hunger_level, health, health_status,
                     mother_id, father_id, born_run_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (offspring.name, offspring.species, offspring.category,
                  offspring.age, offspring.exhibit_name,
                  offspring.hunger_level, offspring.health, offspring.health_status,
                  mother_id, father_id, self.current_run_id))
            self.conn.commit()
            offspring._db_id = c.lastrowid
            if self.current_run_id:
                self.conn.execute("""
                    INSERT INTO animal_state
                        (run_id, animal_id, name, species, age,
                         hunger_level, health, health_status, flagged, event)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 'born')
                """, (self.current_run_id, offspring._db_id,
                      offspring.name, offspring.species, offspring.age,
                      offspring.hunger_level, offspring.health,
                      offspring.health_status))
                self.conn.commit()
        log("DATABASE",
            f"Birth recorded: {offspring.species} '{offspring.name}'  "
            f"id={offspring._db_id}  mother='{mother.name}'", GREEN)
        return offspring._db_id

    def living_animals(self) -> list:
        with self._lock:
            rows = self.conn.execute("""
                SELECT * FROM animals WHERE is_alive=1 ORDER BY species, name
            """).fetchall()
        return [dict(r) for r in rows]

    # ── visitor log ───────────────────────────────────────────────────────────

    def log_visitor(self, visitor, arrival_minute: int, money_start: float):
        if not self.current_run_id:
            return
        with self._lock:
            self.conn.execute("""
                INSERT INTO visitor_log
                    (run_id, name, subtype, age, arrival_minute,
                     unique_exhibits, total_visits, satisfaction, energy_at_exit, money_spent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (self.current_run_id, visitor.name, visitor.subtype, visitor.age,
                  arrival_minute, len(visitor._visited_set),
                  len(visitor.exhibits_visited),
                  round(visitor.satisfaction, 3), round(visitor.energy, 3),
                  round(money_start - visitor.money, 2)))
            self.conn.commit()

    # ── health audit ──────────────────────────────────────────────────────────

    def log_health_audit(self, animals: list, flagged_names: set):
        if not self.current_run_id:
            return
        rows = [(self.current_run_id, a.name, a.species, a.category, a.age,
                 round(a.health, 3), a.health_status, round(a.hunger_level, 3),
                 1 if a.name in flagged_names else 0) for a in animals]
        with self._lock:
            self.conn.executemany("""
                INSERT INTO animal_health_log
                    (run_id, animal_name, species, category, age,
                     health, health_status, hunger, flagged)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, rows)
            self.conn.commit()
        log("DATABASE",
            f"{len(rows)} health records saved  "
            f"({sum(r[-1] for r in rows)} flagged)", GREEN)

    # ── incident log ──────────────────────────────────────────────────────────

    def log_incident(self, incident_type, description, resolved_by,
                     escalation_steps, sim_time=""):
        if not self.current_run_id:
            return
        with self._lock:
            self.conn.execute("""
                INSERT INTO incident_log
                    (run_id, sim_time, incident_type, description,
                     resolved_by, escalation_steps)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.current_run_id,
                  sim_time or datetime.now().strftime("%H:%M:%S"),
                  incident_type, description, resolved_by, escalation_steps))
            self.conn.commit()

    # ── queries ───────────────────────────────────────────────────────────────

    def last_runs(self, n: int = 5) -> list:
        with self._lock:
            rows = self.conn.execute("""
                SELECT run_id, run_date, run_start, n_visitors,
                       avg_satisfaction, total_revenue, busiest_exhibit,
                       animals_died, animals_born
                FROM simulation_runs
                ORDER BY run_id DESC LIMIT ?
            """, (n,)).fetchall()
        return [dict(r) for r in rows]

    def animal_history(self, name: str) -> list:
        with self._lock:
            rows = self.conn.execute("""
                SELECT s.run_id, r.run_date, s.age, s.hunger_level,
                       s.health, s.health_status, s.event
                FROM animal_state s
                JOIN simulation_runs r ON s.run_id = r.run_id
                WHERE s.name = ?
                ORDER BY s.run_id
            """, (name,)).fetchall()
        return [dict(r) for r in rows]

    def print_history(self, n: int = 5):
        from utils import section, blank
        section(f"SIMULATION HISTORY  (last {n} runs)")
        blank()
        runs = self.last_runs(n)
        if not runs:
            print("  No runs recorded yet.")
            return
        print(f"  {'Run':<5}  {'Date':<12}  {'Visitors':>8}  "
              f"{'Satisfaction':>13}  {'Revenue':>10}  "
              f"{'Died':>5}  {'Born':>5}  Busiest Exhibit")
        print(f"  {'─' * 82}")
        for r in runs:
            print(f"  {r['run_id']:<5}  {r['run_date']:<12}  "
                  f"{str(r['n_visitors']):>8}  "
                  f"{str(r['avg_satisfaction'] or '-'):>13}  "
                  f"EUR {str(round(r['total_revenue'],2) if r['total_revenue'] else '-'):>7}  "
                  f"{str(r['animals_died'] or 0):>5}  "
                  f"{str(r['animals_born'] or 0):>5}  "
                  f"{r['busiest_exhibit'] or '-'}")
        blank()

    def print_animal_registry(self):
        from utils import section, blank, BOLD, RESET, GREEN, RED, YELLOW
        section("ANIMAL REGISTRY  (persistent — loaded from zoo.db)")
        blank()
        living = self.living_animals()
        if not living:
            print("  No animals in registry.")
            return
        print(f"  {'ID':<5}  {'Name':<14}  {'Species':<14}  {'Age':>4}  "
              f"{'Health':>7}  {'Status':<10}  {'Hunger':>7}  Exhibit")
        print(f"  {'─' * 80}")
        for a in living:
            color = RED if a['health'] < 0.3 else YELLOW if a['health'] < 0.5 else GREEN
            print(f"  {a['animal_id']:<5}  {a['name']:<14}  {a['species']:<14}  "
                  f"{a['age']:>4}  "
                  f"{color}{a['health']:>7.2f}{RESET}  "
                  f"{a['health_status']:<10}  "
                  f"{a['hunger_level']:>7.2f}  {a['exhibit_name']}")
        blank()

    # ── teardown ──────────────────────────────────────────────────────────────

    def close(self):
        self.conn.close()
        log("DATABASE", f"Connection to '{self.path}' closed.", GREY)
