# ticket.py
# ─────────────────────────────────────────────────────────────────────────────
#  TICKET
# ─────────────────────────────────────────────────────────────────────────────

import random
from datetime import datetime


class Ticket:
    def __init__(self, visitor):
        self.id           = random.randint(100000, 999999)
        self.visitor_type = visitor.subtype
        self.valid_date   = datetime.now().strftime("%Y-%m-%d")
        self.price        = (8.0  if visitor.subtype == "Child"  else
                             5.0  if visitor.subtype == "Senior" else 12.0)

    def validate_ticket(self):
        return True
