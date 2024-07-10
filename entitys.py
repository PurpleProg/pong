import pygame
import settings


class Ball(pygame.sprite.Sprite):
    def __init__(self, init_x: int, init_y: int) -> None:
        super().__init__()

        self.speed: int = 4
        self.direction: pygame.Vector2 = pygame.Vector2(1, 1)
        self.pos: pygame.Vector2 = pygame.Vector2(init_x, init_y)

        self.image: pygame.Surface = pygame.Surface(size=(16, 16))
        self.image.fill((255, 0, 0))

        self.rect: pygame.Rect = pygame.rect.Rect(self.pos.x, self.pos.y, 16, 16)


    def update(self, paddle) -> None:
        '''change the position of the ball'''
        self.pos.x += self.speed * self.direction.x
        self.pos.y += self.speed * self.direction.y

        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y) 

        self.collide_walls()
        self.collide_paddle(paddle)


    def collide_walls(self) -> None:
        ''' check for collision whith the walls and update the direction'''
        if self.pos.x < 0 or (self.pos.x+self.rect.width) > settings.WIDTH :
            self.direction.x *= -1
        if self.pos.y < 0:
            self.direction.y *= -1


    def collide_paddle(self, paddle) -> None:
        # unexpected behaviour when collide from sides
        # TODO: handle collisions depending on the place where the ball touch the paddel
        if self.rect.colliderect(paddle.rect):
            self.direction.y *= -1
    

    def render(self, canvas: pygame.Surface) -> None:
        canvas.blit(self.image, self.rect)


class Paddle(pygame.sprite.Sprite):
    def __init__(self) -> None:
        # only move on the x axis so some value are hard coded
        super().__init__()

        self.size: int = 150
        self.speed: int = 5
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
