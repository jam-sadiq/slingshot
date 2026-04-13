# Slingshot 🪐

A two-player gravity-based space shooter written in Python with pygame.

Originally written in 2007 by Jonathan Musther and Bart Mak and I received it from Hans Peter Bischof at RIT. Ported to Python 3 by a later contributor.

---

## What is the game?

Two spaceships face each other across a field of planets. On each turn, one player aims and fires a missile. The missile does **not** travel in a straight line — the gravity of every planet bends its path. The skill is in predicting the curve and using the planets to your advantage, like a slingshot.

The game ends after a set number of rounds. The player with the most points wins.

---

## How to run it

### Prerequisites

- Python 3.9 or newer
- [uv](https://docs.astral.sh/uv/) — a fast Python package manager

### Install uv (if you don't have it)

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Clone and run

```bash
git clone https://github.com/YOUR_USERNAME/slingshot.git
cd slingshot

# Create the virtual environment and install dependencies
uv sync

# Run the game
uv run python slingshot.py
```

---

## Project layout

```
slingshot/
├── slingshot.py      # Main game loop, Game class, entry point
├── player.py         # Player sprite, aiming, explosion animation
├── planet.py         # Planet sprite, mass/gravity properties
├── menu.py           # All menu classes (main menu, numeric pickers, etc.)
├── general.py        # Shared helpers: image loader, line-circle intersection
├── settings.py       # All tunable constants in one place
├── particle.py       # Particle system for explosions (not included here)
├── pyproject.toml    # uv / pip project definition
└── data/             # Images and fonts
    ├── backdrop-full.png
    ├── red_ship.png
    ├── blue_ship.png
    ├── planet_1.png … planet_8.png
    ├── explosion.png
    ├── explosion-5.png
    ├── explosion-10.png
    ├── menu.png
    ├── box.png
    ├── tick.png
    ├── tick_inactive.png
    ├── help.png
    ├── welcome.png
    ├── icon64x64.png
    └── FreeSansBold.ttf
```

---

## Controls

| Key | Action |
|-----|--------|
| ← / → | Rotate aim |
| ↑ / ↓ | Increase / decrease power |
| Space or Enter | Fire |
| Escape | Open / close menu |
| Shift + arrow | Fine adjustment |
| Ctrl + arrow | Coarse adjustment |

---

## Settings (settings.py)

All game constants live in `settings.py`. Key ones to tweak:

| Setting | Default | Description |
|---------|---------|-------------|
| `MAX_SHOTS` | 5 | Shots allowed per round |
| `MAX_ROUNDS` | 3 | Number of rounds per game |
| `MAX_PLANETS` | 2 | Maximum planets per round |
| `g` | 120 | Gravity strength |
| `BOUNCE` | False | Missiles bounce off planets |
| `INVISIBLE` | False | Planets invisible until round ends |
| `FIXED_POWER` | False | Lock power at `POWER` value |
| `PARTICLES` | False | Enable explosion particles |

---

## Scoring

| Event | Points |
|-------|--------|
| Hit opponent | 1500 + quick-hit bonus |
| Hit yourself | −2000 |
| Quick-hit bonus (1st shot) | +500 |
| Quick-hit bonus (2nd shot) | +200 |
| Quick-hit bonus (3rd shot) | +100 |

---

## License

GNU General Public License v2 or later. See source files for full text.
