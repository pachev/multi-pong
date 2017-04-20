import pygame

from data import constants as const


class Pong(object):
    def __init__(self, screensize, id, x, y, lscore, rscore):
        self.screensize = screensize
        self.id = id
        self.centerx = x
        self.centery = y
        self.lscore = lscore
        self.rscore = rscore
        self.radius = 8

        # create shape and sizes it
        self.rect = pygame.Rect(self.centerx-self.radius,
                                self.centery-self.radius,
                                self.radius*2, self.radius*2)
        self.color = const.WHITE

    def update(self, x, y, lscore, rscore):
        self.centerx = x
        self.centery = y
        self.lscore = lscore
        self.rscore = rscore
        self.rect.center = (self.centerx, self.centery)

    def render(self, screen):
        pygame.draw.circle(screen, self.color, self.rect.center, self.radius, 0)
        # creates black outline of the circle
        pygame.draw.circle(screen, const.BLACK, self.rect.center, self.radius, 1)
