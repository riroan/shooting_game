import pygame
import numpy as np
import random
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
    "missile1":pygame.image.load("images/missile1.png"),\
    "missile2":pygame.image.load("images/missile2.png"),\
    "laser1":pygame.image.load("images/laser1.png"),\
    "laser2":pygame.image.load("images/laser2.png"),\
    "god_laser":pygame.image.load("images/god_laser.png"),\
    "blue_ball":pygame.image.load("images/blue_ball.png"),\
    "red_ball":pygame.image.load("images/red_ball.png"),\
    "ball":pygame.image.load("images/ball.png"),\
    "explosion1":pygame.image.load("images/explosion1.png"),\
    "enemy1":pygame.image.load("images/enemy1.png"),\
    "enemy2":pygame.image.load("images/enemy2.png"),\
    "map1":pygame.image.load("images/map1.png"),\
    "gameover":pygame.image.load("images/gameover.png"),\
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

def isValidPos(x, y, p_x = 0, p_y = 0):
    return not (x + p_x > WIDTH or x < p_x or y + p_y > HEIGHT or y < p_y)

def p(x):
    return random.random() <= x

def normalization(x, y, a = 1):
    return (x/np.sqrt(x*x+y*y) * a, y/np.sqrt(x*x+y*y) * a)

class shooter:
    def __init__(self):
        self.x = WIDTH * 0.4
        self.y = HEIGHT * 0.9
        self.v = 10
        self.shooter_image = images["shooter"]
        self.missileXY = []
        self.img_size = self.shooter_image.get_rect().size
        self.w = self.img_size[0]
        self.h = self.img_size[1]
        self.start = time.time()
        self.die = False
        self.shoot_flag = False
        self.weapon = 5
        
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
        self.x += dx
        self.y += dy
        self.reposition()
        for i, missile in enumerate(self.missileXY):
            missile.move()
            if not isValidPos(missile.x, missile.y):
                try:
                    self.missileXY.remove(missile)
                except:
                    pass

    def shoot(self):
        if self.weapon == 1:
            self.missileXY.append(missile(self.x + self.w * 0.5, self.y - images["missile1"].get_rect().size[1],0,-15,"missile1",1))
        elif self.weapon == 3:
            self.missileXY.append(missile(self.x + self.w * 0.4, self.y - images["missile2"].get_rect().size[1],0,-15,"missile2",3))
            self.missileXY.append(missile(self.x, self.y,0,-15, "missile1", 1))
            self.missileXY.append(missile(self.x+self.w,self.y,0,-15,"missile1",1))
        elif self.weapon == 5:
            self.missileXY.append(missile(self.x + self.w * 0.4, self.y - images["laser1"].get_rect().size[1],0,-15,"laser1",10))
            self.missileXY.append(missile(self.x, self.y,0,-15, "laser2", 3))
            self.missileXY.append(missile(self.x+self.w,self.y,0,-15,"laser2",3))
        elif self.weapon == 10:
            self.missileXY.append(missile(self.x, self.y - images["god_laser"].get_rect().size[1],0,-20,"god_laser",30))
        
    def Collision(self, enemy):
        rect1 = pygame.Rect(enemy.x, enemy.y, enemy.w, enemy.h)
        hitmask1 = getHitMask(enemy.image)
        
        for missile in self.missileXY:    
            hitmask2 = getHitMask(missile.image)
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
        self.image = images["enemy1"]
        self.size = self.image.get_rect().size
        self.w = self.size[0]
        self.h = self.size[1]
        self.missiles = []
        self.flag = True
        self.lv = lv
    
    def move(self, a = (2, 2)):
        if isValidPos(self.x, self.y, self.size[0] + 50, self.size[1] + 50):
            self.x += self.d[0] * a[0]
            self.y += self.d[1] * a[1]
        else:
            self.d = (self.d[0] * -1, 0)
            self.x += self.d[0] * a[0]
            self.y += self.d[1] * a[1]
                   
    def render(self):
        if self.hp <= 0:
            return
        # Enemy Object
        drawObject(self.image, self.x, self.y)
        # Enemy Attack Object
        if self.missiles:
            for i in self.missiles:
                i.move(0.2,0.2)
                drawObject(i.image, i.x, i.y)
                if not isValidPos(i.x, i.y) and self.lv != 6:
                    try:
                        self.missiles.remove(i)
                    except:
                        pass
        # Enemy hp bar
        pygame.draw.rect(screen, GREEN, [30, 30, int(690 * (self.hp / self.max_hp)), 10])
    
    def attack(self):
        pass
                
    def Collision(self, player):
        rect1 = pygame.Rect(player.x, player.y, player.w, player.h)
        hitmask1 = getHitMask(player.shooter_image)
        hitmask2 = getHitMask(self.missiles[0].image)
        
        for i in self.missiles:
            rect2 = pygame.Rect(i.x, i.y, i.size[0], i.size[1])
            if pixelCollision(rect1, rect2, hitmask1, hitmask2):
                drawObject(images["explosion1"], i.x, i.y)
                player.die = True
                try:
                    self.missiles.remove(i)
                except:
                    pass
                print("you die")

