# This file is part of Slingshot.
#
# Slingshot is a two-dimensional strategy game where two players attempt to shoot one
# another through a section of space populated by planets. The main feature of the
# game is that the shots, once fired, are affected by the gravity of the planets.
#
# Slingshot is Copyright 2007 Jonathan Musther and Bart Mak.
# Released under the GNU General Public License version 2, or later if applicable.
#
# ABOUT THE CODE:
# Originally prototype code that became the full game. Ported from Python 2 to
# Python 3 by a later contributor. The game will eventually be ported to C++/SDL.

import asyncio                      # ← NEW: needed for pygbag web export
import pygame
from pygame.locals import *
import math
import os
import sys
from random import randint

from settings import *
from general import *
from player import *
from planet import *
from particle import *
from menu import *


class Game:

    particle_image = None
    particle_image_rect = None

    pygame.font.init()
    Settings.font = pygame.font.Font("data/FreeSansBold.ttf", 14)
    Settings.menu_font = pygame.font.Font(
        "data/FreeSansBold.ttf", Settings.MENU_FONT_SIZE)
    Settings.round_font = pygame.font.Font("data/FreeSansBold.ttf", 100)

    def __init__(self):
        pygame.display.init()

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(Settings.SCREEN_SIZE)

        icon, rect = load_image("data/icon64x64.png", (0, 0, 0))
        pygame.display.set_icon(icon)
        pygame.display.set_caption("Slingshot")

        Settings.particle_image10, Settings.particle_image10_rect = \
            load_image("data/explosion-10.png", (0, 0, 0))
        Settings.particle_image5, Settings.particle_image5_rect = \
            load_image("data/explosion-5.png", (0, 0, 0))

        Settings.menu_background, Settings.menu_rect = \
            load_image("data/menu.png", (0, 0, 0))
        Settings.box, rect = load_image("data/box.png", (0, 0, 0))
        Settings.tick, rect = load_image("data/tick.png", (0, 0, 0))
        Settings.tick_inactive, rect = \
            load_image("data/tick_inactive.png", (0, 0, 0))

        self.dim_screen = pygame.Surface(self.screen.get_size())
        self.dim_screen.set_alpha(175)
        self.dim_screen = self.dim_screen.convert_alpha()

        # Load and pre-scale background to universe size
        self.background, _r = load_image("data/backdrop-full.png")
        self.background = pygame.transform.smoothscale(
            self.background, Settings.UNIVERSE_SIZE)

        self.players = (Dummy(), Player(1), Player(2))
        self.playersprites = pygame.sprite.RenderPlain(
            (self.players[1], self.players[2]))
        self.missile = Missile()
        self.missilesprite = pygame.sprite.RenderPlain((self.missile,))

        # Current auto-zoom scale (universe units -> screen pixels)
        self.current_scale = 1.0

        # All trails shown on screen (each trail is a list of points)
        self.trails = []

        self.load_settings()

        self.main_menu = Menu("Menu")
        self.main_menu.add("Back to game")
        self.main_menu.add("New game")
        self.main_menu.add("Settings")
        self.main_menu.add("Help")
        self.main_menu.add("Quit")

        self.confirm_menu1 = Confirm(
            "Starting a new game", "will apply new settings",
            "and reset the scores")
        self.confirm_menu1.add("Yes")
        self.confirm_menu1.add("No")

        self.confirm_menu2 = Confirm(
            "Starting a new game", "will reset the scores")
        self.confirm_menu2.add("Yes")
        self.confirm_menu2.add("No")

        self.apply_menu = Confirm(
            "This will start a", "new game and reset", "the scores")
        self.apply_menu.add("Yes")
        self.apply_menu.add("No")

        self.settings_menu = Menu("Settings")
        self.settings_menu.add("Back")
        self.settings_menu.add("Game style")
        self.settings_menu.add("Game options")
        self.settings_menu.add("Apply settings")
        self.settings_menu.add("Graphics")

        self.style_menu = Menu("Game style")
        self.style_menu.add("Back")
        self.style_menu.addoption("Random", self.random)
        self.style_menu.addoption("Fixed power", self.fixed_power,
                                  not self.random)
        self.style_menu.addoption("Bounce", self.bounce, not self.random)
        self.style_menu.addoption("Invisible planets", self.invisible,
                                  not self.random)

        self.mode_menu = Menu("Game options")
        self.mode_menu.add("Back")
        self.mode_menu.add("Max number of planets")
        self.mode_menu.add("Number of rounds")
        self.mode_menu.add("Shot timeout")

        self.timeout_menu = Numeric(
            "Shot timeout", self.timeout, 250, 2000, 500)

        self.graphics_menu = Menu("Graphics")
        self.graphics_menu.add("Particles")

        self.planet_menu = Numeric(
            "Maximum number of planets", self.max_planets, 1, 8, 2)

        self.particles_menu = Menu("Particle")
        self.particles_menu.add("Back")
        self.particles_menu.add("On")
        self.particles_menu.add("Off")

        self.rounds_menu = Numeric(
            "Number of rounds", self.max_rounds, 5, 100, 0, "Infinite")

        self.help_menu = Help()
        self.welcome_menu = Welcome()
        self.set_menu(self.welcome_menu)

        self.q = False
        self.message = ""
        self.score_message = ""
        self.started = False

        self.game_init()

    # ------------------------------------------------------------------
    # Initialisation helpers
    # ------------------------------------------------------------------

    def game_init(self):
        self.new_game()
        self.round_init()
        self.bounce_count = 255
        self.bounce_count_inc = 7

    def settings_changed(self):
        return any([
            Settings.MAX_PLANETS != self.max_planets,
            Settings.MAX_FLIGHT != self.timeout,
            Settings.BOUNCE != self.bounce,
            Settings.INVISIBLE != self.invisible,
            Settings.FIXED_POWER != self.fixed_power,
            Settings.MAX_ROUNDS != self.max_rounds,
            Settings.RANDOM != self.random,
        ])

    def new_game(self):
        Settings.MAX_PLANETS = self.max_planets
        Settings.BOUNCE = self.bounce
        Settings.INVISIBLE = self.invisible
        Settings.FIXED_POWER = self.fixed_power
        Settings.MAX_ROUNDS = self.max_rounds
        Settings.RANDOM = self.random
        Settings.MAX_FLIGHT = self.timeout

        self.player = 1
        self.round = 0
        self.players[1].reset_score()
        self.players[2].reset_score()
        self.game_over = False

    def round_init(self):
        self.enable_key_repeat()

        if self.round == Settings.MAX_ROUNDS:
            self.new_game()

        if Settings.RANDOM:
            Settings.BOUNCE = (randint(0, 1) == 1)
            Settings.FIXED_POWER = (randint(0, 1) == 1)
            Settings.INVISIBLE = (randint(0, 1) == 1)

        self.round_over = False
        self.players[1].init()
        self.players[2].init()
        self.missile.reset()
        self.trails = []
        self.zoom_hold = 0

        self.firing = 0
        self.particlesystem = pygame.sprite.RenderPlain()
        self.planetsprites = self.create_planets()
        self.round += 1
        self.player = 1

        self.show_round = 100
        self.show_planets = 100 if Settings.INVISIBLE else 0

    # ------------------------------------------------------------------
    # Menu helpers
    # ------------------------------------------------------------------

    def toggle_menu(self):
        if self.menu is None:
            self.set_menu(self.main_menu)
        elif self.menu == self.main_menu:
            self.set_menu(None)
        elif self.menu == self.particles_menu:
            self.set_menu(self.graphics_menu)
        elif self.menu in (self.rounds_menu, self.planet_menu):
            self.set_menu(self.mode_menu)
        elif self.menu == self.mode_menu:
            self.set_menu(self.settings_menu)
        elif self.menu == self.style_menu:
            self.set_menu(self.settings_menu)
        elif self.menu == self.timeout_menu:
            self.set_menu(self.mode_menu)
        else:
            self.set_menu(self.main_menu)

    def set_menu(self, menu):
        self.menu = menu
        if self.menu is not None:
            self.menu.reset()
            self.disable_key_repeat()
        else:
            self.enable_key_repeat()
            self.started = True

    def enable_key_repeat(self):
        pygame.key.set_repeat(Settings.KEY_DELAY, Settings.KEY_REPEAT)

    def disable_key_repeat(self):
        pygame.key.set_repeat()

    # ------------------------------------------------------------------
    # Game-play helpers
    # ------------------------------------------------------------------

    def create_particlesystem(self, pos, n, size):
        if Settings.PARTICLES:
            nn = n // 2 if Settings.BOUNCE else n
            for _ in range(nn):
                self.particlesystem.add(Particle(pos, size))

    def create_planets(self):
        result = pygame.sprite.RenderPlain()
        n = randint(2, Settings.MAX_PLANETS)
        for _ in range(n):
            result.add(Planet(result, self.background))
        return result

    def change_angle(self, a):
        self.players[self.player].change_angle(a)

    def change_power(self, p):
        self.players[self.player].change_power(p)

    def fire(self):
        if self.round_over:
            self.round_init()
        elif not self.firing:
            self.missile.launch(self.players[self.player])
            self.players[self.player].attempts += 1
            self.last = self.player
            self.player = 0
            self.firing = 1
            self.trails.append(self.missile.trail)
            self.disable_key_repeat()

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self):
        max_extent = [0, 0]
        if self.firing:
            for p in self.missile.trail:
                ax = abs(p[0] - Settings.SCREEN_CENTER[0])
                ay = abs(p[1] - Settings.SCREEN_CENTER[1])
                if ax > max_extent[0]:
                    max_extent[0] = ax
                if ay > max_extent[1]:
                    max_extent[1] = ay

        max_extent = (
            max_extent[0] * (1 + Settings.AUTO_ZOOM_MARGIN),
            max_extent[1] * (1 + Settings.AUTO_ZOOM_MARGIN),
        )
        max_extent = (
            max(max_extent[0], Settings.SCREEN_CENTER[0]),
            max(max_extent[1], Settings.SCREEN_CENTER[1]),
        )
        max_extent = (
            max(min(max_extent[0], Settings.UNIVERSE_SIZE[0] / 2),
                -Settings.UNIVERSE_SIZE[0] / 2),
            max(min(max_extent[1], Settings.UNIVERSE_SIZE[1] / 2),
                -Settings.UNIVERSE_SIZE[1] / 2),
        )

        if self.game_over:
            max_extent = (
                Settings.UNIVERSE_SIZE[0] / 2,
                Settings.UNIVERSE_SIZE[1] / 2,
            )

        ratio = Settings.SCREEN_SIZE[0] / Settings.SCREEN_SIZE[1]
        if max_extent[1] * ratio > max_extent[0]:
            max_extent = (max_extent[1] * ratio, max_extent[1])
        else:
            max_extent = (max_extent[0], max_extent[0] / ratio)

        desired_scale = Settings.SCREEN_SIZE[0] / float(max_extent[0] * 2)

        if self.zoom_hold > 0:
            self.zoom_hold -= 1
        zoom_speed = Settings.AUTO_ZOOM_SPEED * max(
            1 - self.zoom_hold / 30.0, 0.0)

        scale = 1.0 / (
            1.0 / desired_scale * zoom_speed
            + 1.0 / self.current_scale * (1 - zoom_speed)
        )
        self.current_scale = scale

        visible_size = (
            Settings.SCREEN_SIZE[0] / scale,
            Settings.SCREEN_SIZE[1] / scale,
        )
        universe_to_visible = (
            (Settings.UNIVERSE_SIZE[0] - visible_size[0]) / 2,
            (Settings.UNIVERSE_SIZE[1] - visible_size[1]) / 2,
        )
        visible_rect = pygame.Rect(universe_to_visible, visible_size)

        normal_to_visible = (
            (Settings.SCREEN_SIZE[0] - visible_size[0]) / 2,
            (Settings.SCREEN_SIZE[1] - visible_size[1]) / 2,
        )

        def transform(p):
            return (
                (p[0] - normal_to_visible[0]) * scale,
                (p[1] - normal_to_visible[1]) * scale,
            )

        def draw_sprite(sprite):
            image = sprite.image
            pos = transform(sprite.rect.center)
            w = int(sprite.rect.width * scale)
            h = int(sprite.rect.height * scale)
            scaled = pygame.transform.smoothscale(image, (w, h))
            pos = (pos[0] - scaled.get_width() / 2,
                   pos[1] - scaled.get_height() / 2)
            self.screen.blit(scaled, pos)

        visible_background = self.background.subsurface(visible_rect)
        pygame.transform.scale(visible_background, Settings.SCREEN_SIZE,
                               self.screen)

        x1, y1 = transform((0, 0))
        x2, y2 = transform((Settings.SCREEN_SIZE[0], Settings.SCREEN_SIZE[1]))
        pygame.draw.rect(self.screen, (150, 150, 150),
                         pygame.Rect(x1, y1, x2 - x1, y2 - y1), 1)

        show_planets = False
        if not Settings.INVISIBLE:
            show_planets = True
        else:
            if self.round_over:
                if self.show_planets > 0:
                    for p in self.planetsprites:
                        p.fade(self.show_planets)
                        draw_sprite(p)
                    self.show_planets -= 1
                else:
                    show_planets = True
        if show_planets:
            for planet in self.planetsprites:
                draw_sprite(planet)

        for trail in self.trails[:-1]:
            pts = list(map(transform, trail))
            if len(pts) > 1:
                if Settings.OLD_TRAIL_WIDTH == 1:
                    pygame.draw.aalines(self.screen,
                                        Settings.OLD_TRAIL_COLOR, False, pts)
                else:
                    pygame.draw.lines(self.screen, Settings.OLD_TRAIL_COLOR,
                                      False, pts, Settings.OLD_TRAIL_WIDTH)

        if len(self.missile.trail) > 1:
            pts = list(map(transform, self.missile.trail))
            if Settings.CURRENT_TRAIL_WIDTH == 1:
                pygame.draw.aalines(self.screen,
                                    Settings.CURRENT_TRAIL_COLOR, False, pts)
            else:
                pygame.draw.lines(self.screen, Settings.CURRENT_TRAIL_COLOR,
                                  False, pts, Settings.CURRENT_TRAIL_WIDTH)

        draw_sprite(self.players[1])
        draw_sprite(self.players[2])
        if self.firing:
            draw_sprite(self.missile)

        if not self.round_over:
            self.players[self.player].draw_info(self.screen)
            self.players[self.player].draw_line(self.screen, transform)
        else:
            if self.show_round > 30:
                txt = Settings.round_font.render(
                    "Game Over", 1, Settings.TEXT_FLASH_COLOR)
                tmp = pygame.Surface(txt.get_size()).convert_alpha()
                tmp.blit(txt, (0, 0))
                tmp = tmp.convert()
                tmp.set_alpha(2 * self.show_round - 60)
                tmp.set_colorkey((0, 0, 0))
                tmp = tmp.convert_alpha()
                rect = tmp.get_rect()
                s = int((100 - self.show_round) * rect.h / 15)
                tmp = pygame.transform.scale(
                    tmp, (int(rect.w / rect.h * s), s))
                rect = tmp.get_rect()
                rect.center = (399, 299)
                self.screen.blit(tmp, rect.topleft)
                self.show_round /= 1.04
            elif self.show_planets <= 0:
                dim = pygame.Surface(self.end_round_msg.get_size())
                dim.set_alpha(175)
                dim = dim.convert_alpha()
                rect = self.end_round_msg.get_rect()
                rect.center = (399, 299)
                self.screen.blit(dim, rect.topleft)
                self.screen.blit(self.end_round_msg, rect.topleft)

        if self.firing:
            self.missile.draw_status(self.screen)
        elif self.started:
            if Settings.MAX_ROUNDS > 0:
                txt = Settings.font.render(
                    "Round %d of %d" % (self.round, Settings.MAX_ROUNDS),
                    1, Settings.TEXT_STATUS_COLOR)
            else:
                txt = Settings.font.render(
                    "Round %d" % self.round, 1, Settings.TEXT_STATUS_COLOR)
            rect = txt.get_rect()
            rect.midbottom = (399, 594)
            self.screen.blit(txt, rect.topleft)

        if self.started and not self.game_over:
            if self.show_round > 30:
                txt = Settings.round_font.render(
                    "Round %d" % self.round, 1, Settings.TEXT_FLASH_COLOR)
                tmp = pygame.Surface(txt.get_size()).convert_alpha()
                tmp.blit(txt, (0, 0))
                tmp = tmp.convert()
                tmp.set_alpha(2 * self.show_round - 60)
                tmp.set_colorkey((0, 0, 0))
                tmp = tmp.convert_alpha()
                rect = tmp.get_rect()
                s = int((100 - self.show_round) * rect.h / 25)
                tmp = pygame.transform.scale(
                    tmp, (int(rect.w / rect.h * s), s))
                rect = tmp.get_rect()
                rect.center = (399, 299)
                self.screen.blit(tmp, rect.topleft)
                self.show_round /= 1.04

        if self.menu is not None:
            if self.menu.dim:
                self.screen.blit(self.dim_screen, (0, 0))
            img = self.menu.draw()
            rect = img.get_rect()
            rect.center = (399, 299)
            self.screen.blit(img, rect.topleft)

        pygame.display.flip()

    # ------------------------------------------------------------------
    # Update / physics
    # ------------------------------------------------------------------

    def update_particles(self):
        if Settings.PARTICLES:
            for p in list(self.particlesystem):
                if p.update(self.planetsprites) == 0 or p.flight < 0:
                    if p.flight >= 0 and p.in_range():
                        if p.get_size() == 10:
                            self.create_particlesystem(
                                p.get_impact_pos(),
                                Settings.n_PARTICLES_5, 5)
                    self.particlesystem.remove(p)
                if p.flight > Settings.MAX_FLIGHT:
                    self.particlesystem.remove(p)

    def end_shot(self):
        pygame.event.clear()
        self.player = self.last
        if self.menu is None:
            self.enable_key_repeat()
        self.firing = 0
        self.zoom_hold = 45

        if self.players[1].attempts >= Settings.MAX_SHOTS:
            self.end_round()

    def menu_action(self):
        c = self.menu.get_choice()
        if self.menu == self.planet_menu:
            if c >= 0:
                self.max_planets = c
                self.toggle_menu()
        if self.menu == self.rounds_menu:
            if c >= 0:
                self.max_rounds = c
                self.toggle_menu()
        if self.menu == self.timeout_menu:
            if c >= 0:
                self.timeout = c
                self.toggle_menu()
        if c == "Quit":
            self.q = True
        elif c == "Back":
            self.toggle_menu()
        elif c == "Start":
            self.started = True
            self.current_scale = (float(Settings.SCREEN_SIZE[0])
                                  / Settings.UNIVERSE_SIZE[0])
            self.zoom_hold = 30
            self.set_menu(None)
        elif c == "Back to game":
            self.toggle_menu()
        elif c == "Apply settings":
            self.set_menu(self.apply_menu)
        elif c == "New game":
            if self.settings_changed():
                self.set_menu(self.confirm_menu1)
            else:
                self.set_menu(self.confirm_menu2)
        elif c == "Number of rounds":
            self.set_menu(self.rounds_menu)
        elif c == "Shot timeout":
            self.set_menu(self.timeout_menu)
        elif c == "Game style":
            self.set_menu(self.style_menu)
        elif c == "Random":
            self.random = not self.random
            self.style_menu.change_active("Bounce", not self.random)
            self.style_menu.change_active("Invisible planets", not self.random)
            self.style_menu.change_active("Fixed power", not self.random)
        elif c == "Help":
            self.set_menu(self.help_menu)
        elif c == "Yes":
            self.set_menu(None)
            self.save_settings()
            self.game_init()
        elif c == "No":
            self.toggle_menu()
        elif c == "Settings":
            self.set_menu(self.settings_menu)
        elif c == "Game options":
            self.set_menu(self.mode_menu)
        elif c == "Graphics":
            self.set_menu(self.graphics_menu)
        elif c == "Fixed power":
            self.fixed_power = not self.fixed_power
        elif c == "Bounce":
            self.bounce = not self.bounce
        elif c == "Invisible planets":
            self.invisible = not self.invisible
        elif c == "Max number of planets":
            self.set_menu(self.planet_menu)
        elif c == "Particles":
            self.set_menu(self.particles_menu)
        elif c == "On":
            Settings.PARTICLES = True
            self.toggle_menu()
        elif c == "Off":
            Settings.PARTICLES = False
            self.toggle_menu()

    def update(self):
        self.update_particles()
        if self.firing:
            self.firing = self.missile.update(self.planetsprites, self.players)
            if self.missile.flight < 0 and not self.missile.visible():
                self.firing = 0
            if not self.firing:
                if self.missile.visible():
                    self.create_particlesystem(
                        self.missile.get_impact_pos(),
                        Settings.n_PARTICLES_10, 10)
                self.end_shot()
        if self.menu is not None:
            self.menu_action()
        if self.players[1].shot or self.players[2].shot:
            if self.players[1].shot:
                self.players[1].update_explosion()
            else:
                self.players[2].update_explosion()
            self.disable_key_repeat()
            if not self.round_over:
                self.end_round()
        if self.menu is None:
            self.started = True

        self.bounce_count += self.bounce_count_inc
        if self.bounce_count > 255 or self.bounce_count < 125:
            self.bounce_count_inc *= -1
            self.bounce_count += 2 * self.bounce_count_inc

    def end_round(self):
        self.round_over = True

        offset1 = 50 if self.round == Settings.MAX_ROUNDS else 0
        max_shots = self.players[1].attempts >= Settings.MAX_SHOTS

        power_penalty = self.missile.get_score()
        player_shot = None
        for i in range(1, 3):
            if self.players[i].shot:
                player_shot = i

        killed_self = False
        offset = 0
        offset2 = 0
        message = ""

        if player_shot is not None or max_shots:
            i = player_shot
            if player_shot is not None and self.player == player_shot:
                message = "You shot your own ship!"
                score = Settings.SELFHIT
                self.players[i].add_score(-score)
                killed_self = True
            elif player_shot is not None and self.player == 3 - player_shot:
                message = "You hit the other ship!"
                attempts = self.players[3 - i].attempts
                if attempts == 1:
                    bonus = Settings.QUICKSCORE1
                elif attempts == 2:
                    bonus = Settings.QUICKSCORE2
                elif attempts == 3:
                    bonus = Settings.QUICKSCORE3
                else:
                    bonus = 0
                score = power_penalty + bonus + Settings.HITSCORE
                self.players[3 - i].add_score(score)
            elif max_shots:
                message = "You ran out of shots"

            offset = 0 if killed_self else 40
            offset2 = 40 if self.round == Settings.MAX_ROUNDS else 0

            self.end_round_msg = pygame.Surface(
                (450, 190 + offset + offset1 + offset2))
            self.end_round_msg.set_colorkey((0, 0, 0))
            self.end_round_msg.fill((0, 0, 0))

            if self.round == Settings.MAX_ROUNDS:
                msg = Settings.menu_font.render(
                    "Game over", 1, (255, 255, 255))
                rect = msg.get_rect()
                rect.midtop = (224, 28)
                self.end_round_msg.blit(msg, rect.topleft)

            msg = Settings.font.render(message, 1, (255, 255, 255))
            rect = msg.get_rect()
            rect.midtop = (224, 28 + offset1)
            self.end_round_msg.blit(msg, rect.topleft)

            if self.round < Settings.MAX_ROUNDS:
                msg = Settings.font.render(
                    "Press space to go to the next round", 1, (255, 255, 255))
            else:
                msg = Settings.font.render(
                    "Press space to start a new game", 1, (255, 255, 255))
                self.game_over = True
                self.zoom_hold = 45

            rect = msg.get_rect()
            rect.midtop = (224, 140 + offset + offset1 + offset2)
            self.end_round_msg.blit(msg, rect.topleft)

            pygame.draw.rect(self.end_round_msg, (150, 150, 150),
                             self.end_round_msg.get_rect(), 1)

    # ------------------------------------------------------------------
    # Settings persistence
    # ------------------------------------------------------------------

    def load_settings(self):
        self.bounce = Settings.BOUNCE
        self.fixed_power = Settings.FIXED_POWER
        self.invisible = Settings.INVISIBLE
        self.random = Settings.RANDOM
        self.max_planets = Settings.MAX_PLANETS
        self.timeout = Settings.MAX_FLIGHT
        self.max_rounds = Settings.MAX_ROUNDS

    def save_settings(self):
        pass  # disabled for web compatibility


