import pygame
import os
import json
from audio import Audio

pygame.init()
screen = pygame.display.set_mode((1200, 700))
pygame.display.set_caption("Player Hitbox Visualizer")

ASSET_DIR = "assets"
DATA_DIR = os.path.join(ASSET_DIR, "data")
CONFIG_PATH = os.path.join(DATA_DIR, "player_hitboxes.json")

from entity import load_characters
audio = Audio()

characters = load_characters(audio)
current_index = 0
current_character = characters[current_index]

font = pygame.font.Font(None, 24)
clock = pygame.time.Clock()
running = True

facing_left = False  # Toggle with 'L' key

# Ensure data folder exists
os.makedirs(DATA_DIR, exist_ok=True)

# Load or create config
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r") as f:
        saved_config = json.load(f)
else:
    saved_config = {}

def get_config(char_name):
    return saved_config.get(char_name, {
        "w": 0.6,
        "h": 0.6,
        "x_off": 0.2,
        "y_off": 0.4,
        "bullet_x_off": 0,
        "bullet_y_off": 0,
        "bullet_scale_x": 1.0,
        "bullet_scale_y": 1.0
    })

# Load initial character config
current_conf = get_config(current_character.name)
hitbox_width_scale = current_conf["w"]
hitbox_height_scale = current_conf["h"]
hitbox_x_offset = current_conf["x_off"]
hitbox_y_offset = current_conf["y_off"]
bullet_x_offset = current_conf.get("bullet_x_off", 0)
bullet_y_offset = current_conf.get("bullet_y_off", 0)
bullet_scale_x = current_conf.get("bullet_scale_x", 1.0)
bullet_scale_y = current_conf.get("bullet_scale_y", 1.0)

## TODO: ADD A WAY TO CONFIGURE BASED ON BULLETS
# Bullet setup
bullet_image = pygame.image.load(os.path.join("assets", "can.png")).convert_alpha()
#bullet_image = pygame.image.load(os.path.join("assets", "can.png")).convert_alpha()


