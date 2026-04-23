# animals.py
# ─────────────────────────────────────────────────────────────────────────────
#  ANIMAL HIERARCHY
#
#Design patterns housed here (animals own these concepts):
#    Pattern 1  — Factory Method  : AnimalFactory.create(species, ...)
#    Pattern 4  — Prototype       : clone_animal(original, new_name, new_age)
#    Pattern 7  — Bridge          : SoundSystem + SoundRenderer hierarchy
#    Pattern 11 — Visitor Pattern : AnimalVisitor + HealthInspector, HungerAuditor
#
#  Health degrades with age: health = max(0.1, 1.0 - age * 0.025)
#  Older animals are visibly less healthy and trigger the feeder sooner.
# ─────────────────────────────────────────────────────────────────────────────

import random
from utils import log, YELLOW, GREY ,  GREEN, RED, RESET
import copy



class Animal: # the base
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

#─#─ Pattern 11 ───────────────────────────────────────────────────────────────────
    def accept(self, visitor): # every subclass inherits automatically
        dispatch = {
            "Mammal": visitor.visit_mammal,
            "Bird": visitor.visit_bird,
            "Reptile": visitor.visit_reptile,
            "Amphibian": visitor.visit_amphibian,
            "Fish": visitor.visit_fish,
        }
        method = dispatch.get(self.category)
        if method:
            method(self)

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


#─#─ Pattern 1 ───────────────────────────────────────────────────────────────────

class AnimalFactory:
    _registry = {}

    @classmethod
    def register(cls, species_name, animal_class):
        cls._registry[species_name.lower()] = animal_class

    @classmethod
    def create(cls, species, name, age, exhibit_name):
        key = species.lower()
        if key not in cls._registry:
            raise ValueError(f"AnimalFactory: unknown species '{species}'")
        animal = cls._registry[key](name, age, exhibit_name)
        log("FACTORY",
            f"Created {species:<14} '{name}'  age {age:>3}  -> {exhibit_name}", GREEN)
        return animal

    @classmethod
    def available_species(cls):
        return sorted(cls._registry.keys())

    @classmethod
    def register_all(cls):
        """Register every concrete species. Call once at startup."""
        for name, klass in {
            "lion": Lion, "elephant": Elephant, "tiger": Tiger,
            "monkey": Monkey, "zebra": Zebra,
            "parrot": Parrot, "eagle": Eagle, "penguin": Penguin,
            "flamingo": Flamingo, "owl": Owl,
            "snake": Snake, "crocodile": Crocodile, "turtle": Turtle,
            "lizard": Lizard, "chameleon": Chameleon,
            "frog": Frog, "toad": Toad, "salamander": Salamander,
            "newt": Newt, "axolotl": Axolotl,
            "shark": Shark, "clownfish": Clownfish, "goldfish": Goldfish,
            "stingray": Stingray, "seahorse": Seahorse,
        }.items():
            cls._registry[name] = klass

#─#─ Pattern 4 ───────────────────────────────────────────────────────────────────

def clone_animal(animal, new_name, new_age=None):
    cloned = copy.deepcopy(animal)
    cloned.id = random.randint(1000, 9999)
    cloned.name = new_name
    if new_age is not None:
        cloned.age = new_age
        cloned.health = round(max(0.1, 1.0 - new_age * 0.025), 2)
        cloned.health_status = cloned._compute_health_status()
    cloned.hunger_level = round(random.uniform(0.1, 0.3), 2)
    log("PROTOTYPE",
        f"Cloned {animal.species:<12} '{animal.name}' -> '{new_name}'  "
        f"age {cloned.age}  health {cloned.health:.2f}", YELLOW)
    return cloned

#─#─ Pattern 7 ───────────────────────────────────────────────────────────────────
class SoundRenderer:
    def render(self, animal_name, sound):
        raise NotImplementedError


