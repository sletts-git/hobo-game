import pygame
import os
import sys

# --- Settings ---
TILE_SIZE = 240  # base square tile size
MAP_WIDTH = 20
MAP_HEIGHT = 20
SCREEN_WIDTH, SCREEN_HEIGHT = 900, 700

# --- Forced Perspective Controls ---
TOP_SCALE_MIN = 0.55     # Minimum scale for tiles at the top (e.g. 0.8 to shrink, 1.0 to leave unchanged)
TOP_FALLOFF = 0.55        # How fast top tiles shrink (higher = stronger effect)

BOTTOM_SCALE_MAX = 3   # Maximum scale at the bottom
BOTTOM_FALLOFF = 0.55     # How fast bottom tiles grow (higher = stronger effect)

# --- Init ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Isometric Depth Scaling")
clock = pygame.time.Clock()

# --- Load Tile ---
tile_path = os.path.join("assets", "world", "tiles", "world", "grassland1.png")
if not os.path.exists(tile_path):
    print("Missing tile image at:", tile_path)
    sys.exit()

tile_img = pygame.image.load(tile_path).convert_alpha()

# --- Rotate once and optionally squash to diamond ---
rotated = pygame.transform.rotate(tile_img, 45)
base_w, base_h = rotated.get_width(), rotated.get_height()
diamond_tile = pygame.transform.scale(rotated, (base_w, int(base_h * 0.5)))

# --- Camera ---
camera_x, camera_y = 0, 0

def world_to_iso(x, y, camera_y):
    iso_x = (x - y) * (TILE_SIZE // 2)
    base_iso_y = (x + y) * (TILE_SIZE // 4)

    # Simulate on-screen Y to calculate scale
    screen_y = base_iso_y - camera_y
    relative_y = screen_y - SCREEN_HEIGHT // 2
    half_screen = SCREEN_HEIGHT // 2

    if relative_y < 0:
        norm = min(1, -relative_y / half_screen)
        scale = 1.0 - TOP_FALLOFF * norm
        scale = max(TOP_SCALE_MIN, scale)
    else:
        norm = min(1, relative_y / half_screen)
        scale = 1.0 + BOTTOM_FALLOFF * norm
        scale = min(BOTTOM_SCALE_MAX, scale)

    # Apply scale to vertical spacing as well
    iso_y = (x + y) * (TILE_SIZE // 4) * scale

    return iso_x, iso_y, scale


# --- Main Loop ---
running = True
while running:
    screen.fill((30, 30, 30))

    # Handle Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move Camera
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: camera_x -= 10
    if keys[pygame.K_RIGHT]: camera_x += 10
    if keys[pygame.K_UP]: camera_y -= 10
    if keys[pygame.K_DOWN]: camera_y += 10

    # Draw Isometric Map with Tunable Perspective
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            iso_x, iso_y, scale = world_to_iso(x, y, camera_y)

            screen_x = iso_x - camera_x
            screen_y = iso_y - camera_y

            # Perspective scaling relative to camera
            relative_y = screen_y - SCREEN_HEIGHT // 2
            half_screen = SCREEN_HEIGHT // 2

            if relative_y < 0:
                norm = min(1, -relative_y / half_screen)
                scale = 1.0 - TOP_FALLOFF * norm
                scale = max(TOP_SCALE_MIN, scale)
            else:
                norm = min(1, relative_y / half_screen)
                scale = 1.0 + BOTTOM_FALLOFF * norm
                scale = min(BOTTOM_SCALE_MAX, scale)

            scaled_tile = pygame.transform.scale(diamond_tile, (
                int(diamond_tile.get_width() * scale),
                int(diamond_tile.get_height() * scale)
            ))

            offset_x = scaled_tile.get_width() // 2
            offset_y = scaled_tile.get_height()
            screen.blit(scaled_tile, (screen_x - offset_x, screen_y - offset_y + 5))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()