# animals.py
# ─────────────────────────────────────────────────────────────────────────────
#  ANIMAL HIERARCHY
#  Health degrades with age: health = max(0.1, 1.0 - age * 0.025)
#  Older animals are visibly less healthy and trigger the feeder sooner.
# ─────────────────────────────────────────────────────────────────────────────

import random
from utils import log, YELLOW, GREY


class Animal:
    category = "Animal"

    SOUNDS = {}  # overridden per species

    def __init__(self, name, species, age, exhibit_name):
        self.id            = random.randint(1000, 9999)
        self.name          = name
        self.species       = species
        self.age           = age
        self.exhibit_name  = exhibit_name
        self.hunger_level  = round(random.uniform(0.1, 0.5), 2)

        # Health degrades with age — older animals are less healthy
        self.health        = round(max(0.1, 1.0 - age * 0.025), 2)
        self.health_status = self._compute_health_status()

    def _compute_health_status(self):
        if self.health >= 0.8:  return "Healthy"
        if self.health >= 0.5:  return "Aging"
        if self.health >= 0.3:  return "Frail"
        return "Critical"

    def eat(self):
        self.hunger_level = max(0.0, round(self.hunger_level - 0.3, 2))
        log("ANIMAL", f"{self.name:<14} ({self.species:<12})  Fed.   "
            f"Hunger: {self.hunger_bar()} {self.hunger_level:.2f}", YELLOW)

    def sleep(self):
        log("ANIMAL", f"{self.name:<14} ({self.species:<12})  Resting.", GREY)

    def make_sound(self):
        sounds = {
            "Lion": "roar", "Elephant": "trumpet", "Tiger": "growl",
            "Monkey": "chatter", "Zebra": "bark",
            "Parrot": "squawk", "Eagle": "screech", "Penguin": "honk",
            "Flamingo": "call", "Owl": "hoot",
            "Snake": "hiss", "Crocodile": "bellow", "Turtle": "hiss",
            "Lizard": "chirp", "Chameleon": "--",
            "Frog": "croak", "Toad": "croak", "Salamander": "--",
            "Newt": "--", "Axolotl": "--",
            "Shark": "--", "Clownfish": "--", "Goldfish": "--",
            "Stingray": "--", "Seahorse": "--",
        }
        sound = sounds.get(self.species, "--")
        log("ANIMAL", f"{self.name:<14} ({self.species:<12})  Sound: [{sound}]", YELLOW)

    def move_inside_exhibit(self):
        log("ANIMAL", f"{self.name:<14} moves within {self.exhibit_name}.", GREY)

    def hunger_bar(self):
        f = int(self.hunger_level * 10)
        return "[" + "#" * f + "-" * (10 - f) + "]"

    def health_bar(self):
        f = int(self.health * 10)
        return "[" + "#" * f + "-" * (10 - f) + "]"

    def status_line(self):
        return (f"  {self.id:<6}  {self.name:<14}  {self.species:<14}  "
                f"Age {self.age:>3}   "
                f"Health {self.health_bar()} {self.health:.2f}  {self.health_status:<10}  "
                f"Hunger {self.hunger_bar()} {self.hunger_level:.2f}")


# ── Mammals ───────────────────────────────────────────────────────────────────

class Mammal(Animal):
    category = "Mammal"

class Lion(Mammal):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Lion", age, exhibit_name)

class Elephant(Mammal):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Elephant", age, exhibit_name)

class Tiger(Mammal):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Tiger", age, exhibit_name)

class Monkey(Mammal):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Monkey", age, exhibit_name)

class Zebra(Mammal):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Zebra", age, exhibit_name)


# ── Birds ─────────────────────────────────────────────────────────────────────

class Bird(Animal):
    category = "Bird"

class Parrot(Bird):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Parrot", age, exhibit_name)

class Eagle(Bird):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Eagle", age, exhibit_name)

class Penguin(Bird):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Penguin", age, exhibit_name)

class Flamingo(Bird):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Flamingo", age, exhibit_name)

class Owl(Bird):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Owl", age, exhibit_name)


# ── Reptiles ──────────────────────────────────────────────────────────────────

class Reptile(Animal):
    category = "Reptile"

class Snake(Reptile):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Snake", age, exhibit_name)

class Crocodile(Reptile):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Crocodile", age, exhibit_name)

class Turtle(Reptile):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Turtle", age, exhibit_name)

class Lizard(Reptile):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Lizard", age, exhibit_name)

class Chameleon(Reptile):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Chameleon", age, exhibit_name)


# ── Amphibians ────────────────────────────────────────────────────────────────

class Amphibian(Animal):
    category = "Amphibian"

class Frog(Amphibian):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Frog", age, exhibit_name)

class Toad(Amphibian):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Toad", age, exhibit_name)

class Salamander(Amphibian):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Salamander", age, exhibit_name)

class Newt(Amphibian):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Newt", age, exhibit_name)

class Axolotl(Amphibian):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Axolotl", age, exhibit_name)


# ── Fish ──────────────────────────────────────────────────────────────────────

class Fish(Animal):
    category = "Fish"

class Shark(Fish):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Shark", age, exhibit_name)

class Clownfish(Fish):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Clownfish", age, exhibit_name)

class Goldfish(Fish):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Goldfish", age, exhibit_name)

class Stingray(Fish):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Stingray", age, exhibit_name)

class Seahorse(Fish):
    def __init__(self, name, age, exhibit_name):
        super().__init__(name, "Seahorse", age, exhibit_name)
