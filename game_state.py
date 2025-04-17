# game_state.py
# Shared game state across modules (does not get saved between sessions)

# Holds the currently selected Character object (set after loading save or from main menu)
selected_character = None

# Holds the current bullet sprite associated with the selected character's attack
bullet_sprite = None

# Holds the current player class
player = None