while running:
    screen.fill((30, 30, 30))

    sprite = current_character.sprite_frames[0]
    if facing_left:
        sprite = pygame.transform.flip(sprite, True, False)
    sprite_width, sprite_height = sprite.get_size()

    anchor_x = screen.get_width() // 2
    anchor_y = screen.get_height() // 2

    draw_x = anchor_x - sprite_width // 2
    draw_y = anchor_y - sprite_height

    screen.blit(sprite, (draw_x, draw_y))

    # Anchor crosshair
    pygame.draw.circle(screen, (0, 255, 0), (anchor_x, anchor_y), 4)
    pygame.draw.line(screen, (0, 255, 0), (anchor_x - 10, anchor_y), (anchor_x + 10, anchor_y), 1)
    pygame.draw.line(screen, (0, 255, 0), (anchor_x, anchor_y - 10), (anchor_x, anchor_y + 10), 1)

    # Draw character hitbox
    hitbox_width = int(sprite_width * hitbox_width_scale)
    hitbox_height = int(sprite_height * hitbox_height_scale)
    hitbox_x = anchor_x + int(sprite_width * hitbox_x_offset)
    hitbox_y = anchor_y - int(hitbox_height * (1 + hitbox_y_offset))
    hitbox = pygame.Rect(hitbox_x, hitbox_y, hitbox_width, hitbox_height)
    pygame.draw.rect(screen, (255, 0, 0), hitbox, 2)

    # Draw bullet
    bullet_img = bullet_image
    if facing_left:
        bullet_img = pygame.transform.flip(bullet_img, True, False)

    scaled_bullet = pygame.transform.scale(bullet_img, (
        int(bullet_img.get_width() * bullet_scale_x),
        int(bullet_img.get_height() * bullet_scale_y)
    ))

    if facing_left:
        bullet_x = anchor_x - bullet_x_offset - scaled_bullet.get_width()
    else:
        bullet_x = anchor_x + bullet_x_offset

    bullet_y = anchor_y + bullet_y_offset
    screen.blit(scaled_bullet, (bullet_x, bullet_y))

    bullet_hitbox = pygame.Rect(
        bullet_x,
        bullet_y,
        scaled_bullet.get_width(),
        scaled_bullet.get_height()
    )
    pygame.draw.rect(screen, (0, 200, 255), bullet_hitbox, 2)

    # Labels
    labels = [
        f"{current_character.name} (LEFT/RIGHT to switch)",
        f"Width Scale: {hitbox_width_scale:.2f} (W/S)",
        f"Height Scale: {hitbox_height_scale:.2f} (E/D)",
        f"X Offset: {hitbox_x_offset:.2f} (R/F)",
        f"Y Offset: {hitbox_y_offset:.2f} (T/G)",
        f"Bullet X Offset: {bullet_x_offset} (H/K)",
        f"Bullet Y Offset: {bullet_y_offset} (U/J)",
        f"Bullet Scale X: {bullet_scale_x:.2f} (C/V)",
        f"Bullet Scale Y: {bullet_scale_y:.2f} (B/N)",
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
                saved_config[current_character.name] = {
                    "w": round(hitbox_width_scale, 2),
                    "h": round(hitbox_height_scale, 2),
                    "x_off": round(hitbox_x_offset, 2),
                    "y_off": round(hitbox_y_offset, 2),
                    "bullet_x_off": bullet_x_offset,
                    "bullet_y_off": bullet_y_offset,
                    "bullet_scale_x": round(bullet_scale_x, 2),
                    "bullet_scale_y": round(bullet_scale_y, 2)
                }
                with open(CONFIG_PATH, "w") as f:
                    json.dump(saved_config, f, indent=2)
                print(f"Saved config for {current_character.name}:\n", json.dumps(saved_config[current_character.name], indent=2))
            elif event.key == pygame.K_RIGHT:
                current_index = (current_index + 1) % len(characters)
                current_character = characters[current_index]
                conf = get_config(current_character.name)
                hitbox_width_scale = conf["w"]
                hitbox_height_scale = conf["h"]
                hitbox_x_offset = conf["x_off"]
                hitbox_y_offset = conf["y_off"]
                bullet_x_offset = conf.get("bullet_x_off", 0)
                bullet_y_offset = conf.get("bullet_y_off", 0)
                bullet_scale_x = conf.get("bullet_scale_x", 1.0)
                bullet_scale_y = conf.get("bullet_scale_y", 1.0)
            elif event.key == pygame.K_LEFT:
                current_index = (current_index - 1) % len(characters)
                current_character = characters[current_index]
                conf = get_config(current_character.name)
                hitbox_width_scale = conf["w"]
                hitbox_height_scale = conf["h"]
                hitbox_x_offset = conf["x_off"]
                hitbox_y_offset = conf["y_off"]
                bullet_x_offset = conf.get("bullet_x_off", 0)
                bullet_y_offset = conf.get("bullet_y_off", 0)
                bullet_scale_x = conf.get("bullet_scale_x", 1.0)
                bullet_scale_y = conf.get("bullet_scale_y", 1.0)
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
            elif event.key == pygame.K_u:
                bullet_y_offset -= 5
            elif event.key == pygame.K_j:
                bullet_y_offset += 5
            elif event.key == pygame.K_h:
                bullet_x_offset -= 5
            elif event.key == pygame.K_k:
                bullet_x_offset += 5
            elif event.key == pygame.K_c:
                bullet_scale_x = max(0.1, bullet_scale_x - 0.05)
            elif event.key == pygame.K_v:
                bullet_scale_x += 0.05
            elif event.key == pygame.K_b:
                bullet_scale_y = max(0.1, bullet_scale_y - 0.05)
            elif event.key == pygame.K_n:
                bullet_scale_y += 0.05
            elif event.key == pygame.K_l:
                facing_left = not facing_left

pygame.quit()