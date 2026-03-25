# zoo.py
# ─────────────────────────────────────────────────────────────────────────────
#  ZOO  —  top-level container
# ─────────────────────────────────────────────────────────────────────────────

from utils import log, section, blank, GREEN, RED, BOLD, RESET


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

    def kpi_report(self):
        section("END-OF-DAY KPI REPORT")
        blank()

        total    = len(self.visitors)
        avg_sat  = round(sum(v.satisfaction for v in self.visitors) / max(1, total), 2)
        avg_nrg  = round(sum(v.energy       for v in self.visitors) / max(1, total), 2)
        lost     = sum(1 for v in self.visitors if v.energy < 0.2)
        busiest  = max(self.exhibits, key=lambda e: e.current_visitors) if self.exhibits else None
        util_avg = round(sum(e.utilization() for e in self.exhibits) / max(1, len(self.exhibits)), 1)

        # Subtype breakdown
        subtypes = {}
        for v in self.visitors:
            subtypes[v.subtype] = subtypes.get(v.subtype, 0) + 1

        rows = [
            ("Total Visitors",               str(total)),
            ("Avg Satisfaction Score",        f"{avg_sat:.2f} / 1.00"),
            ("Avg Energy at Exit",            f"{avg_nrg:.2f} / 1.00"),
            ("Lost Visitors (energy < 0.2)",  str(lost)),
            ("Avg Exhibit Utilization",       f"{util_avg} %"),
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
