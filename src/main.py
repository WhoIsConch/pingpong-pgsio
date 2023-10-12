import pygame
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, KEYDOWN, K_ESCAPE, QUIT
import socketio as sio

pygame.init()
clock = pygame.time.Clock()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen.fill((255, 255, 255))

class Paddle(pygame.sprite.Sprite):
    def __init__(self, position: str):
        super().__init__()
        self.surf = pygame.Surface((20, 175))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect()

        if position == "left":
            self.rect.left = 5
        elif position == "right":
            self.rect.right = SCREEN_WIDTH - 5
    
    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -5)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, 5)

        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((20, 20))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect()
        self.x_travel = 5
        self.y_travel = 0

        self.rect.left = SCREEN_WIDTH/2
        self.rect.top = SCREEN_HEIGHT/2
    
    def move(self):
        self.rect.move_ip(self.x_travel, self.y_travel)

        if (self.rect.top <= 0) or (self.rect.bottom >= SCREEN_HEIGHT):
            self.y_travel = -self.y_travel
        
    
    def collide(self, sprite: Paddle):
        self.x_travel = -self.x_travel
        print(self.rect)
        print(sprite.rect)

        if self.x_travel > 0:
            print(self.rect.topright)
            print(self.rect.left)
            if self.rect.topright[1] <= (sprite.rect.topleft[1] / 2):
                self.y_travel = -1
            else:
                self.y_travel = 1
        
        else:
            if self.rect.topleft[1] <= sprite.rect.height / 2:
                self.y_travel = -1
            else:
                self.y_travel = 1

player = Paddle("right")
opponent = Paddle("left")
ball = Ball()

all_sprites = pygame.sprite.Group(player, opponent, ball)
players = pygame.sprite.Group(player, opponent)

running = True

while running:
    for event in pygame.event.get():
        # Check for KEYDOWN event
        if event.type == KEYDOWN:
            # If the Esc key is pressed, then exit the main loop
            if event.key == K_ESCAPE:
                running = False
        # Check for QUIT event. If QUIT, then set running to false.
        elif event.type == QUIT:
            running = False
    
    pressed = pygame.key.get_pressed()
    
    player.update(pressed)
    opponent.update(pressed)
    ball.move()

    screen.fill((0, 0, 0))

    for sprite in all_sprites:
        screen.blit(sprite.surf, sprite.rect)

    if sprite := pygame.sprite.spritecollideany(ball, players):
        ball.collide(sprite)

    pygame.display.flip()

    clock.tick(30)