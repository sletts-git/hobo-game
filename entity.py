import os
import json
import math
import random
import pygame
from attack import basic_attack, rapid_fire, can
from biome_map import get_biome_map_colliders
from item_drop import ItemDrop

ASSET_DIR = "assets"
AUDIO_DIR = os.path.join(ASSET_DIR, "audio")
DATA_DIR = os.path.join(ASSET_DIR, "data")
PLAYER_HITBOX_PATH = os.path.join(DATA_DIR, "player_hitboxes.json")
ENEMY_HITBOX_PATH = os.path.join(DATA_DIR, "enemy_hitboxes.json")

HITBOX_CONFIGS = {}
for path in [PLAYER_HITBOX_PATH, ENEMY_HITBOX_PATH]:
    if os.path.exists(path):
        with open(path, "r") as f:
            HITBOX_CONFIGS.update(json.load(f))

def load_image(name, size=None):
    image = pygame.image.load(os.path.join(ASSET_DIR, name)).convert_alpha()
    if size:
        image = pygame.transform.scale(image, size)
    return image

def load_sound(name, volume=1.0):
    path = os.path.join(AUDIO_DIR, name)
    sound = pygame.mixer.Sound(path)
    sound.set_volume(volume)
    return sound

class DeathAnimation:
    def __init__(self, x, y, width, height, frames, facing_left=False, frame_interval=10):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.frames = frames
        self.facing_left = facing_left
        self.frame_index = 0
        self.timer = 0
        self.frame_interval = frame_interval
        self.done = False

    def update(self):
        if self.done:
            return
        self.timer += 1
        if self.timer > self.frame_interval:
            self.frame_index += 1
            self.timer = 0
            if self.frame_index >= len(self.frames):
                self.done = True

    def get_render_data(self):
        if self.done:
            return None
        frame = self.frames[self.frame_index]
        if self.facing_left:
            frame = pygame.transform.flip(frame, True, False)
        draw_x = self.x - self.width // 2
        draw_y = self.y - self.height
        return self.y, frame, draw_x, draw_y