class TerminalSoundRenderer(SoundRenderer):
    def render(self, animal_name, sound):
        log("SOUND", f"{animal_name:<14}  [{sound}]  (terminal)", YELLOW)


class LogFileSoundRenderer(SoundRenderer):
    def render(self, animal_name, sound):
        log("SOUND", f"{animal_name:<14}  [{sound}]  (log-file)", GREY)


_ANIMAL_SOUNDS = {
    "Lion": "roar", "Elephant": "trumpet", "Tiger": "growl",
    "Monkey": "chatter", "Zebra": "bark", "Parrot": "squawk",
    "Eagle": "screech", "Penguin": "honk", "Flamingo": "call",
    "Owl": "hoot", "Snake": "hiss", "Crocodile": "bellow",
    "Turtle": "hiss", "Lizard": "chirp",
}


class SoundSystem:
    def __init__(self, renderer: SoundRenderer):
        self._renderer = renderer

    def set_renderer(self, renderer: SoundRenderer):
        self._renderer = renderer

    def play(self, animal):
        sound = _ANIMAL_SOUNDS.get(animal.species, "--")
        self._renderer.render(animal.name, sound)

    def play_all(self, exhibit):
        log("SOUND", f"Playing sounds for exhibit: {exhibit.name}", YELLOW)
        for animal in exhibit.animals:
            self.play(animal)

#─#─ Pattern 11 ───────────────────────────────────────────────────────────────────

class AnimalVisitor:
    def visit_mammal(self, animal):    raise NotImplementedError
    def visit_bird(self, animal):      raise NotImplementedError
    def visit_reptile(self, animal):   raise NotImplementedError
    def visit_amphibian(self, animal): raise NotImplementedError
    def visit_fish(self, animal):      raise NotImplementedError


class HealthInspector(AnimalVisitor):
    def __init__(self):
        self.flagged = []

    def _inspect(self, animal):
        status = f"health {animal.health:.2f}  [{animal.health_status}]"
        if animal.health < 0.5:
            self.flagged.append(animal)
            log("INSPECTOR",
                f"{animal.name:<14} ({animal.species:<12})  {status}"
                f"  *** ATTENTION REQUIRED ***", RED)
        else:
            log("INSPECTOR",
                f"{animal.name:<14} ({animal.species:<12})  {status}", GREEN)

    def visit_mammal(self, a):
        self._inspect(a)

    def visit_bird(self, a):
        self._inspect(a)

    def visit_reptile(self, a):
        self._inspect(a)

    def visit_amphibian(self, a):
        self._inspect(a)

    def visit_fish(self, a):
        self._inspect(a)

    def print_report(self):
        print()
        if self.flagged:
            log("INSPECTOR",
                f"Health audit complete.  {len(self.flagged)} animal(s) require attention:", RED)
            for a in self.flagged:
                print(f"    - {a.name} ({a.species})  "
                      f"health: {a.health:.2f}  [{a.health_status}]")
        else:
            log("INSPECTOR", "Health audit complete.  All animals healthy.", GREEN)


class HungerAuditor(AnimalVisitor):
    THRESHOLD = 0.5

    def __init__(self):
        self.hungry = []

    def _audit(self, animal):
        if animal.hunger_level > self.THRESHOLD:
            self.hungry.append(animal)
            log("AUDITOR",
                f"{animal.name:<14} ({animal.species:<12})  "
                f"hunger {animal.hunger_level:.2f}  *** NEEDS FEEDING ***", YELLOW)

    def visit_mammal(self, a):    self._audit(a)

    def visit_bird(self, a):      self._audit(a)

    def visit_reptile(self, a):   self._audit(a)

    def visit_amphibian(self, a): self._audit(a)

    def visit_fish(self, a):      self._audit(a)

    def print_report(self):
        print()
        log("AUDITOR",
            f"Hunger audit complete.  {len(self.hungry)} animal(s) need feeding.", YELLOW)
