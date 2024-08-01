import sys
import json
import base64
from typing import Callable
from abc import abstractmethod, ABC
import pygame
from entitys import Ball, Paddle, Brick
import settings


def save(score: int) -> None:
    ''' save the highscore to file '''
    score_data = {
        'manu': score
    }
    score_json: str = json.dumps(score_data)
    encoded_json: str = base64.b64encode(score_json.encode()).decode()
    with open('highscore', 'w') as highscore:
        highscore.write(encoded_json)


class Menu(ABC):
    ''' Parent class of all menus, handel buttons and labels rendering. 
    The first button declared is the bottom one. 
    Exactly one button shall be set selected. 
    The labels can be placed anywhere '''

    class Label(pygame.sprite.Sprite):
        def __init__(self, text: str, font: pygame.font.Font, pos: tuple[int, int]) -> None:
            self.text: str = text
            self.font = font
            self.image: pygame.Surface = self.font.render(self.text, False, settings.FONT_COLOR)
            self.rect: pygame.Rect = self.image.get_rect()
            self.rect.center = pos
        
        def render(self, canvas: pygame.Surface) -> None:
            canvas.blit(self.image, self.rect)

    class Button:
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

    def __init__(self, game, background_color: settings.Color, is_transparent: bool = False) -> None:
        self.canvas: pygame.Surface = pygame.Surface(size=(settings.WIDTH, settings.HEIGHT))
        self.game = game
        self.is_transparent = is_transparent
        self.font = pygame.font.Font('font/PixeloidSans.ttf', 30)
        self.bold_font = pygame.font.Font('font/PixeloidSansBold.ttf', 35)
        self.big_font = pygame.font.Font('font/PixeloidSansBold.ttf', 80)

        # create buttons and labels list for each child
        self.buttons: list[Menu.Button] = []
        self.labels: list[Menu.Label] = []

        # background
        self.background: pygame.Surface = pygame.Surface(size=(settings.WIDTH, settings.HEIGHT))
        self.background.fill(background_color)
        if self.is_transparent:
            self.background.set_alpha(150)   # 0 is fully transparent, 255 is fully opaque

    def go_back(self) -> None:
        ''' just pop the stack ''' 
        self.game.stack.pop()

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

    def render(self, canvas: pygame.Surface) -> None:
        if self.is_transparent is True:
            self.canvas = self.game.stack[-2].canvas.copy()
        else:
            self.canvas = pygame.Surface(size=(settings.WIDTH, settings.HEIGHT))

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

        canvas.blit(self.canvas, dest=(0, 0))


