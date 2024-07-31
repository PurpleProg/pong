import pygame
import settings
import sys  # for proper exit
import json  # for save
import base64   # for save
from typing import Callable
from entitys import Ball, Paddle, Brick


def save(score: int) -> None:
    ''' save the highscore to file '''
    score_data = {
        'manu': score
    }
    score_json: str = json.dumps(score_data)
    encoded_json: str = base64.b64encode(score_json.encode()).decode()
    with open('highscore', 'w') as highscore:
        highscore.write(encoded_json)


class State:
    ''' Blueprint of state for the stack
    handle the stack related stuff'''
    def __init__(self, stack) -> None:
        self.stack = stack
        if len(self.stack):
            self.prev_state = self.stack[-1]
        else:
            self.prev_state = None


    def update(self) -> None:
        raise NotImplementedError


    def render(self) -> None:
        raise NotImplementedError
    

    def enter_state(self) -> None:
        self.stack.append(self)
    

    def exit_state(self) -> None:
        self.stack.pop()


class Menu(State):
    '''Parent class of all menus
    also herit from state'''

    class _Label(pygame.sprite.Sprite):
        def __init__(self, text: str, pos: tuple[int, int]) -> None:
            self.text: str = text
            self.font: pygame.font.Font = pygame.font.Font(settings.FONT_NAME, settings.FONT_SIZE)
            self.image: pygame.Surface = self.font.render(self.text, False, settings.FONT_COLOR)
            self.rect: pygame.Rect = self.image.get_rect()
            self.rect.center = pos
        
        def render(self, canvas: pygame.Surface) -> None:
            canvas.blit(self.image, self.rect)


    class _Button:
        def __init__(self, 
                    text: str, 
                    fonction: Callable[[], None], 
                    font: pygame.font.Font, 
                    selected: bool = False, 
                    ) -> None:
            self.text = text
            self.fonction = fonction
            self.font = font
            self.selected = selected

            self.image: pygame.Surface = self.font.render(self.text, False, color=(0, 0, 0))
            self.rect: pygame.Rect = self.image.get_rect()


        def update(self) -> None:
            if self.selected:
                self.image = self.font.render(('>'+self.text+'<'), False, color=(50, 50, 50))
            else:
                self.image = self.font.render(self.text, False, color=(0, 0, 0))
            
            self.rect = self.image.get_rect()


        def render(self, canvas: pygame.Surface, dest: tuple[int, int]) -> None:
            canvas.blit(self.image, dest=dest)


    def __init__(self, game, background_color, transparency: bool = False) -> None:
        super().__init__(game.stack)
        self.canvas: pygame.Surface = pygame.Surface(size=(settings.WIDTH, settings.HEIGHT))
        self.game = game
        self.transparency = transparency
        self.font = pygame.font.Font('font/PixeloidSans.ttf', 50)
        self.buttons: list[Menu._Button] = []
        self.labels: list[Menu._Label] = []


        # background
        self.background: pygame.Surface = pygame.Surface(size=(settings.WIDTH, settings.HEIGHT))
        self.background.fill(background_color)
        if self.transparency is True:
            self.background.set_alpha(150)   # 0 is fully transparent, 255 is fully opaque
    

    def update(self) -> None:
                
        # move the selected/focus across buttons
        if self.game.keys['UP']:
            self.game.keys['UP'] = False
            for i in range(len(self.buttons)):
                if self.buttons[i].selected:
                    if i != len(self.buttons)-1:
                        self.buttons[i+1].selected = True
                        self.buttons[i].selected = False
                        break
                    else:
                        # uncomment these line to loop throug the buttons
                        # self.buttons[0].selected = True
                        # self.buttons[i].selected = False
                        pass
        if self.game.keys['DOWN']:
            self.game.keys['DOWN'] = False
            for i in range(len(self.buttons)):
                if self.buttons[i].selected:
                    if i != 0:
                        self.buttons[i-1].selected = True
                        self.buttons[i].selected = False
                        break
                    else:
                        # uncomment these line to loop throug the buttons (dont forgot the break it took me half an hour)
                        # self.buttons[4].selected = True
                        # self.buttons[0].selected = False
                        # break
                        pass
        if self.game.keys['RETURN']:
            self.game.keys['RETURN'] = False
            # if there is multiple buttons highlighted, the first one is called
            for button in self.buttons:
                if button.selected:
                    button.fonction()
                    break

        for button in self.buttons:
            # no need to do this every frame
            button.update()   # update every text button if highlighted or not


    def render(self) -> None:
        if self.transparency is True:
            self.canvas = self.prev_state.canvas.copy()
        else:
            self.canvas = self.game.canvas.copy()

        # blit the background
        self.canvas.blit(self.background, dest=(0, 0))


        # blit the buttons
        for i, button in enumerate(self.buttons):
            # center this shit was a pain in the ass
            x = settings.WIDTH//2 - button.rect.width//2
            y = (settings.HEIGHT//2 - (button.rect.height//2) * ((3*i)+1) ) + (len(self.buttons)//2) * (button.rect.height)
            button.render(self.canvas, (x, y))
        
        # blit the labels
        for label in self.labels:
            label.render(self.canvas)
            # self.canvas.blit(label.image, label.rect)

        self.game.canvas = self.canvas.copy()



class Mainmenu(Menu):
    def __init__(self, game) -> None:
        super().__init__(game, '#00ffff')
        self.game = game

        # init buttons
        self.buttons.append(Menu._Button('exit', self.exit_game, self.font))
        self.buttons.append(Menu._Button('play', self.play, self.font, selected=True))

        # create labels
        self.labels.append(Menu._Label('MAIN MENU', pos=(
            settings.WIDTH//2,
            settings.HEIGHT//10
        )))
  

    def exit_game(self) -> None:
        pygame.quit()
        sys.exit()
    

    def play(self) -> None:
        gameplay = Gameplay(self.game)
        gameplay.enter_state()


class Gameplay(State):
    def __init__(self, game) -> None:
        super().__init__(game.stack)
        self.game = game
        self.canvas = pygame.Surface(size=(settings.WIDTH, settings.HEIGHT))
        self.score: float = 0.0
        self.bricks_breaked = 0
        self.playtime_in_frames = 0

        # timer
        self.countdown_in_frames = settings.COUNTDOWN*settings.FPS

        # create objects
        self.balls: pygame.sprite.Group = pygame.sprite.Group()
        ball = Ball(self.game, self.balls)
        self.paddle = Paddle(self.game)
        self.bricks: pygame.sprite.Group = pygame.sprite.Group()
        self.powerups: pygame.sprite.Group = pygame.sprite.Group()

        self.setup_bricks()


    def setup_bricks(self) -> None:
        offset = 25
        gap = 5
        height = int(settings.HEIGHT*0.7)
        brick = Brick(0, 0)
        row_size = brick.rect.height+gap
        column_size = brick.rect.width+gap
        for y in range(height//row_size):
            for x in range(settings.WIDTH//column_size):
                self.bricks.add(Brick(
                    offset + (x * column_size),
                    offset + (y * row_size)
                    ))

    
    def update(self) -> None:
        # process keys press
        if self.game.keys['ESCAPE']:
            self.game.keys['ESCAPE'] = False   # prevente the pause to immediatly quit
            pause = Pause(self.game)
            pause.enter_state()
        if self.game.keys['p']:
            self.game.keys['p'] = False
            self.win()

        # countdown befor start
        if self.countdown_in_frames:
            countdown_in_seconds = self.countdown_in_frames/settings.FPS
            if countdown_in_seconds == int(countdown_in_seconds):    # basicly print 3, 2, 1, 0!
                # print(countdown_in_seconds)    # should re-use this in the UI somehow
                pass
            self.countdown_in_frames -= 1
        # main updates
        else:
            self.playtime_in_frames += 1

            self.powerups.update()
            self.paddle.update(self.powerups)
            for ball in self.balls:
                ball.update(self.paddle, self.bricks, self.powerups)
            if self.check_game_over():
                self.game_over()
            if self.check_win():
                self.win()

            # update score
            playtime = self.playtime_in_frames / settings.FPS
            self.score = (self.bricks_breaked * settings.BRICK_SCORE) - playtime
            self.score = round(self.score)


    def render(self) -> None:
        self.canvas.fill(color=settings.BACKGROUND_COLOR)
        for brick in self.bricks:
            brick.render(self.canvas)
        for powerup in self.powerups:
            powerup.render(self.canvas)
        self.paddle.render(self.canvas)
        for ball in self.balls:
            ball.render(self.canvas)

        self.game.canvas = self.canvas


    def check_win(self) -> bool:
        if len(self.bricks.sprites()) == 0:
            return True
        else:
            return False

    
    def win(self) -> None:
        win = Win(self.game)
        win.enter_state()

        # save the highscore to file if score > highscore
        if (self.score > self.game.highscore['manu']):
            self.game.highscore['manu'] = self.score
            save(round(self.score))


    def check_game_over(self) -> bool:
        if len(self.balls) <= 0:
            return True
        else:
            return False
    

    def game_over(self) -> None:
        '''append game over state to the stack and calc score based on time'''
        gameoverstate = Gameover(self.game)
        gameoverstate.enter_state()


class Gameover(Menu):
    def __init__(self, game) -> None:
        super().__init__(game, '#ff0000')
        self.game = game

        # save score
        if (self.prev_state.score > self.game.highscore['manu']):
            self.game.highscore['manu'] = self.prev_state.score
            save(self.prev_state.score)

        # create buttons
        self.buttons.append(Menu._Button('menu', self.to_menu, self.font))
        self.buttons.append(Menu._Button('replay', self.replay, self.font, selected=True))

        # create labels
        self.labels.append(Menu._Label('GAME OVER', pos=(settings.WIDTH//2, settings.HEIGHT//10)))
        self.labels.append(Menu._Label(f'score : {self.prev_state.score}', pos=(settings.WIDTH//2, (settings.HEIGHT//16)*11)))
        self.labels.append(Menu._Label(f"highscore : {self.game.highscore['manu']}", pos=(settings.WIDTH//2, (settings.HEIGHT//16)*13)))

        self.game_over_font = pygame.font.Font ('font/PixeloidSansBold.ttf', 80)
        self.score_font = pygame.font.Font('font/PixeloidMono.ttf', 50)


    def to_menu(self) -> None:
        # stack :               mainmenu > gameplay > gameover
        self.exit_state()  # back to gameplay
        self.exit_state()  # back to menu


    def replay(self) -> None:
        # stack :               mainmenu > gameplay > gameover
        self.exit_state()  # back to gameplay
        self.exit_state()  # back to menu
        gameplay = Gameplay(self.game)
        gameplay.enter_state()


class Win(Menu):
    def __init__(self, game) -> None:
        super().__init__(game, '#00ff00')

        # save score
        if (self.prev_state.score > self.game.highscore['manu']):
            self.game.highscore['manu'] = self.prev_state.score
            save(self.prev_state.score)

        # create buttons
        self.buttons.append(Menu._Button(
            text='menu', 
            fonction=self.to_menu, 
            font=self.font, 
            ))
        self.buttons.append(Menu._Button(
            text='replay', 
            fonction=self.replay, 
            font=self.font, 
            selected=True
            ))

        # create labels
        self.labels.append(Menu._Label(
            text='YOU WON !!!', 
            pos=(settings.WIDTH//2, settings.HEIGHT//16),
            ))
        self.labels.append(Menu._Label(
            text=f'score : {self.prev_state.score}', 
            pos=(settings.WIDTH//2, (settings.HEIGHT//16) * 11),
            ))
        self.labels.append(Menu._Label(
            text=f"highscore : {self.game.highscore['manu']}", 
            pos=(settings.WIDTH//2, (settings.HEIGHT//16) * 13),
            ))
        self.labels.append(Menu._Label(
            text=f"playtime : {self.prev_state.playtime_in_frames/settings.FPS:.2f}",
            pos=(settings.WIDTH//2, (settings.HEIGHT//16) * 15),
        ))


    def to_menu(self) -> None:
        self.exit_state()  # back to gameplay
        self.exit_state() # back to menu


    def replay(self) -> None:
        self.exit_state()   # back to menu
        gameplay = Gameplay(self.game)
        gameplay.enter_state()


class Pause(Menu):
    def __init__(self, game) -> None:
        super().__init__(game, settings.PAUSE_COLOR)
        
        # dont forgot to set ONE button selected
        # the first button declared here is the bottom one, the last is on top.

        # menu_button
        self.buttons.append(Menu._Button('menu', self.to_mainmenu, self.font))
        # settings_button
        self.buttons.append(Menu._Button('settings', self.to_settings, self.font))
        # resume_button
        self.buttons.append(Menu._Button('resume', self.resume, self.font, selected=True))

        # score
        self.score_text_surf: pygame.Surface = self.font.render(f'score : {self.prev_state.score}', False, color=(settings.FONT_COLOR))


    # fonctions to pass to the buttons
    def resume(self) -> None:
        # after pause restart a counter
        self.prev_state.countdown_in_frames = settings.COUNTDOWN*settings.FPS
        self.exit_state()


    def to_settings(self) -> None:
        raise NotImplementedError


    def to_mainmenu(self) -> None:
        # the stack :
        # >main>gameplay>pause
        self.exit_state()
        # >main>gameplay
        self.exit_state()
        # >main


    def update(self) -> None:
        if self.game.keys['ESCAPE']:
            self.game.keys['ESCAPE'] = False # prevent to go back in pause
            self.resume()
