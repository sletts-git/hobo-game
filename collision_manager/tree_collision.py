import pygame
import os
import json

pygame.init()
screen = pygame.display.set_mode((1200, 700))
pygame.display.set_caption("Tree Hitbox Editor")

ASSET_DIR = "assets/world"
DATA_DIR = "assets/data"
CONFIG_PATH = os.path.join(DATA_DIR, "tree_hitboxes.json")

# Tree filenames
TREE_FILENAMES = [
    "tree_basic_green1.png",
    "tree_basic_green2.png",
    "tree_basic_green3.png",
    "tree_dead.png",
]

# Ensure data folder exists
os.makedirs(DATA_DIR, exist_ok=True)

# Load tree hitbox config
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r") as f:
        saved_config = json.load(f)
else:
    saved_config = {}

def get_config(tree_name):
    return saved_config.get(tree_name, {
        "collision_w_scale": 0.3,
        "collision_h_scale": 0.25,
        "collision_offset_x": 0.0,
        "collision_offset_y": 0.0
    })

current_index = 0
current_tree = TREE_FILENAMES[current_index]

# Load all tree images
tree_images = {
    name: pygame.image.load(os.path.join(ASSET_DIR, name)).convert_alpha()
    for name in TREE_FILENAMES
}

# Load current config
current_conf = get_config(current_tree)
hitbox_width_scale = current_conf["collision_w_scale"]
hitbox_height_scale = current_conf["collision_h_scale"]
hitbox_x_offset = current_conf["collision_offset_x"]
hitbox_y_offset = current_conf["collision_offset_y"]

font = pygame.font.Font(None, 24)
clock = pygame.time.Clock()
running = True

while running:
    screen.fill((30, 30, 30))

    sprite = tree_images[current_tree]
    sprite_width, sprite_height = 140, 140

    anchor_x = screen.get_width() // 2
    anchor_y = screen.get_height() // 2

    draw_x = anchor_x - sprite_width // 2
    draw_y = anchor_y - sprite_height

    screen.blit(sprite, (draw_x, draw_y))

    # Anchor crosshair
    pygame.draw.circle(screen, (0, 255, 0), (anchor_x, anchor_y), 4)
    pygame.draw.line(screen, (0, 255, 0), (anchor_x - 10, anchor_y), (anchor_x + 10, anchor_y), 1)
    pygame.draw.line(screen, (0, 255, 0), (anchor_x, anchor_y - 10), (anchor_x, anchor_y + 10), 1)

    # Hitbox
    hitbox_width = int(sprite_width * hitbox_width_scale)
    hitbox_height = int(sprite_height * hitbox_height_scale)
    hitbox_x = anchor_x + int(sprite_width * hitbox_x_offset) - hitbox_width // 2
    hitbox_y = anchor_y - int(hitbox_height * (1 + hitbox_y_offset))
    hitbox = pygame.Rect(hitbox_x, hitbox_y, hitbox_width, hitbox_height)
    pygame.draw.rect(screen, (255, 0, 0), hitbox, 2)

    # Labels
    labels = [
        f"Tree: {current_tree} (LEFT/RIGHT to switch)",
        f"Width Scale: {hitbox_width_scale:.2f} (W/S)",
        f"Height Scale: {hitbox_height_scale:.2f} (E/D)",
        f"X Offset: {hitbox_x_offset:.2f} (R/F)",
        f"Y Offset: {hitbox_y_offset:.2f} (T/G)",
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
                saved_config[current_tree] = {
                    "collision_w_scale": round(hitbox_width_scale, 2),
                    "collision_h_scale": round(hitbox_height_scale, 2),
                    "collision_offset_x": round(hitbox_x_offset, 2),
                    "collision_offset_y": round(hitbox_y_offset, 2)
                }
                with open(CONFIG_PATH, "w") as f:
                    json.dump(saved_config, f, indent=2)
                print(f"Saved config for {current_tree}:", json.dumps(saved_config[current_tree], indent=2))
            elif event.key == pygame.K_RIGHT:
                current_index = (current_index + 1) % len(TREE_FILENAMES)
                current_tree = TREE_FILENAMES[current_index]
                current_conf = get_config(current_tree)
                hitbox_width_scale = current_conf["collision_w_scale"]
                hitbox_height_scale = current_conf["collision_h_scale"]
                hitbox_x_offset = current_conf["collision_offset_x"]
                hitbox_y_offset = current_conf["collision_offset_y"]
            elif event.key == pygame.K_LEFT:
                current_index = (current_index - 1) % len(TREE_FILENAMES)
                current_tree = TREE_FILENAMES[current_index]
                current_conf = get_config(current_tree)
                hitbox_width_scale = current_conf["collision_w_scale"]
                hitbox_height_scale = current_conf["collision_h_scale"]
                hitbox_x_offset = current_conf["collision_offset_x"]
                hitbox_y_offset = current_conf["collision_offset_y"]
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
                hitbox_x_offset = max(-10.0, hitbox_x_offset - 0.1)
            elif event.key == pygame.K_t:
                hitbox_y_offset += 0.01
            elif event.key == pygame.K_g:
                hitbox_y_offset = max(-10.0, hitbox_y_offset - 0.1)

pygame.quit()