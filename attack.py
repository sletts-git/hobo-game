# attack.py

class Attack:
    def __init__(self, name, description, damage, fire_rate, bullet_speed, effect=None, sprite_name="bullet.png"):
        self.name = name
        self.description = description
        self.damage = damage
        self.fire_rate = fire_rate  # Lower = faster fire rate
        self.bullet_speed = bullet_speed
        self.effect = effect  # Optional effect like "burn", "pierce"
        self.sprite_name = sprite_name  # NEW: sprite image file

    def apply_to_globals(self, globals_dict):
        globals_dict["bullet_damage"] = self.damage
        globals_dict["attack_cooldown"] = self.fire_rate
        globals_dict["bullet_speed"] = self.bullet_speed
        globals_dict["bullet_effect"] = self.effect


# -----------------------
# Define your attack list
# -----------------------

basic_attack = Attack(
    name="Basic Shot",
    description="Balanced and reliable.",
    damage=15,
    fire_rate=15,
    bullet_speed=6,
    sprite_name="bullet.png",
)

rapid_fire = Attack(
    name="Rapid Fire",
    description="Shoots fast but weaker.",
    damage=0.5,
    fire_rate=5,
    bullet_speed=5,
    sprite_name="bullet.png",
)

can = Attack(
    name="can",
    description="Slow but powerful...",
    damage=30,
    fire_rate=25,
    bullet_speed=30,
    sprite_name ="can.png",
)

# Optional: a dictionary or list for easy access
ALL_ATTACKS = {
    "basic": basic_attack,
    "rapid": rapid_fire,
    "can": can
}
