import pygame
from pygame.locals import K_UP, K_DOWN, KEYDOWN, K_ESCAPE, QUIT
from network import GameMode, GameServer, GameClient
from threading import Thread

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen.fill((255, 255, 255))

choice = input("Server or client? (s/c): ")
while choice.lower() not in ["s", "c"]:
    print("Invalid choice")
    choice = input("Server or client? (s/c): ")

if choice == "s":
    mode = GameMode.SERVER
    game = GameServer()

elif choice == "c":
    mode = GameMode.CLIENT
    game = GameClient()

Thread(target=game.run).start()

class Paddle(pygame.sprite.Sprite):
    def __init__(self, position: str):
        super().__init__()
        self.surf = pygame.Surface((20, 175))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect()
        self.scored = 0

        if position == "left":
            self.rect.left = 5
        elif position == "right":
            self.rect.right = SCREEN_WIDTH - 5
    
    def update(self, pressed_keys):
        key = None
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -5)
            key = K_UP

        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, 5)
            key = K_DOWN

        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
        
        return key
    
    def update_with_key(self, key):
        if key == K_UP:
            self.rect.move_ip(0, -5)

        if key == K_DOWN:
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
    
    def move(self) -> None:
        self.rect.move_ip(self.x_travel, self.y_travel)

        if (self.rect.top <= 0) or (self.rect.bottom >= SCREEN_HEIGHT):
            self.y_travel = -self.y_travel

    def should_be_scored(self) -> bool:
        if self.rect.left <= 0:
            return True
        elif self.rect.right >= SCREEN_WIDTH:
            return True
        return False
    
    def collide(self, sprite: Paddle):
        self.x_travel = -self.x_travel
        print(self.rect)
        print(sprite.rect)

        print(self.rect.topright)
        print(self.rect.left)
        if self.rect.midright[1] >= sprite.rect.topright[1] and self.rect.midright[1] <= sprite.rect.midright[1]:
            self.y_travel = -1
        else:
            self.y_travel = 1
        
    def flip_x(self):
        # Flip the ball's x position on the screen
        self.rect.left = SCREEN_WIDTH - self.rect.left

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

        elif event.type == pygame.USEREVENT + 1:
            opponent.update_with_key(event.key)

        elif event.type == pygame.USEREVENT + 3:
            opponent.scored = event.server
            player.scored = event.client

        elif event.type == pygame.USEREVENT + 4:
            ball.rect.topleft = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
            if event.starts_towards == "server" and mode == GameMode.SERVER:
                ball.x_travel = 5
            elif event.starts_towards == "client" and mode == GameMode.CLIENT:
                ball.x_travel = 5

            else:
                ball.x_travel = -5

            ball.y_travel = 0
            ball.flip_x()
    
    pressed = pygame.key.get_pressed()
    
    if pressed.count(1) > 0 and pressed.count(1) < 2:
        key = player.update(pressed)
        game.move(key)

    ball.move()

    if ball.should_be_scored() and mode == GameMode.SERVER:
        if ball.rect.left <= 0:
            opponent.scored += 1
            game.score(opponent.scored, player.scored)
        elif ball.rect.right >= SCREEN_WIDTH:
            player.scored += 1
            game.score(opponent.scored, player.scored)
        game.reset_ball("server" if ball.rect.left <= 0 else "client")
        ball.flip_x()

    screen.fill((0, 0, 0))

    for sprite in all_sprites:
        screen.blit(sprite.surf, sprite.rect)

    if sprite := pygame.sprite.spritecollideany(ball, players):
        ball.collide(sprite)

    score = pygame.font.Font(None, 50).render(f"{opponent.scored} / {player.scored}", True, (255, 255, 255))
    screen.blit(score, (SCREEN_WIDTH/2, 50))

    pygame.display.flip()

    clock.tick(30)