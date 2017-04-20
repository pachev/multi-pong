from pygame.locals import Rect

# Define colors
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 100, 00)
red = (255, 0, 0)

class Pong(object):
    def __init__(self, screensize, id):
        self.screensize = screensize
        self.id = id

        # place ball in the center
        self.centerx = int(screensize[0]*0.5) 
        self.centery = int(screensize[1]*0.5)

        self.radius = 17

        # create shape and sizes it
        self.rect = Rect(self.centerx-self.radius, 
                                self.centery-self.radius,
                                self.radius*2, self.radius*2)
        self.color = white
        self.direction = [1, 1] # current direction to the right and up
        # list so we can access each individual part because it will change

        self.speedx = 1
        self.speedy = 2

        self.hit_left_edge = False
        self.hit_right_edge = False

        self.ai_score = 0
        self.player_score = 0

        self.player_paddle_win = False
        self.ai_paddle_win = False              

    def update(self, player_list):
        self.centerx += self.direction[0]*self.speedx
        self.centery += self.direction[1]*self.speedy
        self.rect.center = (self.centerx, self.centery)
        # makes sure if ball hits top it comes back down
        if self.rect.top <= 0: 
                self.direction[1] = 1
        elif self.rect.bottom >= self.screensize[1]-1:
                self.direction[1] = -1 # bounce up and down
        elif self.rect.right >= self.screensize[0]-1: 
                self.direction[0] = -1
        elif self.rect.left <= 0:
                self.direction[0] = 1

        # checks if the code above is true
        if self.rect.right >=self.screensize[0]-1: # if it's greater than width -1
                self.hit_right_edge = True
        elif self.rect.left <= 0:
                self.hit_left_edge = True
        if self.rect.top <= 0: 
                self.hit_right_edge = True
        elif self.rect.bottom >= self.screensize[1]-1:
                self.hit_left_edge = True

        # check for a collision between the rectangles
        for player in player_list:
            if player.side == 1:
                if self.rect.colliderect(player.rect):
                    print("it's a hit", player.rect.center, self.rect.center)
                    self.direction[0] = -1
                    self.player_score += 1
                    if self.player_score == 10: # win if you score 15 points
                        self.player_paddle_win = True   
            else:
                if self.rect.colliderect(player.rect):
                    print("it's an opposite hit", player.rect.center, self.rect.center)
                    self.direction[0] = 1
                    self.ai_score += 1
                    if self.ai_score == 10: # lose if the computer scores 15 points
                        self.ai_paddle_win = True
    def get_info(self):
        info = {
            "id": self.id,
            "x": self.centerx,
            "y": self.centery,
            "lscore": self.ai_score,
            "rscore": self.player_score,
        }
        return info

