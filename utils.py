# utils.py
# ─────────────────────────────────────────────────────────────────────────────
#  TERMINAL FORMATTING UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

from datetime import datetime

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
MAGENTA = "\033[35m"


W = 72

# ── Simulation clock reference ─────────────────────────────────────────────
_sim_clock = None #  Set by ZooSimulation before threads start.  None = show real time.

def set_sim_clock(clock):
    global _sim_clock
    _sim_clock = clock


def _time_label(): # Returns [SIM HH:MM] when clock is running, real [HH:MM:SS] otherwise
    if _sim_clock is not None and _sim_clock.is_running():
        return f"SIM {_sim_clock.sim_time_str}"
    return datetime.now().strftime("%H:%M:%S")


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
    t = _time_label()
    print(f"  {GREY}[{t}]{RESET}  {color}{BOLD}[{tag:<12}]{RESET}  {msg}")


def rule():
    print(f"  {GREY}{'·' * (W - 2)}{RESET}")


def blank():
    print()


def fill_bar(value, max_value, width=20, color_fn=None):
    ratio  = value / max_value if max_value else 0
    filled = int(ratio * width)
    bar    = "#" * filled + "-" * (width - filled)
    if color_fn:
        c = color_fn(ratio)
        return f"{c}[{bar}]{RESET}"
    return f"[{bar}]"
