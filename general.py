# This file is part of Slingshot.
#
# Slingshot is a two-dimensional strategy game where two players attempt to shoot one
# another through a section of space populated by planets. The main feature of the
# game is that the shots, once fired, are affected by the gravity of the planets.
#
# Slingshot is Copyright 2007 Jonathan Musther and Bart Mak.
# Released under the GNU General Public License version 2, or later if applicable.

import pygame
from pygame.locals import *
from math import sqrt


def load_image(name, colorkey=None):
    fullname = name
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:          # FIX: Python 3 exception syntax
        print("Cannot load image:", fullname)
        raise SystemExit(message)            # FIX: Python 3 raise syntax
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey == -1:                   # FIX: `is -1` is invalid in Python 3.8+
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()


def get_intersect(center, r, pos1, pos2):
    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]
    px = pos1[0]
    py = pos1[1]
    cx = center[0]
    cy = center[1]
    a = dx**2 + dy**2
    b = 2 * (dx * px - dx * cx + dy * py - dy * cy)
    c = (-2 * cx * px - 2 * cy * py + px**2 + py**2
         + cx**2 + cy**2 - r**2)
    D = b**2 - 4 * a * c
    if D < 0:
        return (4000.0, 3000.0)
    alpha = (-b + sqrt(D)) / (2 * a)
    if alpha > 1:
        alpha = (-b - sqrt(D)) / (2 * a)
    alpha = alpha - 0.05
    pos = (px + alpha * dx, py + alpha * dy)
    return pos
