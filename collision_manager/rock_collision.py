import pygame
import os
import json

pygame.init()
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption("Rock Hitbox Visualizer")

ASSET_DIR = os.path.join("assets", "world")
DATA_DIR = os.path.join("assets", "data")
HITBOX_PATH = os.path.join(DATA_DIR, "rock_hitboxes.json")


ROCK_OPTIONS = [
    ("rock_small1.png", True, 0.20, 50),
    ("rock_small2.png", True, 0.10, 50),
    ("rock_medium1.png", True, 0.30, 70),
    ("rock_medium2.png", True, 0.30, 70),
    ("rock_large1.png", True, 0.10, 100),
]

default_config = {
    "collision_w_scale": 0.6,
    "collision_h_scale": 0.5,
    "offset_up_scale": 1.0,
    "offset_right_scale": 1.0
}

rock_index = 0
rock_filename, has_collision, _, size = ROCK_OPTIONS[rock_index]
flip = False

def load_image(name, size=None, flip=False):
    img = pygame.image.load(os.path.join(ASSET_DIR, name)).convert_alpha()
    if size:
        img = pygame.transform.scale(img, (size, size))
    if flip:
        img = pygame.transform.flip(img, True, False)
    return img

def draw_grid(surface, spacing=20, color=(100, 100, 100)):
    width, height = surface.get_size()
    for x in range(0, width, spacing):
        pygame.draw.line(surface, color, (x, 0), (x, height))
    for y in range(0, height, spacing):
        pygame.draw.line(surface, color, (0, y), (width, y))

def calculate_rock_hitbox(rock_size, center_x, base_y, config):
    scale_x = config["collision_w_scale"]
    scale_y = config["collision_h_scale"]
    offset_x = config["offset_right_scale"]
    offset_y = config["offset_up_scale"]

    collision_width = int(rock_size * scale_x)
    collision_height = int(rock_size * scale_y)

    hitbox_x = center_x + int(rock_size * (offset_x - 0.5))
    hitbox_y = base_y - int(collision_height * (1 + offset_y))

    return pygame.Rect(hitbox_x, hitbox_y, collision_width, collision_height)

# Load or initialize config
if os.path.exists(HITBOX_PATH):
    with open(HITBOX_PATH, "r") as f:
        raw = json.load(f)
    hitbox_config = {k: {
        "collision_w_scale": v.get("collision_w_scale", default_config["collision_w_scale"]),
        "collision_h_scale": v.get("collision_h_scale", default_config["collision_h_scale"]),
        "offset_up_scale": v.get("offset_up_scale", default_config["offset_up_scale"]),
        "offset_right_scale": v.get("offset_right_scale", default_config["offset_right_scale"]),
    } for k, v in raw.items()}
else:
    hitbox_config = {r[0]: default_config.copy() for r in ROCK_OPTIONS}

rock_img = load_image(rock_filename, size, flip=flip)
clock = pygame.time.Clock()
running = True

while running:
    screen.fill((50, 50, 50))
    draw_grid(screen)

    rock_anchor_x = screen.get_width() // 2
    rock_anchor_y = screen.get_height() // 2
    rock_x = rock_anchor_x - size // 2
    rock_y = rock_anchor_y - size

    screen.blit(rock_img, (rock_x, rock_y))

    # Anchor base center
    pygame.draw.circle(screen, (0, 255, 0), (rock_anchor_x, rock_anchor_y), 4)
    pygame.draw.line(screen, (0, 255, 0), (rock_anchor_x - 10, rock_anchor_y), (rock_anchor_x + 10, rock_anchor_y), 1)
    pygame.draw.line(screen, (0, 255, 0), (rock_anchor_x, rock_anchor_y - 10), (rock_anchor_x, rock_anchor_y + 10), 1)

    # Top-left corner of image
    pygame.draw.circle(screen, (255, 255, 0), (rock_x, rock_y), 3)

    cfg = hitbox_config[rock_filename]
    hitbox_rect = calculate_rock_hitbox(size, rock_anchor_x, rock_anchor_y, cfg)
    pygame.draw.rect(screen, (255, 0, 0), hitbox_rect, 2)

    # On-screen info
    font = pygame.font.Font(None, 24)
    labels = [
        f"{rock_filename} (LEFT/RIGHT to switch)",
        f"Width scale: {cfg['collision_w_scale']:.2f}  (W/S)",
        f"Height scale: {cfg['collision_h_scale']:.2f}  (E/D)",
        f"Offset up: {cfg['offset_up_scale']:.2f}x height  (R/F)",
        f"Offset right: {cfg['offset_right_scale']:.2f}x size  (T/G)",
        "ESC to quit | ENTER to save",
    ]
    for i, text in enumerate(labels):
        screen.blit(font.render(text, True, (255, 255, 255)), (10, 10 + i * 22))

    pygame.display.flip()
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            cfg = hitbox_config[rock_filename]
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_RETURN:
                os.makedirs(DATA_DIR, exist_ok=True)
                with open(HITBOX_PATH, "w") as f:
                    json.dump(hitbox_config, f, indent=4)
                print("Saved to rock_hitboxes.json in assets/data")

            elif event.key == pygame.K_RIGHT:
                rock_index = (rock_index + 1) % len(ROCK_OPTIONS)
                rock_filename, has_collision, _, size = ROCK_OPTIONS[rock_index]
                rock_img = load_image(rock_filename, size, flip=flip)
            elif event.key == pygame.K_LEFT:
                rock_index = (rock_index - 1) % len(ROCK_OPTIONS)
                rock_filename, has_collision, _, size = ROCK_OPTIONS[rock_index]
                rock_img = load_image(rock_filename, size, flip=flip)
            elif event.key == pygame.K_w:
                cfg["collision_w_scale"] += 0.01
            elif event.key == pygame.K_s:
                cfg["collision_w_scale"] = max(0.01, cfg["collision_w_scale"] - 0.01)
            elif event.key == pygame.K_e:
                cfg["collision_h_scale"] += 0.01
            elif event.key == pygame.K_d:
                cfg["collision_h_scale"] = max(0.01, cfg["collision_h_scale"] - 0.01)
            elif event.key == pygame.K_r:
                cfg["offset_up_scale"] += 0.1
            elif event.key == pygame.K_f:
                cfg["offset_up_scale"] = max(0, cfg["offset_up_scale"] - 0.1)
            elif event.key == pygame.K_t:
                cfg["offset_right_scale"] += 0.1
            elif event.key == pygame.K_g:
                cfg["offset_right_scale"] = max(0, cfg["offset_right_scale"] - 0.1)

pygame.quit()
