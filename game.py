import pygame
import settings
from entitys import Ball


class Game:
    def __init__(self):
        # init pygame
        pygame.init()
        self.display = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        pygame.display.set_caption("Pong Game")
        self.canvas = pygame.Surface(size=(settings.WIDTH, settings.HEIGHT))


        # init global game var
        self.running: bool = True
        self.clock = pygame.time.Clock()
        self.keys: dict[str, bool] = {
            'RETURN': False,
            'ENTER': False,
            'UP': False,
            'DOWN': False,
            'RIGHT': False,
            'LEFT': False,
            'p': False,
        }

        # create objects
        self.ball = Ball(20, 20)
    
    def main_loop(self) -> None:
        self.event()
        self.udpate()
        self.render()

    def event(self) -> None:
        '''get event like keyboard press or mouse input and gather them in a dict'''
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.running = False
                    pygame.quit()
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE:
                            self.keys['ESCAPE'] = True
                        case pygame.K_RETURN:
                            self.kays['ENTER'] = True
                        case pygame.K_UP:
                            self.keys['UP'] = True
                        case pygame.K_DOWN:
                            self.keys['DOWN'] = True
                        case pygame.K_RIGHT:
                            self.keys['RIGHT'] = True
                        case pygame.K_LEFT:
                            self.keys['LEFT'] = True
                        case pygame.K_p:
                            self.keys['p'] = True
                case pygame.KEYUP:
                    match event.key:
                        case pygame.K_ESCAPE:
                            self.keys['ESCAPE'] = False
                        case pygame.K_RETURN:
                            self.kays['ENTER'] = False
                        case pygame.K_UP:
                            self.keys['UP'] = False
                        case pygame.K_DOWN:
                            self.keys['DOWN'] = False
                        case pygame.K_RIGHT:
                            self.keys['RIGHT'] = False
                        case pygame.K_LEFT:
                            self.keys['LEFT'] = False
                        case pygame.K_p:
                            self.keys['p'] = False
                

    def udpate(self) -> None:
        self.ball.update()

    def render(self) -> None:
        '''draw stuff, update screen and limit FPS.'''
        self.canvas.fill(color=settings.BACKGROUND_COLOR)

        self.ball.render(self.canvas)
        self.display.blit(source=self.canvas, dest=(0, 0))

        pygame.display.flip()
        self.clock.tick(settings.FPS)