# main_menu.py
import pygame
import os
import math

import game_state
import save_manager
from entity import Character, Player, load_image

WIDTH, HEIGHT = 1260, 700
WORLD_WIDTH, WORLD_HEIGHT = WIDTH * 4, HEIGHT * 4


ASSET_DIR = "assets"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (180, 180, 180)

class Button:
    def __init__(self, x, y, w, h, text, callback, font_size=36):
        self.rect = pygame.Rect(x, y, w, h)
        self.original_rect = self.rect.copy()
        self.text = text
        self.callback = callback
        self.color = GRAY
        self.hover_color = WHITE
        self.font = pygame.font.Font(None, font_size)
        self.hovered_last_frame = False
        self.is_pressed = False

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)

        self.hovered_last_frame = is_hovered

        draw_rect = self.rect.inflate(-4, -4) if self.is_pressed else self.rect
        pygame.draw.rect(screen, self.hover_color if is_hovered else self.color, draw_rect)
        pygame.draw.rect(screen, BLACK, draw_rect, 2)

        text_surf = self.font.render(self.text, True, BLACK)
        screen.blit(
            text_surf,
            (draw_rect.centerx - text_surf.get_width() // 2, draw_rect.centery - text_surf.get_height() // 2)
        )

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.is_pressed:
                self.callback()
            self.is_pressed = False


class MainMenu:
    MENU_MAIN = 0
    MENU_SETTINGS = 1
    MENU_STATS = 2
    MENU_UNLOCKS = 3

    def __init__(self, screen_width, screen_height, start_callback):
        self.state = self.MENU_MAIN
        self.buttons = []
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.Font(None, 50)
        self.volume_font = pygame.font.Font(None, 36)
        self.start_callback = start_callback

        self.volume = 1.0  # SFX volume
        self.music_volume = 1.0  # Background music volume

        self.slider_rect = pygame.Rect(300, 180, 300, 8)
        self.music_slider_rect = pygame.Rect(300, 260, 300, 8)

        self.slider_handle_radius = 10
        self.dragging_volume = False
        self.dragging_music_volume = False

        self.build_main_menu()

    def build_main_menu(self):
        self.buttons = [
            Button(self.screen_width // 2 - 100, 200, 200, 60, "Start Game", self.start_callback),
            Button(self.screen_width // 2 - 100, 280, 200, 60, "Settings", lambda: self.set_state(self.MENU_SETTINGS)),
            Button(self.screen_width // 2 - 100, 360, 200, 60, "Statistics", lambda: self.set_state(self.MENU_STATS)),
            Button(self.screen_width // 2 - 100, 440, 200, 60, "Unlocks", lambda: self.set_state(self.MENU_UNLOCKS)),
        ]
        self.back_button = Button(self.screen_width // 2 - 100, self.screen_height - 80, 200, 50, "Back", lambda: self.set_state(self.MENU_MAIN))

    def set_state(self, new_state):
        self.state = new_state

    def handle_event(self, event):
        if self.state == self.MENU_MAIN:
            for button in self.buttons:
                button.handle_event(event)

        elif self.state == self.MENU_SETTINGS:
            self.back_button.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                handle_x = self.slider_rect.left + self.volume * self.slider_rect.width
                handle_y = self.slider_rect.centery
                if math.hypot(mouse_x - handle_x, mouse_y - handle_y) <= self.slider_handle_radius:
                    self.dragging_volume = True

                handle_x_music = self.music_slider_rect.left + self.music_volume * self.music_slider_rect.width
                handle_y_music = self.music_slider_rect.centery
                if math.hypot(mouse_x - handle_x_music, mouse_y - handle_y_music) <= self.slider_handle_radius:
                    self.dragging_music_volume = True

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging_volume = False
                self.dragging_music_volume = False

            elif event.type == pygame.MOUSEMOTION:
                mouse_x = event.pos[0]
                if self.dragging_volume:
                    relative_x = max(self.slider_rect.left, min(mouse_x, self.slider_rect.right))
                    self.volume = round((relative_x - self.slider_rect.left) / self.slider_rect.width, 2)

                if self.dragging_music_volume:
                    relative_x = max(self.music_slider_rect.left, min(mouse_x, self.music_slider_rect.right))
                    self.music_volume = round((relative_x - self.music_slider_rect.left) / self.music_slider_rect.width, 2)
                    pygame.mixer.music.set_volume(self.music_volume)

        elif self.state == self.MENU_STATS:
            self.back_button.handle_event(event)


        elif self.state == self.MENU_UNLOCKS:
            self.back_button.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                for i, char in enumerate(Character.all_characters):
                    x = 120 + (i % 4) * (90 + 30)
                    y = 180 + (i // 4) * (120 + 30)
                    rect = pygame.Rect(x, y, 90, 100)
                    if rect.collidepoint(mouse_pos) and char.unlocked:
                        game_state.selected_character = char
                        game_state.player = Player(char, WORLD_WIDTH // 2, WORLD_HEIGHT // 2)

                        # Update global bullet sprite and save to file
                        game_state.bullet_sprite = load_image(char.attack.sprite_name)

                        save_data = save_manager.load_save_data()
                        save_data["selected_character"] = char.name
                        save_manager.save_data(save_data)

    def draw_unlocks(self, screen, characters):
        screen.blit(self.font.render("Character Select", True, BLACK), (100, 100))
        mouse_pos = pygame.mouse.get_pos()

        start_x, start_y = 120, 180
        padding = 30
        hovered = None

        for i, char in enumerate(characters):
            x = start_x + (i % 4) * (90 + padding)
            y = start_y + (i // 4) * (120 + padding)
            rect = pygame.Rect(x, y, 90, 100)

            if not char.unlocked:
                pygame.draw.rect(screen, DARK_GRAY, rect)
            else:
                sprite = char.sprite_frames[0]
                screen.blit(sprite, (x, y))

            if rect.collidepoint(mouse_pos):
                pygame.draw.rect(screen, RED, rect, 3)
                hovered = char
            else:
                pygame.draw.rect(screen, BLACK, rect, 2)

            if not char.unlocked:
                lock_text = self.volume_font.render("LOCKED", True, RED)
                screen.blit(lock_text, (x + 5, y + 35))

        if hovered:
            info_y = self.screen_height - 200
            name_text = self.volume_font.render(f"{hovered.name}", True, BLACK)
            screen.blit(name_text, (100, info_y))

            if hovered.unlocked:
                stats = f"HP: {hovered.max_health}, Speed: {hovered.speed}, Fire Rate: {hovered.fire_rate}, Bullet DMG: {hovered.bullet_damage}"
                stats_text = self.volume_font.render(stats, True, BLACK)
                screen.blit(stats_text, (100, info_y + 40))

                attack_name = hovered.attack.name
                attack_text = self.volume_font.render(f"Weapon: {attack_name}", True, BLACK)
                screen.blit(attack_text, (100, info_y + 80))

        self.back_button.draw(screen)

    def draw(self, screen):
        from entity import Character

        #screen.fill(DARK_GRAY)

        if self.state == self.MENU_MAIN:
            title_text = self.font.render("Survivor Game", True, BLACK)
            screen.blit(title_text, (self.screen_width // 2 - title_text.get_width() // 2, 100))
            for button in self.buttons:
                button.draw(screen)

        elif self.state == self.MENU_SETTINGS:
            screen.blit(self.font.render("Settings", True, BLACK), (100, 100))

            pygame.draw.rect(screen, DARK_GRAY, self.slider_rect)
            handle_x = self.slider_rect.left + int(self.volume * self.slider_rect.width)
            handle_y = self.slider_rect.centery
            pygame.draw.circle(screen, RED, (handle_x, handle_y), self.slider_handle_radius)

            label = self.volume_font.render("SFX Volume", True, BLACK)
            value = self.volume_font.render(f"{int(self.volume * 100)}%", True, BLACK)
            screen.blit(label, (self.slider_rect.left, self.slider_rect.top - 40))
            screen.blit(value, (self.slider_rect.right + 20, self.slider_rect.top - 12))

            pygame.draw.rect(screen, DARK_GRAY, self.music_slider_rect)
            handle_x_music = self.music_slider_rect.left + int(self.music_volume * self.music_slider_rect.width)
            handle_y_music = self.music_slider_rect.centery
            pygame.draw.circle(screen, GREEN, (handle_x_music, handle_y_music), self.slider_handle_radius)

            label_music = self.volume_font.render("Music Volume", True, BLACK)
            value_music = self.volume_font.render(f"{int(self.music_volume * 100)}%", True, BLACK)
            screen.blit(label_music, (self.music_slider_rect.left, self.music_slider_rect.top - 40))
            screen.blit(value_music, (self.music_slider_rect.right + 20, self.music_slider_rect.top - 12))

            self.back_button.draw(screen)

        elif self.state == self.MENU_STATS:
            screen.blit(self.font.render("Statistics (Coming Soon)", True, BLACK), (100, 100))
            self.back_button.draw(screen)

        elif self.state == self.MENU_UNLOCKS:
            self.draw_unlocks(screen, Character.all_characters)