class Mainmenu(Menu):
    def __init__(self, game) -> None:
        super().__init__(game, settings.MAINMENU_BACKGROUND_COLOR)
        self.game = game

        # enter state
        self.game.stack.append(self)

        # init buttons
        self.buttons.append(Menu.Button(
            text='exit', 
            fonction=self.exit_game, 
            font=self.font
        ))  # exit
        self.buttons.append(Menu.Button(
            text='settings', 
            fonction=self.to_settings, 
            font=self.font, 
        ))  # settings
        self.buttons.append(Menu.Button(
            text='difficulties', 
            fonction=self.to_difficulties_choice, 
            font=self.font, 
        ))  # difficulties
        self.buttons.append(Menu.Button(
            text='play', 
            fonction=self.play, 
            font=self.font, 
            selected=True
        ))  # play

        # create labels
        self.labels.append(Menu.Label(
            text='MAIN MENU', 
            font=self.big_font, 
            pos=(settings.WIDTH//2, settings.HEIGHT//10), 
        ))  # main menu
  
    def exit_game(self) -> None:
        pygame.quit()
        sys.exit()
    
    def to_difficulties_choice(self) -> None:
        Difficulties(self.game)
    
    def to_settings(self) -> None:
        Settings(self.game)

    def play(self) -> None:
        gameplay = Gameplay(self.game)


class Gameplay():
    def __init__(self, game) -> None:
        self.game = game
        
        # add itself to the stack
        self.game.stack.append(self)

        self.canvas = pygame.Surface(size=(settings.WIDTH, settings.HEIGHT))
        self.score: float = 0.0
        self.bricks_breaked = 0
        self.playtime_in_frames = 0

        # timer
        self.countdown_in_frames = settings.COUNTDOWN*settings.FPS

        # create objects
        self.balls: pygame.sprite.Group = pygame.sprite.Group()
        self.balls.add(Ball(
            game=self.game, 
            gameplay=self, 
            pos=pygame.Vector2(settings.WIDTH//2, settings.HEIGHT - settings.HEIGHT//8)
        ))
        self.paddle = Paddle(self.game)
        self.powerups: pygame.sprite.Group = pygame.sprite.Group()

        self.setup_bricks()

    def setup_bricks(self) -> None:
        self.bricks: pygame.sprite.Group = pygame.sprite.Group()
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
            # check win and lose
            if not self.bricks.sprites():
                Win(self.game)   # no return
            if not self.balls.sprites():
                Gameover(self.game)  # no return
            
        # process keys press
        if self.game.keys['ESCAPE']:
            self.game.keys['ESCAPE'] = False   # prevente the pause to immediatly quit
            Pause(self.game)
        if self.game.keys['p']:
            self.game.keys['p'] = False
            Win(self.game)


            # update score
            playtime = self.playtime_in_frames / settings.FPS
            self.score = (self.bricks_breaked * settings.BRICK_SCORE) - playtime
            self.score = round(self.score)

    def render(self, canvas: pygame.Surface) -> None:
        self.canvas.fill(color=settings.BACKGROUND_COLOR)
        for brick in self.bricks:
            brick.render(self.canvas)
        for powerup in self.powerups:
            powerup.render(self.canvas)
        self.paddle.render(self.canvas)
        for ball in self.balls:
            ball.render(self.canvas)

        canvas.blit(self.canvas, dest=(0, 0))


class Gameover(Menu):
    def __init__(self, game) -> None:
        super().__init__(game, settings.GAMEOVER_BACKGROUND_COLOR)
        # append itself to the stack
        self.game.stack.append(self)

        # save score
        if (self.game.stack[-2].score > self.game.highscore['manu']):
            self.game.highscore['manu'] = self.game.stack[-2].score
            save(self.game.stack[-2].score)

        # create buttons
        self.buttons.append(Menu.Button(
            text='menu', 
            fonction=self.to_menu, 
            font=self.font
        ))  # menu
        self.buttons.append(Menu.Button(
            text='replay', 
            fonction=self.replay, 
            font=self.font, 
            selected=True
        ))  # replay

        # create labels
        self.labels.append(Menu.Label(
            text='GAME OVER', 
            font=self.big_font, 
            pos=(settings.WIDTH//2, settings.HEIGHT//10)
        ))  # GAME OVER
        self.labels.append(Menu.Label(
            text=f'score : {self.game.stack[-2].score}', 
            font=self.bold_font, 
            pos=(settings.WIDTH//2, (settings.HEIGHT//16)*11)
        ))  # score : 99
        self.labels.append(Menu.Label(
            text=f"highscore : {self.game.highscore['manu']}", 
            font=self.bold_font, 
            pos=(settings.WIDTH//2, (settings.HEIGHT//16)*13)
        ))  # highscore : 9999

    def to_menu(self) -> None:
        # stack :               mainmenu > gameplay > gameover
        self.game.stack.pop()  # back to gameplay
        self.game.stack.pop()  # back to menu

    def replay(self) -> None:
        # stack :               mainmenu > gameplay > gameover
        self.game.stack.pop()  # back to gameplay
        self.game.stack.pop()  # back to menu
        Gameplay(self.game)


class Win(Menu):
    def __init__(self, game) -> None:
        super().__init__(game, settings.WIN_BACKGROUND_COLOR)

        # append itself to the stack
        game.stack.append(self)

        # save score
        if (self.game.stack[-2].score > self.game.highscore['manu']):
            self.game.highscore['manu'] = self.game.stack[-2].score
            save(self.game.stack[-2].score)

        # create buttons
        self.buttons.append(Menu.Button(
            text='menu', 
            fonction=self.to_menu, 
            font=self.font, 
        ))  # menu
        self.buttons.append(Menu.Button(
            text='replay', 
            fonction=self.replay, 
            font=self.font, 
            selected=True
        ))  # replay

        # create labels
        self.labels.append(Menu.Label(
            text='YOU WON !!!', 
            font=self.big_font, 
            pos=(settings.WIDTH//2, settings.HEIGHT//10),
        ))  # YOU WON
        self.labels.append(Menu.Label(
            text=f'score : {self.game.stack[-2].score}', 
            font=self.bold_font, 
            pos=(settings.WIDTH//2, (settings.HEIGHT//16) * 11),
        ))  # score : 090
        self.labels.append(Menu.Label(
            text=f"highscore : {self.game.highscore['manu']}", 
            font=self.bold_font, 
            pos=(settings.WIDTH//2, (settings.HEIGHT//16) * 13),
        ))  # highscore
        self.labels.append(Menu.Label(
            text=f"playtime : {self.game.stack[-2].playtime_in_frames/settings.FPS:.2f}",
            font=self.bold_font, 
            pos=(settings.WIDTH//2, int(settings.HEIGHT * (16 / 15))),
        ))  # playtime

    def to_menu(self) -> None:
        self.game.stack.pop()  # back to gameplay
        self.game.stack.pop() # back to menu

    def replay(self) -> None:
        self.game.stack.pop()   # back to menu
        Gameplay(self.game)


class Pause(Menu):
    def __init__(self, game) -> None:
        super().__init__(game, settings.PAUSE_BACKGROUND_COLOR, is_transparent=True)

        # append itself to the stack
        self.game.stack.append(self)
        
        self.buttons.append(Menu.Button(
            text='menu', 
            fonction=self.to_mainmenu, 
            font=self.font
        ))  # menu
        # self.buttons.append(Menu.Button(
        #     text='settings', 
        #     fonction=self.to_settings, 
        #     font=self.font
        # ))  # settings
        self.buttons.append(Menu.Button(
            text='resume', 
            fonction=self.resume, 
            font=self.font, 
            selected=True
        ))  # resume

        # labels
        self.labels.append(Menu.Label(
            text='Settings', 
            font=self.big_font, 
            pos=(settings.WIDTH//2, settings.HEIGHT//10)
        ))  # settings
        self.labels.append(Menu.Label(
            text=f'score : {self.game.stack[-2].score}', 
            font=self.bold_font, 
            pos=(settings.WIDTH//2, int(settings.HEIGHT*0.8))
        ))  # score : 999

    def resume(self) -> None:
        # after pause restart a counter
        self.game.stack[-2].countdown_in_frames = settings.COUNTDOWN*settings.FPS
        self.game.stack.pop()

    # def to_settings(self) -> None:
    #     Settings(self.game)

    def to_mainmenu(self) -> None:
        # the stack :
        # >main>gameplay>pause
        self.game.stack.pop()
        # >main>gameplay
        self.game.stack.pop()
        # >main


class Settings(Menu):
    def __init__(self, game) -> None:
        super().__init__(game, settings.SETTINGS_BACKGROUND_COLOR, is_transparent=False)
        
        self.game = game

        # append itself to the stack
        self.game.stack.append(self)

        # create buttons
        self.buttons.append(Menu.Button(
            text='Back', 
            fonction=self.go_back, 
            font=self.font, 
        ))  # back
        self.buttons.append(Menu.Button(
            text='sound', 
            fonction=self.to_sound_settings,
            font=self.font,
        ))  # sound
        self.buttons.append(Menu.Button(
            text='resolution', 
            fonction=self.to_resolution_settings, 
            font=self.font, 
            selected=True, 
        ))  # resolution

        # Title
        self.labels.append(Menu.Label(
            text='Settings', 
            font=self.big_font, 
            pos=(settings.WIDTH//2, settings.HEIGHT//10)
        ))  # settings Title

    def to_sound_settings(self) -> None:
        print('Comming Soon !')

    def to_resolution_settings(self) -> None:
        Resolution(self.game)


class Difficulties(Menu):
    def __init__(self, game) -> None:
        super().__init__(game, background_color=settings.SETTINGS_BACKGROUND_COLOR)
        self.game = game
        self.game.stack.append(self)

        # buttons
        self.buttons.extend([
            Menu.Button(
                text='Back', 
                fonction=self.go_back, 
                font=self.font,
            ),  # back
            Menu.Button(
                text='hard', 
                fonction=self.hard, 
                font=self.font
            ),  # hard
            Menu.Button(
                text='Normal', 
                fonction=self.normal, 
                font=self.font, 
                selected=True
            ),  # normal
            Menu.Button(
                text='Easy', 
                fonction=self.easy, 
                font=self.font
            ),  # easy
        ])
    
    def hard(self) -> None:
        settings.BALL_SPEED = 6
        settings.PADDLE_SPEED = 7
        settings.POWERUP_SPEED = 5
        settings.POWERUP_BIG_PADLLE_DURATION = 5
        settings.BALL_MULTIPLYER = 1
        settings.MAX_BOUNCE_ANGLE = 120
        settings.POWERUP_PADDLE_CHANCE = 7
        settings.POWERUP_BALL_CHANCE = 3
        settings.POWERUP_PADDLE_SIZE = 1.1
        self.go_back()
    
    def normal(self) -> None:
        settings.BALL_SPEED = 5
        settings.PADDLE_SPEED = 8
        settings.POWERUP_SPEED = 2
        settings.POWERUP_BIG_PADLLE_DURATION = 10
        settings.BALL_MULTIPLYER = 2
        settings.MAX_BOUNCE_ANGLE = 60
        settings.POWERUP_PADDLE_CHANCE = 10
        settings.POWERUP_BALL_CHANCE = 10
        settings.POWERUP_PADDLE_SIZE = 1.2
        self.go_back()
    
    def easy(self) -> None:
        settings.BALL_SPEED = 4
        settings.PADDLE_SPEED = 8
        settings.POWERUP_SPEED = 1
        settings.POWERUP_BIG_PADLLE_DURATION = 15
        settings.BALL_MULTIPLYER = 3
        settings.MAX_BOUNCE_ANGLE = 45
        settings.POWERUP_PADDLE_CHANCE = 25
        settings.POWERUP_BALL_CHANCE = 15
        settings.POWERUP_PADDLE_SIZE = 1.4
        self.go_back()


class Resolution(Menu):
    def __init__(self, game) -> None:
        super().__init__(game, background_color=settings.SETTINGS_BACKGROUND_COLOR)
        self.game = game
        self.game.stack.append(self)

        # buttons
        self.buttons.append(Menu.Button(
            text='Back', 
            fonction=self.go_back, 
            font=self.font
        ))
        self.buttons.append(Menu.Button(
            text='512x256', 
            fonction=self.res_512x256, 
            font=self.font,
        ))  # 512x256
        self.buttons.append(Menu.Button(
            text='1024x512', 
            fonction=self.res_1024x512, 
            font=self.font,
        ))  # 1024x512
        self.buttons.append(Menu.Button(
            text='Toggle fullscreen', 
            fonction=self.toggle_fullscreen, 
            font=self.font, 
            selected=True
        ))  # fullscreen

        # label
        self.labels.append(Menu.Label(
            text='Resolutions', 
            font=self.big_font, 
            pos=(settings.WIDTH//2, settings.HEIGHT//10)
        ))  # resolution title

    def toggle_fullscreen(self) -> None:
        if self.game.fullscreen:
            self.game.display = pygame.display.set_mode(size=(settings.WIDTH_BACKUP, settings.HEIGHT_BACKUP))
            settings.WIDTH, settings.HEIGHT = settings.WIDTH_BACKUP, settings.HEIGHT_BACKUP
            self.game.fullscreen = False
        else:
            self.game.display = pygame.display.set_mode(size=(0, 0), flags=pygame.FULLSCREEN)
            settings.WIDTH, settings.HEIGHT = self.game.display.get_size()
            self.game.fullscreen = True
        
        self.reload_stack()
        
    def res_512x256(self) -> None:
        self.game.display = pygame.display.set_mode(size=(512, 256))
        settings.WIDTH, settings.HEIGHT = 512, 256
        self.reload_stack()

    def res_1024x512(self) -> None:
        self.game.display = pygame.display.set_mode(size=(1024, 512))
        settings.WIDTH, settings.HEIGHT = 1024, 512
        self.reload_stack()

    def reload_stack(self) -> None:
        ''' empty the stack and recreate every items '''
        #  >mainmenu>settings>resolution
        self.game.stack.pop()
        self.game.stack.pop()
        self.game.stack.pop()
        Mainmenu(self.game)
        Settings(self.game)        
        Resolution(self.game)
