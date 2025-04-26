import pygame
import os
import json
import random

pygame.init()

ASSET_DIR = os.path.join("assets", "world")
DATA_DIR = os.path.join("assets", "data")
HITBOX_CONFIG_PATH = os.path.join(DATA_DIR, "building_hitboxes.json")
TOWN_LAYOUT_PATH = os.path.join(DATA_DIR, "town_layout.json")
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Town Layout Editor")

FONT = pygame.font.Font(None, 24)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
RED = (255, 0, 0)
BLUE = (100, 100, 255)

ASSET_OPTIONS = ["hut1.png", "hut2.png", "fire1.png", "log_weapon.png"]
INTERIOR_OPTIONS = {
    "hut1.png": ["hut_interior1", "hut_interior2", "hut_interior3"],
    "hut2.png": ["hut_interior1", "hut_interior2", "hut_interior3"],
}

default_hitbox_config = {
    "collision_w_scale": 0.1,
    "collision_h_scale": 0.1,
    "collision_offset_right_scale": 0.1,
    "collision_offset_up_scale": 0.1,
    "door_w_scale": 0.1,
    "door_h_scale": 0.1,
    "door_offset_right_scale": 0.1,
    "door_offset_up_scale": 0.1
}

if os.path.exists(HITBOX_CONFIG_PATH):
    with open(HITBOX_CONFIG_PATH, "r") as f:
        hitbox_config = json.load(f)
else:
    hitbox_config = {name: default_hitbox_config.copy() for name in ASSET_OPTIONS}

loaded_assets = {
    name: pygame.image.load(os.path.join(ASSET_DIR, name)).convert_alpha()
    for name in ASSET_OPTIONS
}
background = pygame.image.load(os.path.join(ASSET_DIR, "background.png")).convert()
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

selected_asset = ASSET_OPTIONS[0]
placed_objects = []
dragging_object = None
drag_offset = (0, 0)
show_controls = False
snap_to_grid = True
GRID_SIZE = 20

BUTTON_HEIGHT = 40
button_rects = [
    (pygame.Rect(10, 10 + i * (BUTTON_HEIGHT + 5), 140, BUTTON_HEIGHT), asset)
    for i, asset in enumerate(ASSET_OPTIONS)
]

control_button_rect = pygame.Rect(10, SCREEN_HEIGHT - 60, 140, 40)

def draw_buttons():
    for rect, asset in button_rects:
        pygame.draw.rect(screen, GRAY if asset != selected_asset else RED, rect)
        label = FONT.render(asset, True, BLACK)
        screen.blit(label, (rect.x + 5, rect.y + 10))

    pygame.draw.rect(screen, GRAY, control_button_rect)
    label = FONT.render("Show Controls", True, BLACK)
    screen.blit(label, (control_button_rect.x + 5, control_button_rect.y + 10))

    if show_controls:
        controls = [
            "[S] Save layout",
            "[Left Click] Place / Select",
            "[Right Click] Delete",
            "[Drag] Move selected",
            "[C] Toggle Collision",
            "[V] Toggle Door",
            "[F] Flip Horizontally",
            "[Z/X] Scale object X",
            "[R/T] Scale object Y",
            "[Shift + Arrows] Collision Scale",
            "[Ctrl + Shift + Arrows] Door Scale",
            "[Ctrl + Arrows] Collision Offset",
            "[Alt + Arrows] Door Offset",
            "[G] Toggle Grid Snap",
        ]
        for i, text in enumerate(controls):
            label = FONT.render(text, True, BLACK)
            screen.blit(label, (170, SCREEN_HEIGHT - 60 - (len(controls) - i) * 25))

