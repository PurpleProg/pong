import pygame
import settings


class Ball(pygame.sprite.Sprite):
    def __init__(self, game) -> None:
        super().__init__()

        self.game = game
        self.speed: int = settings.BALL_SPEED
        self.direction: pygame.Vector2 = pygame.Vector2(1, 1)
        self.pos: pygame.Vector2 = pygame.Vector2(
            settings.WIDTH/2 - 16/2,
            settings.HEIGHT - settings.HEIGHT/6
        )

        self.image: pygame.Surface = pygame.Surface(size=(16, 16))
        self.image.fill((255, 0, 0))

        self.rect: pygame.Rect = pygame.rect.Rect(self.pos.x, self.pos.y, 16, 16)
        self.prev_rect = self.rect.copy()


    def update(self, paddle, bricks) -> None:
        '''change the position of the ball'''

        self.pos.x += self.speed * self.direction.x
        self.pos.y += self.speed * self.direction.y
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)

        self.collide(paddle, bricks)


    def collide(self, paddle, bricks) -> None:
        # walls
        if self.rect.left < 0 or self.rect.right > settings.WIDTH :
            self.direction.x *= -1
            if self.rect.right > settings.WIDTH:   # prevent a bug where you can push the ball into the wall
                self.rect.right = settings.WIDTH
                self.direction.x = -1
            elif self.rect.left < 0:
                self.rect.left = 0
                self.direction.x = 1
        if self.rect.top < 0:
            self.rect.top = 0
            self.direction.y = 1

        # paddle
        if self.rect.colliderect(paddle.rect):
            self.rect.bottom = paddle.rect.top
            self.direction.y = -1
            if self.rect.center > paddle.rect.center:
                self.direction.x = 1
            else:
                self.direction.x = -1

        # bricks
        for brick in bricks:
            if brick.rect.colliderect(self.rect):
                bricks.remove(brick)
                self.game.stack[-1].score += 1    # assuming that the ball is ONLY used from gameplay
                # X axis
                if self.direction.x > 0:
                    delta_x = self.rect.right - brick.rect.left
                else:
                    delta_x = brick.rect.right - self.rect.left
                # Y axis
                if self.direction.y > 0:
                    delta_y = self.rect.bottom - brick.rect.top
                else:
                    delta_y = brick.rect.bottom - self.rect.top
                # check incoming direction
                if abs(delta_x - delta_y) < 10:   # corner (aproximation)
                    self.direction.x *= -1
                    self.direction.y *= -1
                elif delta_x > delta_y:   # comming from the top of the block 
                    self.direction.y *= -1
                else:                      # comming from the sides
                    self.direction.x *= -1

        
    def render(self) -> None:
        '''blit itself to the last state on the stack'''
        self.game.stack[-1].canvas.blit(self.image, self.rect)


class Paddle(pygame.sprite.Sprite):
    def __init__(self) -> None:
        # only move on the x axis so some value are hard coded
        super().__init__()

        self.size: int = 150
        self.speed: int = settings.PADDLE_SPEED
        self.direction: int = 0

        self.pos: pygame.Vector2 = pygame.Vector2( ( (settings.WIDTH/2) -(self.size/2) ), settings.HEIGHT-settings.HEIGHT/10)  # center the paddle on x and 10% of height on y
        self.rect: pygame.Rect = pygame.Rect(self.pos.x, self.pos.y, self.size, 20)  # hardcoded height
        self.image: pygame.Surface = pygame.Surface(size=(self.size, 20))  # must match the rect height
        self.image.fill((0, 0, 255))
    

    def update(self, keys: dict[str ,bool]) -> None:

        # move with arrows
        if keys['RIGHT']:
            self.direction = 1
        elif keys['LEFT']:
            self.direction = -1
        else:
            self.direction = 0

        # prevent paddle from going out of bouds
        if self.rect.right > settings.WIDTH:
            self.pos.x = settings.WIDTH-self.size
        elif self.rect.left < 0:
            self.pos.x = 0
        

        self.pos.x += self.speed * self.direction
        self.rect.x = int(self.pos.x)


    def render(self, canvas: pygame.Surface) -> None:
        canvas.blit(self.image, self.rect)


class Brick(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y) -> None:
        super().__init__()
        self.pos: pygame.Vector2 = pygame.Vector2(pos_x, pos_y)
        self.image: pygame.Surface = pygame.Surface((settings.BRICK_WIDTH, settings.BRICK_HEIGHT))
        self.image.fill(settings.BRICK_COLOR)

        self.rect: pygame.Rect = pygame.Rect(self.pos.x, self.pos.y, settings.BRICK_WIDTH, settings.BRICK_HEIGHT)


    def render(self, canvas) -> None:
        canvas.blit(self.image, self.rect)

