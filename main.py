import pygame
import os
import math

# Init Pygame
pygame.init()
WIDTH, HEIGHT = 1260, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Survivor Game")

from renderer import Renderer
from audio import Audio
from entity import Player, load_characters
from biome_map import get_biome_map_colliders
from world import get_render_data
from input import get_movement_direction, should_fire
import save_manager
import game_state
from bullet import Bullet
from main_menu import MainMenu
import world

# Constants
WORLD_WIDTH, WORLD_HEIGHT = WIDTH * 4, HEIGHT * 4
FPS = 90
DIRECTION_ANGLES = {
    "right": 0, "up-right": -math.pi / 4, "up": -math.pi / 2, "up-left": -3 * math.pi / 4,
    "left": math.pi, "down-left": 3 * math.pi / 4, "down": math.pi / 2, "down-right": math.pi / 4
}

clock = pygame.time.Clock()
renderer = Renderer(screen, WIDTH, HEIGHT)

# Load Audio
audio = Audio()

# Load Characters
all_characters = load_characters(audio)
save_data = save_manager.load_save_data()
selected_character = next((c for c in all_characters if c.name == save_data["selected_character"]), all_characters[0])

# Player initialization
player = Player(selected_character, WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
camera_x = camera_y = 0
bullets = []

# Game State
MENU = "MENU"
RUNNING = "RUNNING"
PAUSED = "PAUSED"
GAME_OVER = "GAME_OVER"

state = MENU

def start_game():
    global state
    state = RUNNING

menu = MainMenu(WIDTH, HEIGHT, start_game)


# Main Game Loop
running = True
while running:
    # Handle Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == MENU:
            menu.handle_event(event)

        elif state == RUNNING:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = PAUSED

        elif state == PAUSED:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = RUNNING
                elif event.key == pygame.K_m:
                    state = MENU

        elif state == GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    player.reset(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
                    state = RUNNING
                elif event.key == pygame.K_m:
                    state = MENU

    if state == MENU:
        menu.draw(screen)
        pygame.display.flip()

    elif state == RUNNING:
        # Player Movement
        keys = pygame.key.get_pressed()
        direction = get_movement_direction(keys)
        moving = player.move(keys)
        player.update_animation(moving)

        # Bullet Firing
        ## TODO: ADD MANA/MAX MANA ATTRIBUTE TO PLAYER CLASS
        ##    ADD MANA CHECK AND ADD MANA COST TO ATTACKS
        ##      IF SHOULD_FIRE AND SOME MANA CONDITIONAL
        ##          ADD A BULLET ANIMATION WHERE THE BULLET
        ##          IS ROTATED EVERY ANIMATION FRAME
        ##          AFTER X ANIMATION FRAMES CULL BULLET?
        ##             maybe just reintroduce the cull
        if should_fire(keys):
            angle = DIRECTION_ANGLES[player.last_direction]
            bullet = Bullet(player.x, player.y, angle,
                            player.bullet_speed, player.bullet_damage,
                            player.bullet_sprite,
                            facing_left=player.facing_left, sprite_name=player.character.name)
            bullets.append(bullet)
            #audio.get("shoot").play()

        # Update Bullets
        bullets = [b for b in bullets if not b.update()]

        # Update Camera
        camera_x = player.x - WIDTH // 2
        camera_y = player.y - player.height // 2 - HEIGHT // 2

        # Get Render Data from World
        tile_layers, render_objects, center_chunk = get_render_data(
            camera_x, camera_y, screen_width=WIDTH, screen_height=HEIGHT
        )

        # Draw tile_layers
        #trees = get_biome_map_colliders()[0]
        #renderer.draw_hitboxes(player,[],[], camera_x, camera_y)
        renderer.draw(player, camera_x, camera_y, bullets, [], [], [],
                      tile_layers, render_objects, center_chunk)#, tree_colliders=trees)
        # debug_font = pygame.font.SysFont(None, 20)
        # renderer.draw_debug_chunks(world._loaded_chunks, camera_x, camera_y, debug_font)

    # Update Display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()