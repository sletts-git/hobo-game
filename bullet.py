# bullet.py
import pygame
import math
import os
import json

ASSET_DIR = "assets"
DATA_DIR = os.path.join(ASSET_DIR, "data")
BULLET_CONFIG_PATH = os.path.join(DATA_DIR, "player_hitboxes.json")

# Load bullet offsets
if os.path.exists(BULLET_CONFIG_PATH):
    with open(BULLET_CONFIG_PATH, "r") as f:
        BULLET_CONFIGS = json.load(f)
else:
    BULLET_CONFIGS = {}

class Bullet:
    def __init__(self, x, y, angle, speed, damage, sprite, x_off=0, y_off=0, facing_left=False, scale_x=1.0, scale_y=1.0, sprite_name=None):
        # Scale the sprite
        original_width = sprite.get_width()
        original_height = sprite.get_height()
        scaled_width = int(original_width * BULLET_CONFIGS[sprite_name]["bullet_scale_x"])
        scaled_height = int(original_height * BULLET_CONFIGS[sprite_name]["bullet_scale_y"])
        self.sprite = pygame.transform.scale(sprite, (scaled_width, scaled_height))
        self.hit  = False

        # Set initial position
        x_off = BULLET_CONFIGS[sprite_name]["bullet_x_off"]
        y_off = BULLET_CONFIGS[sprite_name]["bullet_y_off"]
        if facing_left:
            self.x = x + 2 * x_off - original_width
        else:
            self.x = x + x_off

        self.y = y + y_off
        self.angle = angle
        self.speed = speed
        self.damage = damage

        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed

    def update(self):
        self.x += self.dx
        self.y += self.dy

    def get_position(self):
        return self.x, self.y

    def get_hitbox(self):
        return pygame.Rect(self.x, self.y, self.sprite.get_width(), self.sprite.get_height())
