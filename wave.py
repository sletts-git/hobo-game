# wave.py
import random
import math
from enemy import Goblin, Orc

def get_safe_spawn(camera_x, camera_y, width, height, player_x, player_y, safe_radius=150):
    camera_x = int(camera_x)
    camera_y = int(camera_y)
    width = int(width)
    height = int(height)
    player_x = int(player_x)
    player_y = int(player_y)

    while True:
        # Randomly choose one of the four screen edges to spawn off of
        side = random.choice(['left', 'right', 'top', 'bottom'])

        if side == 'left':
            x = random.randint(camera_x - 500, camera_x - 100)
            y = random.randint(camera_y - 300, camera_y + height + 300)
        elif side == 'right':
            x = random.randint(camera_x + width + 100, camera_x + width + 500)
            y = random.randint(camera_y - 300, camera_y + height + 300)
        elif side == 'top':
            x = random.randint(camera_x - 300, camera_x + width + 300)
            y = random.randint(camera_y - 500, camera_y - 100)
        elif side == 'bottom':
            x = random.randint(camera_x - 300, camera_x + width + 300)
            y = random.randint(camera_y + height + 100, camera_y + height + 500)

        # Still check that enemy isn’t too close to player
        if math.hypot(player_x - x, player_y - y) > safe_radius:
            return x, y

class Wave:
    def __init__(self, goblin_count, orc_count):
        self.goblin_count = goblin_count
        self.orc_count = orc_count

    def spawn(self, camera_x, camera_y, width, height, player_x, player_y):
        new_enemies = []
        for _ in range(self.goblin_count):
            x, y = get_safe_spawn(camera_x, camera_y, width, height, player_x, player_y)
            new_enemies.append(Goblin(x, y))

        for _ in range(self.orc_count):
            x, y = get_safe_spawn(camera_x, camera_y, width, height, player_x, player_y)
            new_enemies.append(Orc(x, y))

        return new_enemies
