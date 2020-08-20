import pygame
import numpy as np
from pygame.locals import *
import time

BLACK = (  0,  0,  0)
WHITE = (255,255,255)
BLUE  = (  0,  0,255)
GREEN = (  0,255,  0)
RED   = (255,  0,  0)
GREY  = (128,128,128)

WIDTH = 750
HEIGHT = 1000

size = [WIDTH, HEIGHT]
screen = pygame.display.set_mode(size)

pygame.init()
pygame.display.set_caption("space craft")
clock = pygame.time.Clock()

FPS = 30
done = False
pi = np.pi
e = 1e-7

images ={\
    "shooter":pygame.image.load("images/shooter.png"),\
    "laser":pygame.image.load("images/missile1.png"),\
    "blue_ball":pygame.image.load("images/blue_ball.png"),\
    "explosion1":pygame.image.load("images/explosion1.png"),\
    "enemy1":pygame.image.load("images/enemy1.png"),\
    "enemy2":pygame.image.load("images/enemy2.png"),\
    "map1":pygame.image.load("images/map1.png"),\
    "gameover":pygame.image.load("images/gameover.png")\
}
    

def drawObject(obj,x,y):
    screen.blit(obj,(x,y))
    
def getHitMask(img):
    mask = []
    for x in range(img.get_width()):
        mask.append([])
        for y in range(img.get_height()):
            mask[x].append(bool(img.get_at((x,y))[3]))
    return mask

def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    rect = rect1.clip(rect2)

    if rect.width == 0 or rect.height == 0:
        return False

    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y

    for x in range(rect.width):
        for y in range(rect.height):
            if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                return True
    return False



class shooter:
    def __init__(self):
        self.x = WIDTH * 0.4
        self.y = HEIGHT * 0.9
        self.v = 10
        self.shooter_image = images["shooter"]
        self.missile_image = images["laser"]
        self.missileXY = []
        self.img_size = self.shooter_image.get_rect().size
        self.w = self.img_size[0]
        self.h = self.img_size[1]
        self.start = time.time()
        self.die = False
        
    def display(self):
        drawObject(self.shooter_image, self.x, self.y)
        for missile in self.missileXY:
            drawObject(missile.image, missile.x, missile.y)
        
    def reposition(self):
        if self.x < 0:
            self.x = 0
        elif self.y > HEIGHT - self.h:
            self.y = HEIGHT - self.h
        elif self.x > WIDTH - self.w:
            self.x = WIDTH - self.w
        elif self.y < 0:
            self.y = 0
            
    def move(self, dx, dy):
        if time.time() - self.start > 0.3:
            #self.shoot()
            self.start = time.time()
        self.x += dx
        self.y += dy
        self.reposition()
        for i, missile in enumerate(self.missileXY):
            missile.move()
            if not missile.isValidPos():
                try:
                    self.missileXY.remove(missile)
                except:
                    pass

    def shoot(self):
        self.missileXY.append(missile(self.x + self.w * 0.5, self.y - images["laser"].get_rect().size[1],0,-15,"laser",1))
        
    def Collision(self, enemy):
        rect1 = pygame.Rect(enemy.x, enemy.y, enemy.w, enemy.h)
        hitmask1 = getHitMask(enemy.image)
        hitmask2 = getHitMask(self.missile_image)
        
        for missile in self.missileXY:
            rect2 = pygame.Rect(missile.x, missile.y, missile.size[0], missile.size[1])
            if pixelCollision(rect1, rect2, hitmask1, hitmask2):
                enemy.hp = 0 if enemy.hp < 0 else enemy.hp - missile.damage
                drawObject(images["explosion1"], missile.x - 30, missile.y - 30)
                try:
                    self.missileXY.remove(missile)
                except:
                    pass
        