class enemy1(enemy):
    def __init__(self, x = 0, y = 0, max_hp = 50, d = (1, 1)):
        super().__init__(x, y, 1, max_hp, d)
        self.image = images["enemy1"]
        self.size = self.image.get_rect().size
        self.w = self.size[0]
        self.h = self.size[1]
        
    def attack(self):
        a = random.random() - 0.5
        num_missile = 7 
        x_ = self.x + self.size[0] / 2
        y_ = self.y + self.size[1] / 2
        for i in range(num_missile):
            x__ = x_ + 50 * np.cos(2 * pi / num_missile * i + a)
            y__ = y_ + 50 * np.sin(2 * pi / num_missile * i + a)
            self.missiles.append(missile(x__, y__, x__ - x_, y__ - y_,"red_ball"))    
                
class enemy2(enemy):
    def __init__(self, x = 0, y = 0, max_hp = 100, d = (1, 1)):
        super().__init__(x, y, 2, max_hp, d)
        self.image = images["enemy2"]
        self.size = self.image.get_rect().size
        self.w = self.size[0]
        self.h = self.size[1]
        
    def attack(self):
        a = random.random() - 0.5
        num_missile = 10
        x_ = self.x + self.size[0] / 2
        y_ = self.y + self.size[1] / 2
        for i in range(num_missile):
            x__ = x_ + 50 * np.cos(pi / (num_missile) * i + a)
            y__ = y_ + 50 * np.sin(pi / (num_missile) * i + a)
            self.missiles.append(missile(x__, y__, x__ - x_, y__ - y_,"blue_ball"))

class enemy3(enemy):
    def __init__(self, x = 0, y = 0, max_hp = 300, d = (1, 1)):
        super().__init__(x, y, 3, max_hp, d)
        self.image = images["enemy2"]
        self.size = self.image.get_rect().size
        self.w = self.size[0]
        self.h = self.size[1]
        
    def move(self):
        super().move()
        for m in self.missiles:
            self.bounce(m)
        
    def attack(self):
        num_missile = 7
        if not self.missiles:
            for i in range(num_missile):
                a = random.randrange(20,40)
                self.missiles.append(missile(self.x, self.y, (random.random() - 0.3) * a, (random.random() - 0.3) * a,"ball"))
                
    def bounce(self, m):
        if m.x + m.size[0] > WIDTH or m.x < 10:
            m.d_x *= -1
        if m.y + m.size[1] > HEIGHT or m.y < 10:
            m.d_y *= -1

