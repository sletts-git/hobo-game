import pygame
import os

ASSET_DIR = "assets"
AUDIO_DIR = os.path.join(ASSET_DIR, "audio")

class Audio:
    def __init__(self):
        self.sounds = {}
        self.volume = 1.0
        self.load_core_sounds()
        self.load_music()

    def load_core_sounds(self):
        self.sounds = {
            "shoot": self.load_sound("shoot.wav"),
            "player_death": self.load_sound("player_death.wav"),
        }

    def load_sound(self, filename):
        path = os.path.join(AUDIO_DIR, filename)
        sound = pygame.mixer.Sound(path)
        sound.set_volume(self.volume)
        return sound

    def set_volume(self, volume):
        self.volume = volume
        for sound in self.sounds.values():
            sound.set_volume(volume)

    def get(self, key):
        return self.sounds.get(key)

    def load_music(self, music_file="bgm.mp3"):
        music_path = os.path.join(AUDIO_DIR, music_file)
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(1.0)

    def restart_music(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.play(-1)
