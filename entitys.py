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

        self.rect: pygame.rect.Rect = pygame.rect.Rect(self.pos.x, self.pos.y, 16, 16)


    def update(self) -> None:
        '''change the position of the ball'''
        self.pos.x += self.speed * self.direction.x
        self.pos.y += self.speed * self.direction.y

        self.rect.x = self.pos.x
        self.rect.y = self.pos.y        


    def render(self, canvas: pygame.Surface) -> None:
        canvas.blit(self.image, self.rect)
