# renderer.py
import pygame
import math
from world import get_render_data, load_image

class Renderer:
    def __init__(self, screen, width, height, tile_size=150):
        self.screen = screen
        self.WIDTH = width
        self.HEIGHT = height
        self.TILE_SIZE = tile_size
        self.DEBUG_DRAW_HITBOXES = False

    def draw(self, player, camera_x, camera_y, bullets, enemies, dead_entities, item_drops, tile_layers, render_objects, center_chunk, tree_colliders=None):
        self.screen.fill((0, 0, 0))
        render_queue = []

        for tile_img, x, y in tile_layers:
            sx, sy = x - camera_x, y - camera_y
            self.screen.blit(tile_img, (sx, sy))

        # Add world objects to render queue
        for obj in render_objects:
            img = load_image(obj["filename"])
            scale_x, scale_y = obj.get("scale_x", 1.0), obj.get("scale_y", 1.0)
            flipped = obj.get("flipped", False)

            if flipped:
                img = pygame.transform.flip(img, True, False)
            if scale_x != 1.0 or scale_y != 1.0:
                img = pygame.transform.scale(img, (int(img.get_width() * scale_x), int(img.get_height() * scale_y)))

            sx, sy = obj["x"] - camera_x, obj["y"] - camera_y
            anchor_y = obj["y"] + img.get_height()
            render_queue.append((anchor_y, img, obj["x"], obj["y"]))

        # Add dead entities
        render_queue += [ent.get_render_data() for ent in dead_entities if not ent.done]

        # Add enemies
        render_queue += [e.get_render_data() for e in enemies if not e.is_dead]

        # Add player
        render_queue.append(player.get_render_data())

        # Y-sort
        render_queue.sort(key=lambda t: t[0])

        # Draw sorted entities and objects
        for _, img, x, y in render_queue:
            self.screen.blit(img, (x - camera_x, y - camera_y))

        # Draw rotated bullets after sorting
        for bullet in bullets:
            rotated = pygame.transform.rotate(bullet.sprite, -math.degrees(bullet.angle))
            sx, sy = bullet.x - camera_x, bullet.y - camera_y
            self.screen.blit(rotated, (sx, sy))

        # Item drops
        for item in item_drops:
            item.draw(self.screen, camera_x, camera_y)

        if tree_colliders:
            for rect in tree_colliders:
                pygame.draw.rect(self.screen, (255, 0, 0), rect.move(-camera_x, -camera_y), 20)

        # Optional debug overlay
        if self.DEBUG_DRAW_HITBOXES:
            self.draw_hitboxes(player, bullets, enemies, camera_x, camera_y)

    def draw_hitboxes(self, player, bullets, enemies, camera_x, camera_y):
        for e in enemies:
            pygame.draw.rect(self.screen, (255, 0, 255), e.get_hitbox().move(-camera_x, -camera_y), 2)
        for b in bullets:
            pygame.draw.rect(self.screen, (0, 255, 255), b.get_hitbox().move(-camera_x, -camera_y), 2)
        # pygame.draw.rect(self.screen, (255, 255, 0), player.get_hitbox().move(-camera_x, -camera_y), 2)

    def draw_ui(self, font, wave, score, kills, current_hp, max_hp):
        self.screen.blit(font.render(f"Wave: {wave}", True, (0, 0, 0)), (self.WIDTH // 2 - 60, 10))
        self.screen.blit(font.render(f"Score: {score}", True, (0, 0, 0)), (self.WIDTH - 150, 10))
        self.screen.blit(font.render(f"Kills: {kills}", True, (0, 0, 0)), (10, 30))

        pygame.draw.rect(self.screen, (255, 0, 0), (10, 10, 100, 10))
        pygame.draw.rect(self.screen, (0, 255, 0), (10, 10, 100 * (current_hp / max_hp), 10))

    def draw_chunk_center(self, chunk, camera_x, camera_y):
        TILE_SIZE = 150
        CHUNK_SIZE = 5
        chunk_w = TILE_SIZE * CHUNK_SIZE
        chunk_h = TILE_SIZE * CHUNK_SIZE

        # World-space center of chunk
        cx, cy = chunk
        world_x = cx * chunk_w + chunk_w // 2
        world_y = cy * chunk_h + chunk_h // 2

        # Convert to screen space
        screen_x = world_x - camera_x
        screen_y = world_y - camera_y

        color = (160, 32, 240)  # Purple
        size = 30  # 5x larger (original was ~6)

        pygame.draw.circle(self.screen, color, (screen_x, screen_y), size)
        pygame.draw.line(self.screen, color, (screen_x - size, screen_y), (screen_x + size, screen_y), 4)
        pygame.draw.line(self.screen, color, (screen_x, screen_y - size), (screen_x, screen_y + size), 4)

    def draw_debug_chunks(self, loaded_chunks, camera_x, camera_y, font):
        for (cx, cy) in loaded_chunks:
            TILE_SIZE = 150
            CHUNK_SIZE = 5  # in tiles
            world_x = cx * CHUNK_SIZE * TILE_SIZE
            world_y = cy * CHUNK_SIZE * TILE_SIZE
            screen_x = world_x - camera_x
            screen_y = world_y - camera_y

            # Draw boundary
            pygame.draw.rect(self.screen, (255, 0, 0),
                             (screen_x, screen_y, CHUNK_SIZE * TILE_SIZE, CHUNK_SIZE * TILE_SIZE), 1)

            # Draw coordinates label
            label = font.render(f"{cx},{cy}", True, (255, 255, 255))
            self.screen.blit(label, (screen_x + 4, screen_y + 4))
