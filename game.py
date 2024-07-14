import pygame
import sys  # for proper exit
import settings
import json
import base64
from states import Mainmenu, State


class Game:
    def __init__(self) -> None:
        # font
        pygame.init()
        pygame.font.init()
        self.font = pygame.font.Font(settings.FONT_NAME, settings.FONT_SIZE)
        # display
        self.display = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        pygame.display.set_caption("Pong Game")
        self.canvas = pygame.Surface(size=(settings.WIDTH, settings.HEIGHT))

        # init a stack
        self.stack: list[State] = []
        menu = Mainmenu(self)
        menu.enter_state()

        # init global game var
        self.running: bool = True
        self.clock = pygame.time.Clock()
        self.keys: dict[str, bool] = {
            'ESCAPE': False,
            'RETURN': False,
            'UP': False,
            'DOWN': False,
            'RIGHT': False,
            'LEFT': False,
            'p': False,
        }
        try:
            with open('highscore', 'r') as highscore_file:
                encoded_json: str = highscore_file.read()
                decoded_json: str = base64.b64decode(encoded_json.encode()).decode()
                self.highscore = json.loads(decoded_json)
        except FileNotFoundError:
            # if the file is not found, create it with hiscore 0
            with open('highscore', 'w') as highscore:
                self.highscore = {'manu': 0}
                json_data = json.dumps(self.highscore)
                encoded_data = base64.b64encode(json_data.encode())    # byte like objects
                highscore.write(encoded_data.decode())   # decode method just convert it to string

        
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
                    sys.exit()
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE:
                            self.keys['ESCAPE'] = True
                        case pygame.K_RETURN:
                            self.keys['RETURN'] = True
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
                            self.keys['RETURN'] = False
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
        self.stack[-1].update()
        

    def render(self) -> None:
        '''draw stuff, update screen and limit FPS.'''

        self.stack[-1].render()

        self.display.blit(source=self.canvas, dest=(0, 0))
        pygame.display.flip()
        self.clock.tick(settings.FPS)
