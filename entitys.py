import pygame
import settings


class Ball(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()

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

        self.prev_rect.x = self.rect.x
        self.pos.x += self.speed * self.direction.x
        self.rect.x = int(self.pos.x)
        self.collide_x(paddle, bricks)

        self.prev_rect.y = self.rect.y
        self.pos.y += self.speed * self.direction.y
        self.rect.y = int(self.pos.y)
        self.collide_y(paddle, bricks)


    def collide_x(self, paddle, bricks) -> None:
        # walls
        if self.pos.x < 0 or (self.pos.x+self.rect.width) > settings.WIDTH :
            self.direction.x *= -1

        # paddle
        if self.rect.colliderect(paddle.rect):
            self.direction.x *= -1
            if self.prev_rect.left > paddle.rect.right:
                self.rect.left = paddle.rect.right
            elif self.prev_rect.right < paddle.rect.left:
                self.rect.right = paddle.rect.left

        # bricks
        for brick in bricks:
            if brick.rect.colliderect(self.rect):
                bricks.remove(brick)
                self.direction.x *= -1
                if self.prev_rect.left > brick.rect.right:
                    self.rect.left = brick.rect.right
                elif self.prev_rect.right < brick.rect.left:
                    self.rect.right = brick.rect.left
        

    def collide_y(self, paddle, bricks) -> None:
        # walls
        if self.pos.y < 0:
            self.direction.y *= -1

        # paddle
        if self.rect.colliderect(paddle.rect):
            self.direction.y *= -1
            self.rect.bottom = paddle.rect.top
            if self.rect.centerx > paddle.rect.centerx:
                self.direction.x = 1
            else:
                self.direction.x = -1

        # bricks
        for brick in bricks:
            if brick.rect.colliderect(self.rect):
                bricks.remove(brick)
                self.direction.y *= -1
                if self.prev_rect.top > brick.rect.bottom:
                    self.rect.top = brick.rect.bottom
                elif self.prev_rect.bottom < brick.rect.top:
                    self.rect.bottom = brick.rect.top


    def render(self, canvas: pygame.Surface) -> None:
        canvas.blit(self.image, self.rect)


class Paddle(pygame.sprite.Sprite):
    def __init__(self) -> None:
        # only move on the x axis so some value are hard coded
        super().__init__()

        self.size: int = 150
        self.speed: int = 6
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

