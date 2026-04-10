# This file is part of Slingshot.
#
# Slingshot is a two-dimensional strategy game where two players attempt to shoot one
# another through a section of space populated by planets. The main feature of the
# game is that the shots, once fired, are affected by the gravity of the planets.
#
# Slingshot is Copyright 2007 Jonathan Musther and Bart Mak.
# Released under the GNU General Public License version 2, or later if applicable.

import pygame
import math
from random import randint
from math import sqrt

from settings import *
from general import *


class Planet(pygame.sprite.Sprite):

    def __init__(self, planets, background):
        pygame.sprite.Sprite.__init__(self)

        # Pick a planet type, ensuring uniqueness if UNIQUE_PLANETS is set
        unique = False
        while not unique:
            unique = True
            self.n = randint(1, Settings.NUM_PLANET_TYPES)
            if Settings.UNIQUE_PLANETS:
                for p in planets:
                    if self.n == p.get_n():
                        unique = False

        filename = "data/planet_%d.png" % self.n
        self.orig, self.rect = load_image(filename, (0, 0, 0))
        self.image = self.orig

        # Place the planet so it doesn't overlap ships or other planets
        positioned = False
        while not positioned:
            self.mass = randint(8, 512)
            self.r = self.mass ** (1.0 / 3.0) * Settings.PLANET_RADIUS_SCALE
            self.pos = (
                randint(
                    Settings.PLANET_SHIP_DISTANCE + round(self.r),
                    800 - Settings.PLANET_SHIP_DISTANCE - int(round(self.r)),
                ),
                randint(
                    Settings.PLANET_EDGE_DISTANCE + int(round(self.r)),
                    600 - Settings.PLANET_EDGE_DISTANCE - int(round(self.r)),
                ),
            )
            positioned = True
            for p in planets:
                d = math.sqrt(
                    (self.pos[0] - p.get_pos()[0]) ** 2
                    + (self.pos[1] - p.get_pos()[1]) ** 2
                )
                if d < (self.r + p.get_radius()) * 1.5 + 0.1 * (
                    self.mass + p.get_mass()
                ):
                    positioned = False

        s = int(round(2 * self.r / 0.96))
        self.orig = pygame.transform.scale(self.image, (s, s))
        self.image = self.orig

        self.rect = self.orig.get_rect()
        self.rect.center = self.pos

        # Pre-bake a "fade" surface showing the planet composited onto background
        tmp = pygame.Surface(background.get_size())
        tmp.blit(background, (0, 0))
        rect = tmp.blit(self.orig, self.rect.topleft)
        self.fade_image = pygame.Surface(self.orig.get_size())
        self.fade_image.blit(tmp, (0, 0), rect)
        self.fade_image.set_alpha(255)
        self.fade_image.convert()

    def get_n(self):
        return self.n

    def get_radius(self):
        return self.r

    def get_mass(self):
        return self.mass

    def get_pos(self):
        return self.pos

    def fade(self, f):
        """Set planet alpha so it fades out as f increases from 0 to 100."""
        self.image = self.fade_image
        self.image.set_alpha(255 - int(round(f * 2.55)))
