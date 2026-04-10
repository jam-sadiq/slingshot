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

from settings import *
from general import *


class Player(pygame.sprite.Sprite):

    def __init__(self, n):
        pygame.sprite.Sprite.__init__(self)
        self.player = n
        self.init()
        self.score = 0

    def init(self):
        self.power = Settings.INITIAL_POWER
        self.shot = False
        self.attempts = 0
        self.e = 0
        self.exp, self.rect = load_image("data/explosion.png", (0, 0, 0))

        if self.player == 1:
            self.angle = 90
            self.orig, self.rect = load_image("data/red_ship.png", (0, 0, 0))
            self.rect = pygame.Rect(0, 0, 40, 33)
            self.rect.midleft = (30, randint(100, 500))
            self.color = Settings.PLAYER_1_COLOR
        elif self.player == 2:
            self.angle = 270
            self.orig, self.rect = load_image("data/blue_ship.png", (0, 0, 0))
            self.rect = pygame.Rect(0, 0, 40, 33)
            self.rect.midright = (770, randint(100, 500))
            self.color = Settings.PLAYER_2_COLOR
        else:
            self.orig = None

        self.rel_rot = 0.01
        if self.player == 1:
            self.d = self.rect.right - self.rect.centerx + 2
        else:
            self.d = self.rect.centerx - self.rect.left + 3

        if self.orig is not None:
            self.image = self.orig.subsurface(0, 0, 40, 33)

        if Settings.FIXED_POWER:
            self.power = Settings.POWER

    def reset_score(self):
        self.score = 0

    def add_score(self, score):
        self.score += score

    def get_color(self):
        return self.color

    def change_angle(self, a):
        self.angle += a
        self.rel_rot += a
        for attr in ("angle", "rel_rot"):
            v = getattr(self, attr)
            if v >= 360:
                setattr(self, attr, v - 360)
            elif v < 0:
                setattr(self, attr, v + 360)

        center = self.rect.center

        img1 = int(round((self.rel_rot + 22.5) / 45 - 0.49)) % 8
        img2 = int(round(self.rel_rot / 45 - 0.49)) % 8
        if img1 == img2 or img1 == -img2:
            img2 = (img2 + 1) % 8
            f = (self.rel_rot - img1 * 45.0) / 45.0
        else:
            f = ((img2 + 1) * 45.0 - self.rel_rot) / 45.0

        rect1 = pygame.Rect(img1 * 40, 0, 40, 33)
        rect2 = pygame.Rect(img2 * 40, 0, 40, 33)
        image1 = self.orig.subsurface(rect1).convert_alpha()
        image2 = self.orig.subsurface(rect2).convert_alpha()

        tmp = pygame.Surface((40, 33)).convert_alpha()
        tmp.blit(image2, (0, 0))
        tmp = tmp.convert()
        tmp.set_alpha(int(round(255.0 * f)))
        tmp.set_colorkey((0, 0, 0))
        tmp = tmp.convert_alpha()

        image1.blit(tmp, (0, 0))
        self.image = pygame.transform.rotozoom(image1, -self.rel_rot, 1.0)
        self.rect = self.image.get_rect()
        self.rect.center = center

    def change_power(self, p):
        if not Settings.FIXED_POWER:
            self.power = max(0, min(self.power + p, Settings.MAXPOWER))

    def get_angle(self):
        return self.angle

    def get_power(self):
        return self.power

    def get_launchpoint(self):
        if Settings.ROTATE:
            return (
                self.rect.center[0] + self.d * math.sin(math.radians(self.angle)),
                self.rect.center[1] - self.d * math.cos(math.radians(self.angle)),
            )
        else:
            if self.player == 1:
                return (self.rect.midright[0] + 1, self.rect.midright[1])
            if self.player == 2:
                return (self.rect.midleft[0] - 1, self.rect.midleft[1])

    def draw_info(self, screen):
        txt = Settings.font.render(
            "Angle: %3.2f" % self.angle, 1, Settings.TEXT_STATUS_COLOR)
        rect = txt.get_rect()
        rect.topleft = (240, 5)
        screen.blit(txt, rect.topleft)

        txt = Settings.font.render(
            "Power: %3.1f" % self.power, 1, Settings.TEXT_STATUS_COLOR)
        rect = txt.get_rect()
        rect.topleft = (350, 5)
        screen.blit(txt, rect.topleft)

        txt = Settings.font.render(
            "Shots: %d of %d" % (self.attempts, Settings.MAX_SHOTS),
            1, Settings.TEXT_STATUS_COLOR)
        rect = txt.get_rect()
        rect.topleft = (460, 5)
        screen.blit(txt, rect.topleft)

    def draw_status(self, screen):
        if self.player == 1:
            txt = Settings.font.render(
                "Player 1  --  %d" % self.score, 1, self.color)
            rect = txt.get_rect()
            rect.topleft = (5, 5)
        else:
            txt = Settings.font.render(
                "%d  --  Player 2" % self.score, 1, self.color)
            rect = txt.get_rect()
            rect.topright = (794, 5)
        screen.blit(txt, rect.topleft)

    def update_explosion(self):
        self.e += 0.2
        s = self.e * (10 - self.e) * 100 / 9
        if s >= 0:
            self.image = pygame.transform.scale(
                self.exp, (int(s), int(s)))
            pos = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = pos

    def draw_line(self, screen, transform):
        sx, sy = self.get_launchpoint()
        p1 = transform((sx, sy))
        p2 = transform((
            sx + self.power * math.sin(math.radians(self.angle)),
            sy - self.power * math.cos(math.radians(self.angle)),
        ))
        if Settings.AIM_WIDTH == 1:
            pygame.draw.aaline(screen, Settings.AIM_COLOR, p1, p2)
        else:
            pygame.draw.line(screen, Settings.AIM_COLOR, p1, p2,
                             Settings.AIM_WIDTH)

    def draw(self, screen):
        """
        Renders the ship sprite with alpha-blended frame interpolation.
        NOTE: This method is unused in the main loop (draw_zoom / draw_sprite
        are used instead), but is kept for reference.
        """
        center = self.rect.center

        img1 = int(round((self.rel_rot + 22.5) / 45 - 0.4999)) % 8
        img2 = int(round(self.rel_rot / 45 - 0.4999)) % 8
        if img1 == img2:
            img2 = (img2 + 1) % 8
            f = (self.rel_rot - img1 * 45.0) / 45.0
        else:
            f = ((img2 + 1) * 45.0 - self.rel_rot) / 45.0

        rect1 = pygame.Rect(img1 * 40, 0, 40, 33)
        rect2 = pygame.Rect(img2 * 40, 0, 40, 33)
        image1 = self.orig.subsurface(rect1).convert_alpha()
        image2 = self.orig.subsurface(rect2).convert_alpha()

        tmp = pygame.Surface((40, 33)).convert_alpha()
        tmp.blit(image1, (0, 0))
        tmp = tmp.convert()
        tmp.set_alpha(int(round(255.0 * (1.0 - f))))
        tmp.set_colorkey((0, 0, 0))
        tmp = tmp.convert_alpha()

        image2.blit(tmp, (0, 0))
        self.image = pygame.transform.rotate(image2, self.rel_rot)
        self.rect = self.image.get_rect(center=center)  # FIX: was `image.get_rect` (NameError)

    def hit(self, pos):
        if not self.rect.collidepoint(pos):
            return False
        x = int(round(pos[0] - self.rect.topleft[0]))
        y = int(round(pos[1] - self.rect.topleft[1]))
        if x <= 1 or y <= 1:
            return False
        x -= 1
        y -= 1
        if self.image.get_at((x, y)) != (0, 0, 0, 0):
            self.shot = True
            return True
        return False


class Dummy(Player):
    """A no-op placeholder player used when no human is controlling a slot."""

    def __init__(self):
        Player.__init__(self, 0)

    def draw_line(self, screen, transform):
        pass

    def change_angle(self, a):
        pass

    def change_power(self, p):
        pass

    def draw_info(self, screen):
        pass