# ======================================================================
# Entry point — async for pygbag (web) and normal desktop use
# ======================================================================

async def main():                               # ← CHANGED: now async
    path = os.path.expanduser("~") + "/.slingshot"
    os.makedirs(path, exist_ok=True)

    game = Game()

    while not game.q:                           # ← CHANGED: loop moved here
        game.clock.tick(Settings.FPS)

        for event in pygame.event.get():
            if event.type == QUIT:
                game.q = True
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    game.toggle_menu()

                if game.menu is None:
                    mod = event.mod
                    if mod in (4160, 64, 4224):
                        p = Settings.POWER_STEP_SMALL
                        a = Settings.ANGLE_STEP_SMALL
                    elif mod in (4097, 1, 4098):
                        p = Settings.POWER_STEP_LARGE
                        a = Settings.ANGLE_STEP_LARGE
                    elif mod in (4352, 20480, 4608):
                        p = 0.2
                        a = 0.05
                    else:
                        p = Settings.POWER_STEP_NORMAL
                        a = Settings.ANGLE_STEP_NORMAL

                    if not game.round_over:
                        if event.key == K_UP:
                            game.change_power(p)
                        elif event.key == K_DOWN:
                            game.change_power(-p)
                        elif event.key == K_LEFT:
                            game.change_angle(-a)
                        elif event.key == K_RIGHT:
                            game.change_angle(a)
                    if event.key in (13, 32):
                        if game.round_over:
                            if game.round == Settings.MAX_ROUNDS:
                                game.set_menu(game.welcome_menu)
                            game.round_init()
                            game.started = False
                        else:
                            game.fire()
                else:
                    if event.key == K_UP:
                        game.menu.up()
                    elif event.key == K_DOWN:
                        game.menu.down()
                    elif event.key == K_LEFT:
                        game.menu.left()
                    elif event.key == K_RIGHT:
                        game.menu.right()
                    elif event.key in (13, 32):
                        game.menu.select()

        game.update()
        game.draw()

        await asyncio.sleep(0)                  # ← KEY LINE: yields to browser each frame


asyncio.run(main())                             # ← CHANGED: works for both desktop and pygbag
