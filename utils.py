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

W = 72


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
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"  {GREY}[{ts}]{RESET}  {color}{BOLD}[{tag:<12}]{RESET}  {msg}")


def rule():
    print(f"  {GREY}{'·' * (W - 2)}{RESET}")


def blank():
    print()


def fill_bar(value, max_value, width=20, color_fn=None):
    """Generic ASCII progress bar."""
    ratio  = value / max_value if max_value else 0
    filled = int(ratio * width)
    bar    = "#" * filled + "-" * (width - filled)
    if color_fn:
        c = color_fn(ratio)
        return f"{c}[{bar}]{RESET}"
    return f"[{bar}]"