class BaseEntity:
    def __init__(self, x, y, width, height, health, speed, frames, death_frames, hitbox_key, idle_frame=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.health = self.max_health = health
        self.speed = speed
        self.idle_frame = idle_frame
        self.frames = frames
        self.death_frames = death_frames
        self.hitbox_config = HITBOX_CONFIGS.get(hitbox_key, {"w": 1.0, "h": 1.0, "x_off": 0.0, "y_off": 0.0})

        self.animation_index = 0
        self.animation_timer = 0
        self.facing_left = False
        self.is_dead = False
        self.death_animation = None

    def get_hitbox(self):
        config = self.hitbox_config
        sprite_width = self.width
        sprite_height = self.height

        hitbox_width = int(sprite_width * config["w"])
        hitbox_height = int(sprite_height * config["h"])

        hitbox_x = self.x + int(sprite_width * config["x_off"])
        hitbox_y = self.y - int(hitbox_height * (1 + config["y_off"]))

        return pygame.Rect(hitbox_x, hitbox_y, hitbox_width, hitbox_height)

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.die()

    def die(self):
        if not self.is_dead:
            self.is_dead = True
            self.death_animation = DeathAnimation(
                self.x, self.y, self.width, self.height,
                self.death_frames, self.facing_left
            )

    def update_animation(self, moving=False):
        if self.is_dead and self.death_animation:
            self.death_animation.update()
        elif moving:
            self.animation_timer += 1
            if self.animation_timer > 10:
                self.animation_index = (self.animation_index + 1) % len(self.frames)
                self.animation_timer = 0

    def get_render_data(self):
        if self.is_dead and self.death_animation:
            data = self.death_animation.get_render_data()
            if data:
                _, frame, draw_x, draw_y = data
                return self.y, frame, draw_x, draw_y
            return None
        frame = self.idle_frame if hasattr(self, "is_idle") and self.is_idle and self.idle_frame else self.frames[self.animation_index]
        if self.facing_left:
            frame = pygame.transform.flip(frame, True, False)
        draw_x = self.x - self.width // 2
        draw_y = self.y - self.height
        return self.y, frame, draw_x, draw_y

class Character:
    all_characters = []

    def __init__(self, name, sprite_prefix, attack, max_health, speed, fire_rate, bullet_speed, bullet_damage, unlocked=True, death_sound=None):
        self.name = name
        self.attack = attack
        self.unlocked = unlocked
        self.death_sound = death_sound

        self.max_health = self.base_max_health = max_health
        self.speed = self.base_speed = speed
        self.fire_rate = self.base_fire_rate = fire_rate
        self.bullet_speed = self.base_bullet_speed = bullet_speed
        self.bullet_damage = self.base_bullet_damage = bullet_damage

        self.idle_frame = self.load_idle_frame(sprite_prefix)
        self.walk_frames = self.load_walk_frames(sprite_prefix)
        self.sprite_frames = self.walk_frames["down"]  # default, down frames

        self.death_frames = self.load_death_frames(sprite_prefix)

        self.sprite_width, self.sprite_height = self.sprite_frames[0].get_size()
        self.hitbox_key = name
        self.hitbox_config = HITBOX_CONFIGS.get(self.hitbox_key, {"w": 1.0, "h": 1.0, "x_off": 0.0, "y_off": 0.0})

        Character.all_characters.append(self)

    def load_walk_frames(self, prefix):
        size = (75, 95)
        try:
            walk_down = [load_image(f"{prefix}_walk{i}.png", size) for i in (1, 2)]
        except:
            walk_down = None
        try:
            walk_up = [load_image(f"{prefix}_walk{i}.png", size) for i in (3, 4)]
        except:
            walk_up = None
        return {"down": walk_down, "up": walk_up}

    def load_idle_frame(self, prefix):
        size = (75, 95)
        return load_image(f"{prefix}_idle.png", size)

    def load_death_frames(self, prefix):
        size = (90, 90)
        return [load_image(f"{prefix}_death{i}.png", size) for i in range(1, 4) if os.path.exists(os.path.join(ASSET_DIR, f"{prefix}_death{i}.png"))]

    def use_attack(self, x, y, direction, bullet_speed):
        return self.attack(x, y, direction, bullet_speed, self.bullet_damage)

    def reset_stats(self):
        self.max_health = self.base_max_health
        self.speed = self.base_speed
        self.fire_rate = self.base_fire_rate
        self.bullet_damage = self.base_bullet_damage

    def to_dict(self):
        return {"name": self.name, "unlocked": self.unlocked}


class Player(BaseEntity):
    def __init__(self, character, x, y):
        super().__init__(x, y, character.sprite_width, character.sprite_height,
                         character.max_health, character.speed,
                         character.sprite_frames, character.death_frames,
                         character.name, character.idle_frame)

        self.character = character
        self.bullet_sprite = load_image(character.attack.name + ".png")
        self.fire_rate = character.fire_rate
        self.bullet_speed = character.bullet_speed
        self.bullet_damage = character.bullet_damage
        self.last_direction = "right"

    def move(self, keys):
        move_x = move_y = 0
        if keys[pygame.K_LEFT]: move_x = -self.speed; self.last_direction = "left"; self.facing_left = True
        if keys[pygame.K_RIGHT]: move_x = self.speed; self.last_direction = "right"; self.facing_left = False
        if keys[pygame.K_UP]:
            move_y = -self.speed
            if self.last_direction == "right":
                self.last_direction = "up-right"
            elif self.last_direction == "left":
                self.last_direction = "up-left"
            else:
                self.last_direction ="up"
        if keys[pygame.K_DOWN]:
            move_y = self.speed
            if self.last_direction == "right":
                self.last_direction = "down-right"
            elif self.last_direction == "left":
                self.last_direction = "down-left"
            else:
                self.last_direction = "down"

        moving = move_x != 0 or move_y != 0

        if moving:
            mag = math.hypot(move_x, move_y)
            move_x = (move_x / mag) * self.speed
            move_y = (move_y / mag) * self.speed
            new_rect = self.get_hitbox()
            new_rect.x += move_x
            new_rect.y += move_y
            trees, rocks = get_biome_map_colliders()
            if not any(new_rect.colliderect(c) for c in trees + rocks):
                self.x += move_x
                self.y += move_y

        self.is_idle = not moving
        if "up" in self.last_direction:
            self.frames = self.character.walk_frames["up"]
        else:
            self.frames = self.character.walk_frames["down"]
        return moving

    def reset(self, x, y):
        self.x, self.y = x, y
        self.character.reset_stats()
        self.health = self.character.max_health
        self.speed = self.character.speed
        self.fire_rate = self.character.fire_rate
        self.bullet_damage = self.character.bullet_damage
        self.last_direction = "right"
        self.animation_index = self.animation_timer = 0
        self.death_animation = None
        self.is_dead = False


class Enemy(BaseEntity):
    def __init__(self, x, y, width, height, health, speed, damage, frames, death_frames, death_sounds, enemy_type):
        super().__init__(x, y, width, height, health, speed, frames, death_frames, enemy_type)
        self.damage = damage
        self.death_sounds = death_sounds
        self.enemy_type = enemy_type
        self.pickup_sound = load_sound("pickup.wav")
        self.drop_table = {
            "heal": 0.6,
            "speed": 0.25,
            "fire_rate": 0.1,
            "max_health": 0.05,
        }

    def move_toward_player(self, px, py):
        dx, dy = px - self.x, py - self.y
        mag = math.hypot(dx, dy)
        if mag:
            dx /= mag; dy /= mag
            self.x += dx * self.speed
            self.y += dy * self.speed
            self.facing_left = dx < 0

    def die(self):
        if not self.is_dead:
            super().die()
            if (channel := pygame.mixer.find_channel()):
                channel.play(random.choice(self.death_sounds))

    def roll_drop(self, volume=1.0):
        if random.random() < 0.3:
            item_type = random.choices(list(self.drop_table.keys()), weights=self.drop_table.values())[0]
            return ItemDrop(self.x, self.y, item_type, self.pickup_sound, volume)
        return None


class Goblin(Enemy):
    def __init__(self, x, y):
        width, height = 63, 54
        frames = [load_image(f"goblin_walk{i}.png", (height, width)) for i in (1, 2)]
        death_frames = [load_image(f"goblin_death{i}.png", (height, width)) for i in (1, 2)]
        sounds = [load_sound(f"goblin_death{i}.wav") for i in (1, 2)]
        super().__init__(x, y, width, height, 30, 1.9, 15, frames, death_frames, sounds, "Goblin")


class Orc(Enemy):
    def __init__(self, x, y):
        width, height = 105, 105
        frames = [load_image(f"orc_walk{i}.png", (height, width)) for i in (1, 2)]
        death_frames = [load_image(f"orc_death{i}.png", (height, width)) for i in (1, 2)]
        sounds = [load_sound(f"orc_death{i}.wav") for i in (1, 2)]
        super().__init__(x, y, width, height, 60, 1.1, 30, frames, death_frames, sounds, "Orc")


def load_characters(audio):
    Character.all_characters.clear()
    #Character("Wizard", "wizard", basic_attack, 30, 3, 15, 6,30, True, audio.get("player_death"))
    Character("Hobo", "hobo", can, 5, 50, 18, 6,15, True, audio.get("player_death"))
    #Character("Placeholder Gunner", "placeholder_gunner", basic_attack, 10, 3, 20, 6,30, False, audio.get("player_death"))
    return Character.all_characters