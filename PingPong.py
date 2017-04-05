## Forked from https://github.com/smoross/Pygame b
## a game from Samantha Moross


import pygame
import sys, os, time
import random
import json

from pygame.locals import Rect, DOUBLEBUF, QUIT, K_ESCAPE, KEYDOWN, K_DOWN, \
    K_LEFT, K_UP, K_RIGHT, KEYUP, K_LCTRL, K_RETURN, FULLSCREEN

from socket import *
from _thread import *


#Initialize the game
pygame.init()
screensize = (640, 480)
screen = pygame.display.set_mode(screensize)
FPS = 200

PLAYER_LIST = []

#Define colors
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 100, 00)
red = (255, 0, 0)

class Pong(object):
    def __init__(self, screensize):
        self.screensize = screensize

        #place ball in the center
        self.centerx = int(screensize[0]*0.5) 
        self.centery = int(screensize[1]*0.5)

        self.radius = 8

        #create shape and sizes it
        self.rect = pygame.Rect(self.centerx-self.radius, 
                self.centery-self.radius, 
                self.radius*2, self.radius*2) 

        self.color = white
        self.direction = [1,1] #current direction to the right and up
        #list so we can access each individual part because it will change

        self.speedx = 2
        self.speedy = 5

        self.hit_left_edge = False
        self.hit_right_edge = False

        self.ai_score = 0
        self.player_score = 0

        self.player_paddle_win = False
        self.ai_paddle_win = False              

    def update(self):
        global PLAYER_LIST
        self.centerx += self.direction[0]*self.speedx
        self.centery += self.direction[1]*self.speedy

        self.rect.center = (self.centerx, self.centery)

        sound = pygame.mixer.Sound(os.path.join('data/ping.wav'))

        #makes sure if ball hits top it comes back down
        if self.rect.top <= 0: 
                self.direction[1] = 1
        elif self.rect.bottom >= self.screensize[1]-1:
                self.direction[1] = -1 #bounce up and down
        elif self.rect.right >= self.screensize[0]-1: 
                self.direction[0] = -1
        elif self.rect.left <= 0:
                self.direction[0] = 1

        #checks if the code above is true
        if self.rect.right >=self.screensize[0]-1: #if it's greater than width -1
                self.hit_right_edge = True
        elif self.rect.left <= 0:
                self.hit_left_edge = True
        if self.rect.top <= 0: 
                self.hit_right_edge = True
        elif self.rect.bottom >= self.screensize[1]-1:
                self.hit_left_edge = True

        #check for a collision between the rectangles
        for player in PLAYER_LIST:
            if player.side == 1:
                if self.rect.colliderect(player.rect):
                        self.direction[0] = -1
                        self.player_score += 1
                        sound.play()
                        self.speedx += 1 #speed increases when pong ball collides
                        if self.player_score == 10: #win if you score 15 points
                                self.player_paddle_win = True   
            else:
                if self.rect.colliderect(player.rect):
                        self.direction[0] = 1
                        self.ai_score += 1
                        sound.play()
                        if self.ai_score == 10: #lose if the computer scores 15 points
                                self.ai_paddle_win = True

    def render(self, screen):
        pygame.draw.circle(screen, self.color, self.rect.center, self.radius, 0)
        #creates black outline of the circle
        pygame.draw.circle(screen, black, self.rect.center, self.radius, 1)


class PlayerPaddle(object):
        #TODO: Add logic for different x positions of player paddles based on client number

    def __init__(self, screensize, player):
        self.screensize = screensize

        if player % 2 == 0:
            self.centery = int(screensize[1]*0.5)
            self.centerx = screensize[0]-5
        else:
            self.centery = int(screensize[1]*0.5)
            self.centerx = 5
        self.height = 100
        self.width = 10
        self.id = player

        #Pygame box that paddle is drawn and refreshed on 
        self.rect = pygame.Rect(0, self.centery-int(self.height*0.5), self.width, self.height)

        self.color = white
        self.side = player % 2

        # Speed and direction
        self.speed = 3
        self.direction = 0
                
    def update(self):
        self.centery += self.direction*self.speed
        self.rect.center = (self.centerx, self.centery)

        #make sure paddle does not go off screen
        if self.rect.top < 0:
                self.rect.top = 0
        if self.rect.bottom > self.screensize[1]-1:
                self.rect.bottom = self.screensize[1]-1 

    def render(self,screen):
        pygame.draw.rect(screen, self.color, self.rect, 0)
        pygame.draw.rect(screen, black, self.rect, 1)