class enemy4(enemy):
    def __init__(self, x = 0, y = 0, max_hp = 500, d = (1, 1)):
        super().__init__(x, y, 4, max_hp, d)
        self.image = images["enemy2"]
        self.size = self.image.get_rect().size
        self.w = self.size[0]
        self.h = self.size[1]
        self.n = 1
        
    def attack(self):
        num_missile = 4
        k = 10
        s = [(0,0),(WIDTH,0),(0,HEIGHT),(WIDTH,HEIGHT)]
        a = WIDTH / k * self.n
        b = HEIGHT / k * self.n
        e = [(a,HEIGHT),(0,b),(WIDTH,HEIGHT-b),(WIDTH-a,0)]
        d = [normalization(e[i][0]-s[i][0],e[i][1]-s[i][1], 15) for i in range(num_missile)]
        for i in range(num_missile):
            self.missiles.append(missile(s[i][0],s[i][1],d[i][0],d[i][1],"blue_ball"))
        self.n = (self.n + 1) % (k / 2) + k / 2

class enemy6(enemy):
    def __init__(self, x = 0, y = 0, max_hp = 1000, d = (1, 1)):
        super().__init__(x, y, 6, max_hp, d)
        self.image = images["enemy2"]
        self.size = self.image.get_rect().size
        self.w = self.size[0]
        self.h = self.size[1]
        self.r = 200
        self.v = 0.05
        self.dx = 0
        
    def move(self):
        super().move()
        num_missile = len(self.missiles)
        if not num_missile:
            return
        self.dx += self.v
        if p(0.1):
            self.r += 10
        if p(0.1):
            self.r-= 5
        for i, m in enumerate(self.missiles):
            m.x = self.x + self.w / 2 + self.r * np.cos(2 * pi / num_missile * i + self.dx)
            m.y = self.y + self.h / 2 + self.r * np.sin(2 * pi / num_missile * i + self.dx)
        
    def attack(self):
        if self.missiles:
            return
        num_missile = 7
        for i in range(num_missile):
            self.missiles.append(missile(self.x + self.w / 2 + self.r * np.cos(2 * pi / num_missile * i), self.y + self.h / 2 + self.r * np.sin(2 * pi / num_missile * i), 0, 0, "blue_ball"))

class missile:
    def __init__(self, x, y, d_x, d_y, t = "none",damage = 10):
        self.x = x
        self.y = y
        self.d_x = d_x
        self.d_y = d_y
        self.t = t
        self.damage = damage
        self.image = images[t]
        self.size = self.image.get_rect().size
        
    def move(self, m_x = 1, m_y = 1):
        self.x += self.d_x * m_x
        self.y += self.d_y * m_y
        
player = shooter()
it = 0
(dx, dy) = (0,0)
 
e1 = enemy1(100,100,d = (1,0))
e2 = enemy2(200,200,100,(1,0.1))
e3 = enemy3(200,200,300,(1,0.1))
e4 = enemy4(200,200,300,(1,0.1))
e6 = enemy6(200,200,d=(1,0.1))
enemys = [e6]
start = time.time()
a = 0.1

while not done:
    screen.fill(BLACK)
    #drawObject(images["map1"], 0, 0)
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
                player.shoot_flag = 1
        if event.type == KEYUP:
            if event.key == K_LEFT or event.key == K_RIGHT:
                dx = 0
            if event.key == K_UP or event.key == K_DOWN:
                dy = 0
            if event.key == K_z:
                player.shoot_flag = 0
    player.shoot_flag = 1
    if player.shoot_flag and it % 10 == 1:
        player.shoot()
        
    for e in enemys:
        e.move()
        e.render()
        if e.missiles and e.hp:
            e.Collision(player)
        if player.missileXY and e.hp:
            player.Collision(e)
        # enemy die
        if e.hp <= 0:
            try:
                enemys.remove(e)
            except:
                pass
        # attack    
        if it % 12000 == 1:
            e.attack()
            
    if not player.die:
        player.move(dx, dy)
        player.display()
    else:
        drawObject(images["gameover"],275,450)
        pygame.display.flip()
        pygame.time.delay(2000)
        done = True
    
    pygame.display.flip()
    it += 1
    clock.tick(FPS)
    
pygame.quit()