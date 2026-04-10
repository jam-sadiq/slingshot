# This file is part of Slingshot.
#
# Slingshot is a two-dimensional strategy game where two players attempt to shoot one
# another through a section of space populated by planets. The main feature of the
# game is that the shots, once fired, are affected by the gravity of the planets.
#
# Slingshot is Copyright 2007 Jonathan Musther and Bart Mak.
# Released under the GNU General Public License version 2, or later if applicable.

from settings import *
from general import *
import pygame
import math
from math import sqrt
from random import randint


class Particle(pygame.sprite.Sprite):

    def __init__(self, pos=(0.0, 0.0), size=10):
        pygame.sprite.Sprite.__init__(self)
        if size == 5:
            self.image = Settings.particle_image5
        else:
            self.image = Settings.particle_image10
        self.rect = self.image.get_rect()
        self.pos = pos
        self.impact_pos = pos
        self.size = size
        angle = randint(0, 359)
        if size == 5:
            speed = randint(Settings.PARTICLE_5_MINSPEED, Settings.PARTICLE_5_MAXSPEED)
        else:
            speed = randint(Settings.PARTICLE_10_MINSPEED, Settings.PARTICLE_10_MAXSPEED)
        self.v = (
            0.1 * speed * math.sin(angle),
            -0.1 * speed * math.cos(angle),
        )
        self.flight = Settings.MAX_FLIGHT

    def max_flight(self):
        return self.flight < 0

    def update(self, planets, timestep=1.0):
        self.flight -= timestep
        self.last_pos = self.pos

        for p in planets:
            p_pos = p.get_pos()
            mass = p.get_mass()
            d = (self.pos[0] - p_pos[0]) ** 2 + (self.pos[1] - p_pos[1]) ** 2
            d_sqrt = math.sqrt(d)
            a = (
                Settings.g * mass * (self.pos[0] - p_pos[0]) / (d * d_sqrt),
                Settings.g * mass * (self.pos[1] - p_pos[1]) / (d * d_sqrt),
            )
            self.v = (
                self.v[0] - a[0] * timestep,
                self.v[1] - a[1] * timestep,
            )

        self.pos = (
            self.pos[0] + self.v[0] * timestep,
            self.pos[1] + self.v[1] * timestep,
        )

        if not self.in_range():
            return 0

        for p in planets:
            p_pos = p.get_pos()
            r = p.get_radius()
            d = (self.pos[0] - p_pos[0]) ** 2 + (self.pos[1] - p_pos[1]) ** 2
            if d <= r ** 2:
                self.impact_pos = get_intersect(p_pos, r, self.last_pos, self.pos)
                self.pos = self.impact_pos
                return 0

        if Settings.BOUNCE:
            if self.pos[0] > 799:
                d = self.pos[0] - self.last_pos[0]
                self.pos = (
                    799,
                    self.last_pos[1]
                    + (self.pos[1] - self.last_pos[1]) * (799 - self.last_pos[0]) / d,
                )
                self.v = (-self.v[0], self.v[1])
            if self.pos[0] < 0:
                d = self.last_pos[0] - self.pos[0]
                self.pos = (
                    0,
                    self.last_pos[1]
                    + (self.pos[1] - self.last_pos[1]) * self.last_pos[0] / d,
                )
                self.v = (-self.v[0], self.v[1])
            if self.pos[1] > 599:
                d = self.pos[1] - self.last_pos[1]
                self.pos = (
                    self.last_pos[0]
                    + (self.pos[0] - self.last_pos[0]) * (599 - self.last_pos[1]) / d,
                    599,
                )
                self.v = (self.v[0], -self.v[1])
            if self.pos[1] < 0:
                d = self.last_pos[1] - self.pos[1]
                self.pos = (
                    self.last_pos[0]
                    + (self.pos[0] - self.last_pos[0]) * self.last_pos[1] / d,
                    0,
                )
                self.v = (self.v[0], -self.v[1])

        self.rect.center = (round(self.pos[0]), round(self.pos[1]))
        return 1

    def in_range(self):
        return pygame.Rect(-800, -600, 2400, 1800).collidepoint(self.pos)

    def visible(self):
        return pygame.Rect(0, 0, 800, 600).collidepoint(self.pos)

    def get_pos(self):
        return self.pos

    def get_impact_pos(self):
        return self.impact_pos

    def get_size(self):
        return self.size


class Missile(Particle):

    def __init__(self):
        Particle.__init__(self)
        self.image, self.rect = load_image("data/shot.png", (0, 0, 0))
        self.rect = self.image.get_rect()

    def reset(self):                                 # FIX: was indented with tab (IndentationError)
        self.trail = []
        self.last_pos = (0.0, 0.0)
        self.flight = 0

    def launch(self, player):
        self.flight = Settings.MAX_FLIGHT
        self.pos = player.get_launchpoint()
        speed = player.get_power()
        angle = math.radians(player.get_angle())
        self.v = (
            0.1 * speed * math.sin(angle),
            -0.1 * speed * math.cos(angle),
        )
        self.trail_color = player.get_color()
        self.trail = [self.pos]
        self.score = -Settings.PENALTY_FACTOR * speed

    def update_players(self, players):
        result = 1
        for i in range(10):
            pos = (
                self.last_pos[0] + i * 0.1 * self.v[0],
                self.last_pos[1] + i * 0.1 * self.v[1],
            )
            if players[1].hit(pos):
                result = 0
            if players[2].hit(pos):
                result = 0
            if result == 0:
                self.impact_pos = pos
                self.pos = pos
                break
        return result

    def draw_status(self, screen):
        if self.flight >= 0:
            txt = Settings.font.render(
                "Timeout in %d" % self.flight, 1, Settings.TEXT_STATUS_COLOR)
        else:
            txt = Settings.font.render(
                "Shot timed out...", 1, Settings.TEXT_STATUS_COLOR)
        rect = txt.get_rect()
        rect.midbottom = (399, 594)
        screen.blit(txt, rect.topleft)

    def update(self, planets, players):
        # Simulate one frame using multiple sub-steps for accuracy
        timestep = 1.0 / Settings.SUPERSAMPLING
        result = 1
        for _ in range(Settings.SUPERSAMPLING):
            result *= Particle.update(self, planets, timestep)
            result *= self.update_players(players)
            self.trail.append(self.pos)
            if result == 0:
                break
        return result

    def get_image(self):
        return self.image

    def get_score(self):
        return self.score