# connecting to server logic
def handle_server(server):
    #TODO: Handle connection errors
    global PLAYER_LIST
    print ("Connected to server")

    while True:
        res = server.recv(1024).decode().split(";")
        data = b'ack\r\n'

        if res[0] == "newPlayer":
            server.send(data)
            detail = json.loads(res[1])
            player = PlayerPaddle(screensize, detail["id"])
            PLAYER_LIST.append(player)
        if res[0] == "currentList":
            server.send(data)
            p_list = json.loads(res[1])
            update_players(p_list)


    server.close()

def update_players(p_list):
    global PLAYER_LIST

    for i in range(len(p_list)):
        for player in PLAYER_LIST:
            if p_list[i]["id"] != player.id:
                PLAYER_LIST.append(PlayerPaddle(screensize, p_list[i]["id"]))

def main():
    global PLAYER_LIST
    #TODO: get host and port from a config file and possibly from settings
    server = socket(AF_INET, SOCK_STREAM)
    server.connect(('', 2115))
    start_new_thread(handle_server ,(server,))
    running = True

    clock = pygame.time.Clock()

    pong = Pong(screensize)

    player_paddle1 = PlayerPaddle(screensize, 1)
    PLAYER_LIST.append(player_paddle1)


    pygame.display.set_caption('Pong')

    pygame.mixer.music.load(os.path.join('data/ping.wav'))
    pygame.mixer.music.load(os.path.join('data/win.wav'))
    pygame.mixer.music.load(os.path.join('data/lose.wav'))

    win = pygame.mixer.Sound(os.path.join('data/win.wav'))
    lose = pygame.mixer.Sound(os.path.join('data/lose.wav'))        

    while running: #Main game loop  
        if len(PLAYER_LIST) <= 1:
            continue
        else:
            for event in pygame.event.get(): #handles events
                if event.type == pygame.QUIT: #Makes sure we can quit the game
                        pygame.quit()
                        exit()

                if event.type == KEYDOWN:
                        if event.key == K_UP:
                                player_paddle1.direction = -1
                        elif event.key == K_DOWN:
                                player_paddle1.direction = 1

                if event.type == KEYUP: 
                        if event.key == K_UP and player_paddle1.direction == -1:
                                player_paddle1.direction = 0 

                        elif event.key == K_DOWN and player_paddle1.direction == 1:
                                player_paddle1.direction = 0

            # if pong.player_paddle_win == True:
            #         running = False
            # elif pong.ai_paddle_win == True:
            #             running = False

            for player in PLAYER_LIST:
                player.update()

            pong.update()                             

            screen.fill(green)
            #draw vertical line for ping pong design
            pygame.draw.line(screen, white, (320, 0), (320, 480), 5)         

            for player in PLAYER_LIST:
                player.render(screen)

            pong.render(screen) #calls render function to the screen

            default_font = pygame.font.get_default_font()
            font = pygame.font.Font(default_font, 50)
            msg = font.render("   "+str(pong.ai_score)+"  Score  "+str(pong.player_score), True, white)
            screen.blit(msg, (320, 0)) #adds score to the screen

            clock.tick(FPS)
            pygame.display.flip() #renders everything based on the update

    if pong.player_paddle_win == True:
            txt = font.render(" You Won!!!!", True, white)
            screen.blit(txt, (100, 200))
            win.play()
    elif pong.ai_paddle_win == True:
            txt2 = font.render("Sorry, try again!", True, white)
            screen.blit(txt2, (100, 200))
            lose.play()

    pygame.display.flip() 
    pygame.time.delay(5000)
    pygame.quit()

if __name__=='__main__':
        main()
