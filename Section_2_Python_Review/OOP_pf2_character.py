import random

class pc_character:
    def __init__(self, name, level, race, class_type, health, accuracy, defense, speed, weapon=None, condition=None):
        self.name = name
        self.level = level
        self.race = race
        self.class_type = class_type
        self.health = health
        self.max_health = health
        self.accuracy = accuracy
        self.defense = defense
        self.speed = speed
        self.weapon = weapon
        self.condition = condition if condition is not None else 'healthy'

    def heal(self, amount):
        if self.health + amount > self.max_health:
            amount = self.max_health - self.health
        self.health += amount
        print(f"{self.name} has been healed by {amount}. Current health: {self.health}")

    def attack(self, target):
        if self.accuracy + random.randint(1, 20) > target.defense:
            damage = self.level * (random.randint(1, 6) if self.weapon == 'pistol' else random.randint(1, 4))
            target.health -= damage
            print(f"{self.name} attacks {target.name} for {damage} damage.")
        else:
            print(f"{self.name} missed the attack on {target.name}.")

orik = pc_character(
    name="Orik",
    level= 1,
    race='Elf',
    class_type='gunslinger',
    health=13,
    accuracy=8,
    defense=17,
    speed=30,
    weapon='pistol'
)

cassius = pc_character(
    name="Cassius",
    level=1,
    race='Human',
    class_type='Champion',
    health=18,
    accuracy=4,
    defense=18,
    speed=20,
    weapon='guisarme'
)

cassius.attack(orik)
orik.attack(cassius)
cassius.attack(orik)
orik.attack(cassius)
cassius.attack(orik)
orik.attack(cassius)
cassius.attack(orik)
orik.attack(cassius)



print(f"{orik.name} - Health: {orik.health}, Condition: {orik.condition}")
print(f"{cassius.name} - Health: {cassius.health}, Condition: {cassius.condition}")