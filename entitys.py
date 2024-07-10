import pygame
import settings


class Ball(pygame.sprite.Sprite):
    def __init__(self, init_x: int, init_y: int):
        super().__init__()

        self.speed: int = 5
        self.direction: pygame.Vector2 = pygame.Vector2(1, 1)
        self.pos: pygame.Vector2 = pygame.Vector2(init_x, init_y)

        self.image: pygame.Surface = pygame.Surface(size=(16, 16))
        self.image.fill((255, 0, 0))

        self.rect: pygame.Rect = pygame.rect.Rect(self.pos.x, self.pos.y, 16, 16)


    def update(self) -> None:
        '''change the position of the ball'''
        self.pos.x += self.speed * self.direction.x
        self.pos.y += self.speed * self.direction.y

        self.rect.x = self.pos.x
        self.rect.y = self.pos.y 


        # check for collision whith the walls
        if self.pos.x < 0 or (self.pos.x+self.rect.width) > settings.WIDTH :
            self.direction.x *= -1
        if self.pos.y < 0 or (self.pos.y+self.rect.height) > settings.HEIGHT :
            self.direction.y *= -1
        

    def render(self, canvas: pygame.Surface) -> None:
        canvas.blit(self.image, self.rect)


class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        # only move on the x axis so some value are hard coded
        super().__init__()

        self.size: int = 150
        self.speed: int = 5
        self.direction: int = 0

        self.pos: pygame.Vector2 = pygame.Vector2( ( (settings.WIDTH/2) -(self.size/2) ), settings.HEIGHT-settings.HEIGHT/10)  # center the paddle on x and 10% of height on y
        self.rect: pygame.Rect = pygame.Rect(self.pos.x, self.pos.y, self.size, 20)  # hardcoded height
        self.image: pygame.Surface = pygame.Surface(size=(self.size, 20))  # must match the rect height
        self.image.fill((0, 0, 255))
    

    def update(self) -> None:
        self.pos.x += self.speed * self.direction


    def render(self, canvas: pygame.Surface) -> None:
        canvas.blit(self.image, self.rect)
