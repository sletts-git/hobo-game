# item_drop.py
import pygame
import os
import random
import time

ASSET_DIR = os.path.join("assets", "drops")
item_size = 40

def load_image(name):
    return pygame.transform.scale(
        pygame.image.load(os.path.join(ASSET_DIR, name)).convert_alpha(),
        (item_size, item_size)
    )

ITEM_SPRITES = {
    "max_health": load_image("item_max_heal.png"),
    "heal": load_image("item_heal.png"),
    "speed": load_image("item_speed.png"),
    "fire_rate": load_image("item_fire_rate.png"),
    "bullet_damage": load_image("item_bullet_damage.png"),
}

class ItemDrop:
    def __init__(self, x, y, item_type, pickup_sound, volume=1.0):
        self.spawn_time = time.time()
        self.expiration_time = 36  # seconds
        self.pickup_sound = pickup_sound
        self.pickup_sound.set_volume(volume)
        self.x = x
        self.y = y
        self.type = item_type
        self.sprite = ITEM_SPRITES[self.type]
        self.radius = 50  # pickup range

    def is_expired(self):
        return (time.time() - self.spawn_time) > self.expiration_time

    def draw(self, screen, camera_x, camera_y):
        screen.blit(self.sprite, (self.x - camera_x, self.y - camera_y))

    def set_volume(self, volume):
        self.pickup_sound.set_volume(volume)

    def check_pickup(self, player_x, player_y):
        if abs(self.x - player_x) < self.radius and abs(self.y - player_y) < self.radius:
            self.pickup_sound.play()
            return True
        return False
