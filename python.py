import pygame as pg
import random
from os import path
import pyfirmata
import time

# Initialize Pygame
pg.init()

# Define screen resolution and FPS
width = 480
height = 600
FPS = 60

# Define colors
white = (255, 255, 255)
black = (0, 0, 0)

# Initialize Pygame window
screen = pg.display.set_mode((width, height))
pg.display.set_caption("ShipSpace!")
clock = pg.time.Clock()

# Load game graphics
img_dir = path.join('/Users/wttw/Documents/moduino_game/Workshop_Pygame_student_2024 2/source/img')
bg = pg.image.load(path.join(img_dir, "space.png")).convert()
ship_img = pg.image.load(path.join(img_dir, "Ship.png")).convert()
meteor_img = pg.image.load(path.join(img_dir, "meteor_med.png")).convert()
bullet_img = pg.image.load(path.join(img_dir, "red_bullet.png")).convert()

bgEnd = pg.image.load(path.join(img_dir, "Pen.png")).convert()
bgEnd_rect = bgEnd.get_rect()

# Initialize Pyfirmata
port = '/dev/cu.usbserial-A50285BI'  # Update this to your port
board = pyfirmata.Arduino(port)
it = pyfirmata.util.Iterator(board)
it.start()

# Setup analog input pins
X_pin = board.get_pin('a:0:i')
Y_pin = board.get_pin('a:1:i')
SW_pin = board.get_pin('a:2:i')

# Enable reporting for analog pins
X_pin.enable_reporting()
Y_pin.enable_reporting()
SW_pin.enable_reporting()

# Define classes
class Ship(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.transform.scale(ship_img, (50, 38))
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.centerx = width / 2
        self.rect.bottom = height - 10
        self.speedx = 0
        self.speedy = 0

    def update(self):
        self.speedx = 0
        self.speedy = 0
        
        # Read joystick values
        X_value = X_pin.read()
        Y_value = Y_pin.read()
        SW_value = SW_pin.read()

        # Map joystick values to ship movement
        if X_value is not None:
            self.speedx = (X_value - 0.5) * 16
        if Y_value is not None:
            self.speedy = (Y_value - 0.5) * 16

        # Update ship position
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        # Keep ship within screen bounds
        self.rect.x = max(0, min(self.rect.x, width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, height - self.rect.height))
    
    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
# Define other classes and functions
# ...
class Meteor(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = meteor_img
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(width - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-3, 3)

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > height + 10 or self.rect.left < -25 or self.rect.right > width + 20:
            self.rect.x = random.randrange(width - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)
class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(black)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        # ทำลายลูกกระสุนทิ้งถ้าลูกกระสุนออกจากหน้าจอ
        if self.rect.bottom < 0:
            self.kill()

def newmeteor():
    m = Meteor()
    all_sprites.add(m)
    meteors.add(m)

font_name = pg.font.match_font('arial')
def draw_text(surf, text, size, x, y):
    font = pg.font.Font(font_name, size)
    text_surface = font.render(text, True, white)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)
# Game setup
new_game = True
all_sprites = pg.sprite.Group()
meteors = pg.sprite.Group()
bullets = pg.sprite.Group()
score = 0
# Main game loop
while True:
    clock.tick(FPS)

    if new_game:
        new_game = False

        all_sprites = pg.sprite.Group()
        meteors = pg.sprite.Group()
        bullets = pg.sprite.Group()

        # TO DO 1-2 : สร้าง Object ให้กับ ship
        ship = Ship()


        # TO DO 1-3 : เพิ่ม ship ลงใน all_sprites
        all_sprites.add(ship)
        for i in range(8):
            newmeteor()
    print(SW_pin.read())
    if SW_pin.read() == 0:  # Handle joystick button press for shooting
        ship.shoot()
        time.sleep(0.01)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
        
    all_sprites.update()

    # Check for collisions
    # ...
    hits = pg.sprite.groupcollide(bullets, meteors, True, True)
    for hit in hits:
        newmeteor()
        score +=1
        
    hits = pg.sprite.spritecollide(ship, meteors, False)
    if hits:
        new_game = True
        score=0

    screen.fill(black)
    screen.blit(bg, (0, 0))
    draw_text(screen, f"Score: {score}", 24, width / 2, 10)

    all_sprites.draw(screen)
    pg.display.flip()

pg.quit()
board.exit()
