import pygame
import os
import json

pygame.init()
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption("Enemy Hitbox Visualizer")

from enemy import Goblin, Orc  # Add other enemies here as needed

ASSET_DIR = "assets"
CONFIG_PATH = "assets/data/enemy_hitboxes.json"

font = pygame.font.Font(None, 24)
clock = pygame.time.Clock()
running = True

enemies = [Goblin(0, 0), Orc(0, 0)]  # Add more enemy instances here
current_index = 0
current_enemy = enemies[current_index]

facing_left = False  # Toggle with 'L' key

# Load existing config or use default
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r") as f:
        saved_config = json.load(f)
else:
    saved_config = {}

def get_config(enemy_type):
    return saved_config.get(enemy_type, {
        "w": 1.0,
        "h": 1.0,
        "x_off": 0.0,
        "y_off": 0.0
    })

enemy_type = current_enemy.__class__.__name__
conf = get_config(enemy_type)
hitbox_width_scale = conf["w"]
hitbox_height_scale = conf["h"]
hitbox_x_offset = conf["x_off"]
hitbox_y_offset = conf["y_off"]

while running:
    screen.fill((30, 30, 30))

    sprite = current_enemy.frames[0]
    if facing_left:
        sprite = pygame.transform.flip(sprite, True, False)
    sprite_width, sprite_height = sprite.get_size()

    anchor_x = screen.get_width() // 2
    anchor_y = screen.get_height() // 2

    draw_x = anchor_x - sprite_width // 2
    draw_y = anchor_y - sprite_height

    screen.blit(sprite, (draw_x, draw_y))

    # Green cross at center
    pygame.draw.circle(screen, (0, 255, 0), (anchor_x, anchor_y), 4)
    pygame.draw.line(screen, (0, 255, 0), (anchor_x - 10, anchor_y), (anchor_x + 10, anchor_y), 1)
    pygame.draw.line(screen, (0, 255, 0), (anchor_x, anchor_y - 10), (anchor_x, anchor_y + 10), 1)

    hitbox_width = int(sprite_width * hitbox_width_scale)
    hitbox_height = int(sprite_height * hitbox_height_scale)

    hitbox_x = anchor_x + int(sprite_width * (hitbox_x_offset - 0.5))
    hitbox_y = anchor_y - int(hitbox_height * (1 + hitbox_y_offset))

    hitbox = pygame.Rect(hitbox_x, hitbox_y, hitbox_width, hitbox_height)
    pygame.draw.rect(screen, (255, 0, 0), hitbox, 2)

    labels = [
        f"{enemy_type} (LEFT/RIGHT to switch)",
        f"Width Scale: {hitbox_width_scale:.2f} (W/S)",
        f"Height Scale: {hitbox_height_scale:.2f} (E/D)",
        f"X Offset: {hitbox_x_offset:.2f} (R/F)",
        f"Y Offset: {hitbox_y_offset:.2f} (T/G)",
        f"Facing Left: {facing_left} (L to toggle)",
        "ENTER to save config, ESC to quit"
    ]
    for i, line in enumerate(labels):
        screen.blit(font.render(line, True, (255, 255, 255)), (10, 10 + i * 20))

    pygame.display.flip()
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_RETURN:
                saved_config[enemy_type] = {
                    "w": round(hitbox_width_scale, 2),
                    "h": round(hitbox_height_scale, 2),
                    "x_off": round(hitbox_x_offset, 2),
                    "y_off": round(hitbox_y_offset, 2)
                }
                with open(CONFIG_PATH, "w") as f:
                    json.dump(saved_config, f, indent=2)
                print(f"Saved config for {enemy_type}.")
            elif event.key == pygame.K_RIGHT:
                current_index = (current_index + 1) % len(enemies)
                current_enemy = enemies[current_index]
                enemy_type = current_enemy.__class__.__name__
                conf = get_config(enemy_type)
                hitbox_width_scale = conf["w"]
                hitbox_height_scale = conf["h"]
                hitbox_x_offset = conf["x_off"]
                hitbox_y_offset = conf["y_off"]
            elif event.key == pygame.K_LEFT:
                current_index = (current_index - 1) % len(enemies)
                current_enemy = enemies[current_index]
                enemy_type = current_enemy.__class__.__name__
                conf = get_config(enemy_type)
                hitbox_width_scale = conf["w"]
                hitbox_height_scale = conf["h"]
                hitbox_x_offset = conf["x_off"]
                hitbox_y_offset = conf["y_off"]
            elif event.key == pygame.K_w:
                hitbox_width_scale += 0.01
            elif event.key == pygame.K_s:
                hitbox_width_scale = max(0.01, hitbox_width_scale - 0.01)
            elif event.key == pygame.K_e:
                hitbox_height_scale += 0.01
            elif event.key == pygame.K_d:
                hitbox_height_scale = max(0.01, hitbox_height_scale - 0.01)
            elif event.key == pygame.K_r:
                hitbox_x_offset += 0.01
            elif event.key == pygame.K_f:
                hitbox_x_offset = max(-1.0, hitbox_x_offset - 0.01)
            elif event.key == pygame.K_t:
                hitbox_y_offset += 0.01
            elif event.key == pygame.K_g:
                hitbox_y_offset = max(-1.0, hitbox_y_offset - 0.01)
            elif event.key == pygame.K_l:
                facing_left = not facing_left

pygame.quit()