class enemy:
    def __init__(self, x = 0, y = 0, lv = 1, max_hp = 50, d = (1, 1)):
        self.x = x
        self.y = y
        self.d = d      # direction vector
        self.hp = max_hp
        self.max_hp = max_hp
        if lv == 1:
            self.image = images["enemy1"]
        elif lv == 2:
            self.image = images["enemy2"]
        self.size = self.image.get_rect().size
        self.w = self.size[0]
        self.h = self.size[1]
        self.missileXY = []
        self.flag = True
    
    def move(self, a = (1, 1)):
        if self.x < 700:
            self.x += self.d[0] * a[0]
        else:
            self.d = (-1, 0)
        if self.y < 300:
            self.y += self.d[1] * a[1]
                   
    def render(self):
        if self.hp <= 0:
            return
        # Enemy Object
        drawObject(self.image, self.x, self.y)
        # Enemy Attack Object
        if self.missileXY:
            for i in self.missileXY:
                i.move(0.2,0.2)
                drawObject(i.image, i.x, i.y)
                if not i.isValidPos():
                    try:
                        self.missileXY.remove(i)
                    except:
                        pass
        # Enemy hp bar
        pygame.draw.rect(screen, GREEN, [30, 30, int(690 * (self.hp / self.max_hp)), 10])
        
    def attack1(self, a):
        num_missile = 10
        x_ = self.x + self.size[0] / 2
        y_ = self.y + self.size[1] / 2
        for i in range(num_missile):
            x__ = x_ + 50 * np.cos(2 * pi / num_missile * i + a)
            y__ = y_ + 50 * np.sin(2 * pi / num_missile * i + a)
            self.missileXY.append(missile(x__, y__, x__ - x_, y__ - y_,"blue_ball"))
    
    def attack2(self, a):
        num_missile = 10
        x_ = self.x + self.size[0] / 2
        y_ = self.y + self.size[1] / 2
        for i in range(num_missile):
            x__ = x_ + 50 * np.cos(pi / (num_missile) * i + a)
            y__ = y_ + 50 * np.sin(pi / (num_missile) * i + a)
            
            self.missileXY.append(missile(x__, y__, x__ - x_, y__ - y_,"blue_ball"))
        
            
    def Collision(self, player):
        rect1 = pygame.Rect(player.x, player.y, player.w, player.h)
        hitmask1 = getHitMask(player.shooter_image)
        hitmask2 = getHitMask(self.missileXY[0].image)
        
        for i in self.missileXY:
            rect2 = pygame.Rect(i.x, i.y, i.size[0], i.size[1])
            if pixelCollision(rect1, rect2, hitmask1, hitmask2):
                drawObject(images["explosion1"], i.x, i.y)
                player.die = True
                try:
                    self.missileXY.remove(i)
                except:
                    pass
                print("you die")   
    
class missile:
    def __init__(self, x, y, d_x, d_y, t = "none",damage = 10):
        self.x = x
        self.y = y
        self.d_x = d_x
        self.d_y = d_y
        self.t = t
        self.damage = damage
        if t == "blue_ball":
            self.image = images["blue_ball"]
        elif t == "laser":
            self.image = images["laser"]
        self.size = self.image.get_rect().size
        
    def move(self, m_x = 1, m_y = 1):
        self.x += self.d_x * m_x
        self.y += self.d_y * m_y
        
    def isValidPos(self):
        return not (self.x > WIDTH or self.x < 0 or self.y > HEIGHT or self.y < 0)
        
player = shooter()
it = 0
(dx, dy) = (0,0)

e1 = enemy(30,70,d = (1,0))
e2 = enemy(30,70,2,100,(1,0.1))
enemys = [e2]
start = time.time()
a = 0.1

while not done:
    drawObject(images["map1"], 0, 0)
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                done = True
            if event.key == K_LEFT:
                dx -= player.v
            if event.key == K_RIGHT:
                dx += player.v
            if event.key == K_UP:
                dy -= player.v
            if event.key == K_DOWN:
                dy += player.v
            if event.key == K_z:
                player.shoot()
        if event.type == KEYUP:
            if event.key == K_LEFT or event.key == K_RIGHT:
                dx = 0
            elif event.key == K_UP or event.key == K_DOWN:
                dy = 0

    if it % 30 == 29:
        e.attack2(a)
        a*=-1
     
    for e in enemys:
        e.move()
        e.render()
        if e.missileXY and e.hp:
            e.Collision(player)
        if player.missileXY and e.hp:
            player.Collision(e)
        
    if not player.die:
        player.move(dx, dy)
        player.display()
    else:
        drawObject(images["gameover"],275,450)
        pygame.display.flip()
        pygame.time.delay(2000)
        done = True    
        
    
    pygame.display.flip()
    it = (it + 1) % FPS
    clock.tick(FPS)
    
pygame.quit()