def save_layout():
    data = {
        "objects": [],
        "hitboxes": {},
    }
    for obj in placed_objects:
        entry = {
            "filename": obj["filename"],
            "x": obj["x"],
            "y": obj["y"],
            "scale_x": obj["scale_x"],
            "scale_y": obj["scale_y"],
            "flipped": obj.get("flipped", False),
            "has_collision": obj.get("has_collision", False),
            "has_door": obj.get("has_door", False)
        }
        if "interior_id" in obj:
            entry["interior_id"] = obj["interior_id"]
        data["objects"].append(entry)

    for filename in hitbox_config:
        data["hitboxes"][filename] = hitbox_config[filename]

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(TOWN_LAYOUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
    print("Saved layout to assets/data/town_layout.json")

def calculate_hitbox(obj, kind):
    cfg = hitbox_config.get(obj["filename"], default_hitbox_config)
    scale = obj.get("scale_x", 1.0)
    size = int(loaded_assets[obj["filename"]].get_width() * scale)
    x, y = obj["x"], obj["y"]
    anchor_x = x + size // 2
    anchor_y = y + size

    if kind == "collision":
        w = int(size * cfg["collision_w_scale"])
        h = int(size * cfg["collision_h_scale"])
        ox = cfg["collision_offset_right_scale"]
        oy = cfg["collision_offset_up_scale"]
    elif kind == "door":
        w = int(size * cfg["door_w_scale"])
        h = int(size * cfg["door_h_scale"])
        ox = cfg["door_offset_right_scale"]
        oy = cfg["door_offset_up_scale"]
    else:
        return None

    if obj.get("flipped", False):
        ox = 1.0 - ox

    hx = anchor_x + int(size * (ox - 0.5))
    hy = anchor_y - int(h * (1 + oy))
    return pygame.Rect(hx, hy, w, h)

running = True
clock = pygame.time.Clock()

while running:
    screen.blit(background, (0, 0))
    draw_buttons()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            if control_button_rect.collidepoint(event.pos):
                show_controls = not show_controls
            elif event.button == 1:
                for rect, asset in button_rects:
                    if rect.collidepoint(event.pos):
                        selected_asset = asset
                        break
                else:
                    for obj in reversed(placed_objects):
                        img = loaded_assets[obj["filename"]]
                        rect = img.get_rect(topleft=(obj["x"], obj["y"]))
                        rect.width = int(rect.width * obj["scale_x"])
                        rect.height = int(rect.height * obj["scale_y"])
                        if rect.collidepoint(event.pos):
                            dragging_object = obj
                            drag_offset = (mouse_x - obj["x"], mouse_y - obj["y"])
                            break
                    else:
                        px, py = mouse_x, mouse_y
                        if snap_to_grid:
                            px = (px // GRID_SIZE) * GRID_SIZE
                            py = (py // GRID_SIZE) * GRID_SIZE
                        new_obj = {
                            "filename": selected_asset,
                            "x": px,
                            "y": py,
                            "scale_x": 1.0,
                            "scale_y": 1.0,
                            "flipped": False,
                            "has_collision": False,
                            "has_door": False
                        }
                        if selected_asset in INTERIOR_OPTIONS:
                            new_obj["interior_id"] = random.choice(INTERIOR_OPTIONS[selected_asset])
                        placed_objects.append(new_obj)
            elif event.button == 3:
                for obj in placed_objects[:]:
                    img = loaded_assets[obj["filename"]]
                    rect = img.get_rect(topleft=(obj["x"], obj["y"]))
                    rect.width = int(rect.width * obj["scale_x"])
                    rect.height = int(rect.height * obj["scale_y"])
                    if rect.collidepoint(event.pos):
                        placed_objects.remove(obj)
                        break

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging_object = None

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                save_layout()
            elif event.key == pygame.K_g:
                snap_to_grid = not snap_to_grid
            elif dragging_object:
                if event.key == pygame.K_c:
                    dragging_object["has_collision"] ^= True
                elif event.key == pygame.K_v:
                    dragging_object["has_door"] ^= True
                elif event.key == pygame.K_f:
                    dragging_object["flipped"] ^= True
                elif event.key == pygame.K_z:
                    dragging_object["scale_x"] = max(0.1, dragging_object["scale_x"] - 0.05)
                elif event.key == pygame.K_x:
                    dragging_object["scale_x"] += 0.05
                elif event.key == pygame.K_r:
                    dragging_object["scale_y"] += 0.05
                elif event.key == pygame.K_t:
                    dragging_object["scale_y"] = max(0.1, dragging_object["scale_y"] - 0.05)
                else:
                    mods = pygame.key.get_mods()
                    cfg = hitbox_config[dragging_object["filename"]]

                    if mods & pygame.KMOD_SHIFT and not mods & pygame.KMOD_CTRL:
                        if event.key == pygame.K_UP:
                            cfg["collision_h_scale"] += 0.01
                        elif event.key == pygame.K_DOWN:
                            cfg["collision_h_scale"] = max(0.01, cfg["collision_h_scale"] - 0.01)
                        elif event.key == pygame.K_LEFT:
                            cfg["collision_w_scale"] = max(0.01, cfg["collision_w_scale"] - 0.01)
                        elif event.key == pygame.K_RIGHT:
                            cfg["collision_w_scale"] += 0.01
                    elif mods & pygame.KMOD_SHIFT and mods & pygame.KMOD_CTRL:
                        if event.key == pygame.K_UP:
                            cfg["door_h_scale"] += 0.01
                        elif event.key == pygame.K_DOWN:
                            cfg["door_h_scale"] = max(0.01, cfg["door_h_scale"] - 0.01)
                        elif event.key == pygame.K_LEFT:
                            cfg["door_w_scale"] = max(0.01, cfg["door_w_scale"] - 0.01)
                        elif event.key == pygame.K_RIGHT:
                            cfg["door_w_scale"] += 0.01
                    elif mods & pygame.KMOD_CTRL:
                        if event.key == pygame.K_UP:
                            cfg["collision_offset_up_scale"] += 0.05
                        elif event.key == pygame.K_DOWN:
                            cfg["collision_offset_up_scale"] -= 0.05
                        elif event.key == pygame.K_LEFT:
                            cfg["collision_offset_right_scale"] -= 0.05
                        elif event.key == pygame.K_RIGHT:
                            cfg["collision_offset_right_scale"] += 0.05
                    elif mods & pygame.KMOD_ALT:
                        if event.key == pygame.K_UP:
                            cfg["door_offset_up_scale"] += 0.05
                        elif event.key == pygame.K_DOWN:
                            cfg["door_offset_up_scale"] -= 0.05
                        elif event.key == pygame.K_LEFT:
                            cfg["door_offset_right_scale"] -= 0.05
                        elif event.key == pygame.K_RIGHT:
                            cfg["door_offset_right_scale"] += 0.05

    if dragging_object:
        mx, my = pygame.mouse.get_pos()
        dragging_object["x"] = (mx - drag_offset[0]) // GRID_SIZE * GRID_SIZE if snap_to_grid else mx - drag_offset[0]
        dragging_object["y"] = (my - drag_offset[1]) // GRID_SIZE * GRID_SIZE if snap_to_grid else my - drag_offset[1]

    for obj in placed_objects:
        sprite = loaded_assets[obj["filename"]]
        w = int(sprite.get_width() * obj["scale_x"])
        h = int(sprite.get_height() * obj["scale_y"])
        image = pygame.transform.scale(sprite, (w, h))
        if obj.get("flipped"):
            image = pygame.transform.flip(image, True, False)
        screen.blit(image, (obj["x"], obj["y"]))

        if obj.get("has_collision"):
            rect = calculate_hitbox(obj, "collision")
            if rect: pygame.draw.rect(screen, RED, rect, 2)
        if obj.get("has_door"):
            rect = calculate_hitbox(obj, "door")
            if rect: pygame.draw.rect(screen, BLUE, rect, 2)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
