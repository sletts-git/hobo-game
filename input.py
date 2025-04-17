# input.py
import pygame

DIRECTION_KEYS = {
    pygame.K_UP: "up",
    pygame.K_DOWN: "down",
    pygame.K_LEFT: "left",
    pygame.K_RIGHT: "right"
}

FIRE_KEYS = [pygame.K_SPACE, pygame.K_z]
TOGGLE_HITBOX_KEY = pygame.K_h

def get_movement_direction(keys):
    """
    Returns an 8-way string direction based on key input.
    """
    up = keys[pygame.K_UP]
    down = keys[pygame.K_DOWN]
    left = keys[pygame.K_LEFT]
    right = keys[pygame.K_RIGHT]

    if up and left: return "up-left"
    if up and right: return "up-right"
    if down and left: return "down-left"
    if down and right: return "down-right"
    if up: return "up"
    if down: return "down"
    if left: return "left"
    if right: return "right"
    return None

def should_fire(keys):
    return any(keys[k] for k in FIRE_KEYS)

def is_toggle_hitbox(event):
    return event.type == pygame.KEYDOWN and event.key == TOGGLE_HITBOX_KEY