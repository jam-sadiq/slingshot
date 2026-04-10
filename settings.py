# This file is part of Slingshot.
#
# Slingshot is a two-dimensional strategy game where two players attempt to shoot one
# another through a section of space populated by planets. The main feature of the
# game is that the shots, once fired, are affected by the gravity of the planets.
#
# Slingshot is Copyright 2007 Jonathan Musther and Bart Mak.
# Released under the GNU General Public License version 2, or later if applicable.


class Settings:

    g = 120                         # gravity
    MAXPOWER = 350
    PLANET_SHIP_DISTANCE = 100      # distance from ships to planet-free zone (left/right)
    PLANET_EDGE_DISTANCE = 50       # distance from top/bottom edge

    PARTICLE_5_MINSPEED = 100
    PARTICLE_5_MAXSPEED = 200       # 200: easy, 300: wild
    PARTICLE_10_MINSPEED = 150
    PARTICLE_10_MAXSPEED = 250      # 250: easy, 400-500: wild
    n_PARTICLES_5 = 20              # small particles spawned from a large one
    n_PARTICLES_10 = 30             # large particles spawned from explosion

    ROTATE = True
    BOUNCE = False
    FIXED_POWER = False
    PARTICLES = False
    INVISIBLE = False
    RANDOM = False
    POWER = 200

    MAX_FLIGHT = 500                # shot timeout in frames

    MAX_PLANETS = 2

    HITSCORE = 1500
    SELFHIT = 2000
    QUICKSCORE1 = 500
    QUICKSCORE2 = 200
    QUICKSCORE3 = 100

    PENALTY_FACTOR = 5

    FPS = 30
    KEY_REPEAT = 15                 # ms between key repeat events (keep below 1000/FPS)
    KEY_DELAY = 250

    MENU_FONT_SIZE = 26
    MENU_LINEFEED = 36

    MAX_ROUNDS = 3

    MAX_SHOTS = 5

    # Size of the full universe (the scrollable/zoomable world)
    UNIVERSE_SIZE = (2400, 1800)
    # Size of the visible window
    SCREEN_SIZE = (800, 600)

    SCREEN_CENTER = (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)

    # Show this much extra margin around the missile trail when auto-zooming
    AUTO_ZOOM_MARGIN = 0.20

    # Blend toward target zoom scale at this rate each frame
    AUTO_ZOOM_SPEED = 0.1

    # Physics sub-steps per frame
    SUPERSAMPLING = 4

    INITIAL_POWER = 150

    PLAYER_1_COLOR = (255, 0, 0)
    PLAYER_2_COLOR = (132, 152, 192)

    TEXT_STATUS_COLOR = (0, 0, 0)
    TEXT_FLASH_COLOR = (0, 0, 255)

    AIM_COLOR = (255, 0, 0)
    AIM_WIDTH = 3

    OLD_TRAIL_COLOR = (0, 0, 128)
    OLD_TRAIL_WIDTH = 3
    CURRENT_TRAIL_COLOR = (192, 0, 0)
    CURRENT_TRAIL_WIDTH = 3

    NUM_PLANET_TYPES = 8
    UNIQUE_PLANETS = False
    PLANET_RADIUS_SCALE = 3

    ANGLE_STEP_SMALL = 0.25
    ANGLE_STEP_NORMAL = 1
    ANGLE_STEP_LARGE = 5

    POWER_STEP_SMALL = 1
    POWER_STEP_NORMAL = 10
    POWER_STEP_LARGE = 25
