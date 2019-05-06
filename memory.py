#
# Python 3 + PyGame: Memory (PyDays 2019 Beginner Workshop)
# =========================================================
# Copyright 2019 Thomas Perl (m@thp.io)
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
#

import pygame
from pygame.locals import *

import math, random, time, os, glob

pygame.font.init()
pygame.mixer.init(buffer=128)

font = pygame.font.SysFont('Consolas', 30)
screen = pygame.display.set_mode((640, 480))
cheat_mode = False

class Sounds(object):
    # you are not expected to understand this
    for filename in glob.glob(os.path.join(os.path.dirname(__file__), '*.wav')):
        sound_id, _ = os.path.splitext(os.path.basename(filename))
        locals()[sound_id] = pygame.mixer.Sound(filename)

def modify_color(color, factor=0.5):
    return tuple(max(0, min(int(x*factor), 255)) for x in color)

class Position(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Size(object):
    def __init__(self, w, h):
        self.w = w
        self.h = h

    def contains(self, x, y):
        return x >= 0 and x < self.w and y >= 0 and y < self.h

class Rectangle(Size):
    SHADOW_OFFSET = 3

    def __init__(self, x, y, w, h):
        super().__init__(w, h)
        self.pos = Position(x, y)
        self.color = (0, 0, 255)
        self.hovering = False

    def draw(self, surface):
        for y in range(0, self.h, 2):
            pygame.draw.rect(surface, modify_color(self.color, 0.5), (self.pos.x+self.SHADOW_OFFSET, self.pos.y+self.SHADOW_OFFSET+y, self.w, 1))
        pygame.draw.rect(surface, self.color, (self.pos.x, self.pos.y, self.w, self.h))
        pygame.draw.rect(surface, modify_color(self.color, 1.2), (self.pos.x, self.pos.y, self.w, self.h), 1)

    def contains(self, x, y):
        return super().contains(x - self.pos.x, y - self.pos.y)

    def click(self, x, y):
        if self.contains(x, y):
            self.on_click()

    def hover(self, x, y):
        self.hovering = self.contains(x, y)

    def on_click(self):
        ...

class RectangleWithText(Rectangle):
    def __init__(self, x, y, w, h, text):
        super().__init__(x, y, w, h)
        self.text = text

    def draw(self, surface):
        super().draw(surface)
        text_surface = font.render(self.text, True, modify_color(self.color, 0.7))
        xoff = (self.w - text_surface.get_width()) / 2
        yoff = (self.h - text_surface.get_height()) / 2
        surface.blit(text_surface, (self.pos.x + xoff, self.pos.y + yoff))

class Card(RectangleWithText):
    SPACING = 10
    BORDER = SPACING * 1.5
    CARD_HEIGHT = 75
    CARD_WIDTH = CARD_HEIGHT * 1.5

    def __init__(self, x, y):
        ypos = self.BORDER + y * (self.SPACING + self.CARD_HEIGHT)
        xpos = self.BORDER + x * (self.SPACING + self.CARD_WIDTH)
        self.value = 0
        self.opened = False
        self.obtained = False
        self.failed = 0
        super().__init__(xpos, ypos, self.CARD_WIDTH, self.CARD_HEIGHT, '')

    def draw(self, surface):
        if self.failed > 0 and time.time() - self.failed > 1:
            self.failed = 0

        if self.opened or self.obtained or self.failed > 0 or cheat_mode:
            self.text = f'{self.value}'
        else:
            self.text = '???'

        if self.obtained:
            self.color = (127, 255, 127)
        elif self.failed > 0:
            self.color = (255, 127, 127)
        elif self.opened:
            self.color = (127, 127, 255)
        elif self.hovering:
            self.color = modify_color((0, 255, 255), 0.8+0.2*math.sin(time.time()*9))
        else:
            self.color = (0, 0, 255 - 50 * abs(math.sin(time.time())))

        super().draw(surface)

    def on_click(self):
        print(f'card {self.value} clicked')
        if self.failed == 0 and not self.obtained:
            self.opened = not self.opened

    def obtain(self):
        self.obtained = True
        self.opened = False

    def fail(self):
        self.failed = time.time()
        self.opened = False

names = 'monty python holy grail life brian meaning pydays19'.split() * 2
random.shuffle(names)

cards = [Card(x, y) for y in range(4) for x in range(4)]

for card, name in zip(cards, names):
    card.value = name

class FixedTimestep(object):
    def __init__(self, rate):
        self.last = time.time()
        self.rate = rate
        self.step = 1. / rate
        self.accumulator = 0

    def update(self, func):
        now = time.time()
        self.accumulator += (now - self.last)
        while self.accumulator > self.step:
            if not func():
                return False
            self.accumulator -= self.step
        self.last = now
        return True



finished = False
timestep = None

while True:
    event = pygame.event.poll()
    if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
        break
    elif event.type in (KEYDOWN, KEYUP) and event.key == K_c:
        cheat_mode = (event.type == KEYDOWN)
    elif event.type == KEYDOWN and event.key == K_w:
        for card in cards:
            card.obtained = True
    elif event.type == MOUSEBUTTONDOWN:
        for card in cards:
            card.click(*event.pos)
    elif event.type == MOUSEMOTION:
        for card in cards:
            card.hover(*event.pos)

    if not finished:
        screen.fill((0, 0, 0))
        for card in cards:
            card.draw(screen)

    opened_cards = [card for card in cards if card.opened]
    if len(opened_cards) == 2:
        if opened_cards[0].value == opened_cards[1].value:
            for card in opened_cards:
                card.obtain()
            Sounds.success.play()
        else:
            for card in opened_cards:
                card.fail()
            Sounds.failure.play()

    pygame.display.set_caption(f'{len(cards)} cards, {sum(card.obtained for card in cards)} obtained')

    # Solitaire-Style Finale
    if all(card.obtained for card in cards):
        if not finished:
            for card in cards:
                card.velocity = Position(0.3, 3)
                card.color = (random.randint(40, 255), random.randint(40, 255), random.randint(40, 255))
                RectangleWithText.draw(card, screen)
            # Sort cards again so that we go from bottom-to-top and right-to-left
            cards = sorted(cards, key=lambda card: (card.pos.y, card.pos.x), reverse=True)
            finished = True
            timestep = FixedTimestep(300)

        def update_once():
            for card in cards:
                if card.pos.x > screen.get_width():
                    continue

                card.text = ':)'
                card.pos.y += card.velocity.y
                card.pos.x += card.velocity.x
                card.velocity.y += 0.05  # gravity
                if card.pos.y >= screen.get_height() - card.h:
                    card.velocity.y *= -0.85  # bounce
                    card.pos.y = screen.get_height() - card.h
                    Sounds.bounce.set_volume(min(1., abs(card.velocity.y)/5))
                    Sounds.bounce.play()
                RectangleWithText.draw(card, screen)
                return True

            return False

        if not timestep.update(update_once):
            break

    pygame.display.flip()
