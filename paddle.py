import pygame
import json

HOST = ''
GAME_PORT = 2115

# Define colors
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 100, 00)
red = (255, 0, 0)


class PlayerPaddle(object):
        # TODO: Add logic for different x positions of player paddles based on client number

    def __init__(self, screensize, player, color=white):

        self.screensize = screensize
        self.centery = int(screensize[1]*0.5)

        if player % 2 == 0:
            self.centerx = screensize[0] - (5 + (player * 30))
        else:
            self.centerx = (player * 30) + 5 if player > 1 else 5

        self.height = 100
        self.width = 10

        self.id = player

        # Pygame box that paddle is drawn and refreshed on
        self.rect = pygame.Rect(0, self.centery-int(self.height*0.5), self.width, self.height)

        self.color = color
        self.side = player % 2

        # Speed and direction
        self.speed = 3
        self.direction = 0

    def update_local(self, y_new):
        self.centery = y_new
        self.rect.center = (self.centerx, self.centery)

        #make sure paddle does not go off screen
        if self.rect.top < 0:
                self.rect.top = 0
        if self.rect.bottom > self.screensize[1]-1:
                self.rect.bottom = self.screensize[1]-1 

    def getId(self):
        return self.id
                
    def update(self,server):
        global HOST
        global GAME_PORT
        self.centery += self.direction*self.speed
        self.rect.center = (self.centerx, self.centery)

        # make sure paddle does not go off screen
        if self.rect.top < 0:
                self.rect.top = 0
        if self.rect.bottom > self.screensize[1]-1:
                self.rect.bottom = self.screensize[1]-1 

        info = {"x": self.centerx, "y": self.centery, "id": self.id}
        data = "updateLocation;" +json.dumps(info) + "\r\n"

        server.sendto(data.encode(), (HOST, GAME_PORT))

    def render(self,screen):
        pygame.draw.rect(screen, self.color, self.rect, 0)
        pygame.draw.rect(screen, black, self.rect, 1)
