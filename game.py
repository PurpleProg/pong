import pygame
import sys  # for proper exit
import settings
from entitys import Ball, Paddle


class Game:
    def __init__(self) -> None:
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
        self.paddle = Paddle()
    

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
                            self.keys['ENTER'] = True
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
                            self.keys['ENTER'] = False
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
        self.paddle.update(self.keys)
        self.ball.update(self.paddle)
        if self.check_game_over():
            self.game_over()


    def render(self) -> None:
        '''draw stuff, update screen and limit FPS.'''
        self.canvas.fill(color=settings.BACKGROUND_COLOR)

        self.paddle.render(self.canvas)
        self.ball.render(self.canvas)
        self.display.blit(source=self.canvas, dest=(0, 0))

        pygame.display.flip()
        self.clock.tick(settings.FPS)


    def check_game_over(self) -> bool:
        ''' check the ball pos '''
        if self.ball.pos.y > settings.HEIGHT:
            return True
        else:
            return False
    

    def game_over(self) -> None:
        self.running = False
        pygame.quit()
        sys.exit()
