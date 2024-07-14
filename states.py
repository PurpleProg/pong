import pygame
import settings
import sys  # for proper exit
import time
import json
import base64
from entitys import Ball, Paddle, Brick


def save(score: dict[str, int]) -> None:
    ''' save the highscore to file '''
    score_data = {
        'manu': score
    }
    score_json: str = json.dumps(score_data)
    encoded_json: str = base64.b64encode(score_json.encode()).decode()
    with open('highscore', 'w') as highscore:
        highscore.write(encoded_json)


class State:
    ''' Blueprint of state for the stack'''
    def __init__(self, game) -> None:
        self.game = game
        if len(self.game.stack):
            self.prev_state = self.game.stack[-1]
    
    def update(self) -> None:
        raise NotImplementedError

    def render(self) -> None:
        raise NotImplementedError
    
    def enter_state(self) -> None:
        self.game.stack.append(self)
    
    def exit_state(self) -> None:
        self.game.stack.pop()


class Mainmenu(State):
    def __init__(self, game) -> None:
        super().__init__(game)
        self.game = game
        self.canvas = pygame.Surface(size=(settings.WIDTH, settings.HEIGHT))
        self.canvas.fill((0, 255, 255))   # yellow (i hope)  fuck it cyan works too

        # init buttons
        self.buttons: list[Button] = list()
        exit_button = Button(self.game, self, 'exit', self.buttons, self.exit_game)
        play_button = Button(self.game, self, 'play', self.buttons, self.play, highlight=True)

        # init font
        big_menu_font = pygame.font.Font('font/PixeloidSansBold.ttf', 80)
        self.menu_text_surface = big_menu_font.render('MAIN MENU', False, color=('#000000'))
  

    def exit_game(self) -> None:
        pygame.quit()
        sys.exit()
    

    def play(self) -> None:
        gameplay = Gameplay(self.game)
        gameplay.enter_state()

    
    def update(self) -> None:
        if self.game.keys['UP']:
            self.game.keys['UP'] = False
            for i in range(len(self.buttons)):
                if self.buttons[i].highlight:
                    if i != len(self.buttons)-1:
                        self.buttons[i+1].highlight = True
                        self.buttons[i].highlight = False
                        break
                    else:
                        # uncomment these line to loop throug the buttons
                        # self.buttons[0].highlight = True
                        # self.buttons[i].highlight = False
                        pass
        if self.game.keys['DOWN']:
            self.game.keys['DOWN'] = False
            for i in range(len(self.buttons)):
                if self.buttons[i].highlight:
                    if i != 0:
                        self.buttons[i-1].highlight = True
                        self.buttons[i].highlight = False
                        break
                    else:
                        # uncomment these line to loop throug the buttons (dont forgot the break it took me half an hour)
                        # self.buttons[4].highlight = True
                        # self.buttons[0].highlight = False
                        # break
                        pass
        if self.game.keys['RETURN']:
            self.game.keys['RETURN'] = False
            # if there is multiple buttons highlighted, they are all called. That should'nt append but who knows
            for button in self.buttons:
                if button.highlight:
                    button.fonction()
                    break

        for button in self.buttons:
            button.update()   # update every text button if highlighted or not


    def render(self) -> None:
        self.canvas.fill('#00ffff')

        # blit the MAIN MENU text
        self.canvas.blit(self.menu_text_surface, dest=(
            int(settings.WIDTH/2 - self.menu_text_surface.get_rect().width/2), 
            int(settings.HEIGHT/10)
        ))

        for i, button in enumerate(self.buttons):
            # center this shit is a pain in the ass
            x = int(settings.WIDTH/2 - button.rect.width/2)   # center button in X axis
            y = int((settings.HEIGHT/2 - (button.rect.height/2) * ((3*i)+1) ) + (len(self.buttons)/2) * (button.rect.height))
            button.render(x, y)
        
        self.game.canvas = self.canvas


class Gameplay(State):
    def __init__(self, game) -> None:
        super().__init__(game)
        self.game = game
        self.canvas = pygame.Surface(size=(settings.WIDTH, settings.HEIGHT))
        self.score: float = 0.0
        self.bricks_breaked = 0
        self.playtime_in_frames = 0

        # timer
        self.countdown_in_frames = settings.COUNTDOWN*settings.FPS

        # create objects
        self.ball = Ball(self.game)
        self.paddle = Paddle()
        self.bricks: pygame.sprite.Group = pygame.sprite.Group()
        # setup bricks
        gap = 5
        for y in range(16):
            for x in range(14):
                self.bricks.add(Brick(
                    25 + gap*x + x*settings.BRICK_WIDTH, 
                    10 + gap*y + y*settings.BRICK_HEIGHT
                    ))

    
    def update(self) -> None:

        self.playtime_in_frames += 1

        # process keys press
        if self.game.keys['ESCAPE']:
            self.game.keys['ESCAPE'] = False   # prevente the pause to immediatly quit
            pause = Pause(self.game)
            pause.enter_state()   

        # countdown befor start
        if self.countdown_in_frames:
            countdown_in_seconds = self.countdown_in_frames/settings.FPS
            if countdown_in_seconds == int(countdown_in_seconds):    # basicly print 3, 2, 1, 0!
                print(countdown_in_seconds)    # should re-use this in the UI somehow
            self.countdown_in_frames -= 1
        else:
            # main update thing whatever blablabla
            self.paddle.update(self.game.keys)
            self.ball.update(self.paddle, self.bricks)
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
        self.paddle.render(self.canvas)
        self.ball.render()

        self.game.canvas = self.canvas


    def check_win(self) -> bool:
        if len(self.bricks.sprites()) == 0:
            return True
        else:
            return False

    
    def win(self) -> None:
        win = Win(self.game)
        win.enter_state()


    def check_game_over(self) -> bool:
        ''' check the ball pos '''
        if self.ball.pos.y > settings.HEIGHT:
            return True
        else:
            return False
    

    def game_over(self) -> None:
        '''append game over state to the stack and calc score based on time'''
        gameoverstate = Gameover(self.game)
        gameoverstate.enter_state()


class Gameover(State):
    def __init__(self, game) -> None:
        super().__init__(game)
        self.canvas = pygame.Surface(size=(settings.WIDTH, settings.HEIGHT))
        self.canvas.fill((255, 0, 0))

        if (self.prev_state.score > self.game.highscore['manu']):
            save(self.prev_state.score)

        # setup buttons
        self.buttons: list = []
        menu = Button(self.game, self, 'menu', self.buttons, self.to_menu)
        replay = Button(self.game, self, 'replay', self.buttons, self.replay, highlight=True)

        # setup font
        self.game_over_font = pygame.font.Font ('font/PixeloidSansBold.ttf', 80)
        self.game_over_text_surf = self.game_over_font.render('GAME OVER', False, color=('#000000'))
        self.score_font = pygame.font.Font('font/PixeloidMono.ttf', 50)

        self.score_text_surf = self.score_font.render(f'score : {self.prev_state.score}', False, color=('#000000'))


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


    def update(self) -> None:
        if self.game.keys['ESCAPE']:
            # if the escape key make the stack beeing used twice in a frame
            # for exemple here from menu > gameplay > gameover
            #                    to menu > gameplay > pause
            # as it skips   menu > gameplay
            # it unsync the stack and just breaks everything.
            self.game.keys['ESCAPE'] = False
            self.replay()
        
        if self.game.keys['UP']:
            self.game.keys['UP'] = False
            for i in range(len(self.buttons)):
                if self.buttons[i].highlight:
                    if i != len(self.buttons)-1:
                        self.buttons[i+1].highlight = True
                        self.buttons[i].highlight = False
                        break
                    else:
                        # uncomment these line to loop throug the buttons
                        # self.buttons[0].highlight = True
                        # self.buttons[i].highlight = False
                        pass
        if self.game.keys['DOWN']:
            self.game.keys['DOWN'] = False
            for i in range(len(self.buttons)):
                if self.buttons[i].highlight:
                    if i != 0:
                        self.buttons[i-1].highlight = True
                        self.buttons[i].highlight = False
                        break
                    else:
                        # uncomment these line to loop throug the buttons (dont forgot the break it took me half an hour)
                        # self.buttons[4].highlight = True
                        # self.buttons[0].highlight = False
                        # break
                        pass
        if self.game.keys['RETURN']:
            self.game.keys['RETURN'] = False
            # if there is multiple buttons highlighted, they are all called. That should'nt append but who knows
            for button in self.buttons:
                if button.highlight:
                    button.fonction()
                    break

        for button in self.buttons:
            button.update()   # update every text button if highlighted or not

    
    def render(self) -> None:

        self.canvas = self.prev_state.canvas.copy()   # last state's canvas

        self.transparency: pygame.Surface = pygame.Surface(size=(settings.WIDTH, settings.HEIGHT))
        self.transparency.fill(("#ff0000"))
        self.transparency.set_alpha(150)   # 0 is fully transparent, 255 is fully opaque
        self.canvas.blit(self.transparency, dest=(0, 0))

        # blit the game over text
        self.canvas.blit(self.game_over_text_surf, dest=(
            settings.WIDTH/2 - self.game_over_text_surf.get_rect().width/2, 
            settings.HEIGHT/10
        ))
        # blit the buttons
        for i, button in enumerate(self.buttons):
            # center this shit is a pain in the ass
            x = settings.WIDTH/2 - button.rect.width/2   # center button in X axis
            y = (settings.HEIGHT/2 - (button.rect.height/2) * ((3*i)+1) ) + (len(self.buttons)/2) * (button.rect.height)
            button.render(x, y)
        # blit the score
        self.canvas.blit(self.score_text_surf, dest=(
            settings.WIDTH/2 - self.score_text_surf.get_rect().width/2, 
            settings.HEIGHT-(2 * settings.HEIGHT/10)
        ))

        self.game.canvas = self.canvas


class Win(State):
    def __init__(self, game) -> None:
        super().__init__(game)
        self.canvas = pygame.Surface(size=(settings.WIDTH, settings.HEIGHT))
        self.canvas.fill((255, 0, 0))

        if self.prev_state.score > self.game.highscore['manu']:
            save(self.prev_state.score)

        # setup buttons
        self.buttons: list = []
        menu = Button(self.game, self, 'menu', self.buttons, self.to_menu)
        replay = Button(self.game, self, 'replay', self.buttons, self.replay, highlight=True)

        # setup font
        win_font = pygame.font.Font('font/PixeloidSansBold.ttf', 80)
        self.score_win_font = pygame.font.Font('font/PixeloidSans.ttf', 50)
        self.win_text_surface = win_font.render('YOU WON !!!', False, color=('#000000'))

        self.score_text_surf = self.score_win_font.render(f'score : {self.prev_state.score}', False, color=('#000000'))


    def to_menu(self) -> None:
        self.exit_state()  # back to gameplay
        self.exit_state() # back to menu


    def replay(self) -> None:
        self.exit_state()   # back to menu
        gameplay = Gameplay(self.game)
        gameplay.enter_state()


    def update(self) -> None:

        # this makes it act like a pause
        # if self.game.keys['ESCAPE']:
        #     self.game.keys['ESCAPE'] = False
        #     self.exit_state()
        
        if self.game.keys['UP']:
            self.game.keys['UP'] = False
            for i in range(len(self.buttons)):
                if self.buttons[i].highlight:
                    if i != len(self.buttons)-1:
                        self.buttons[i+1].highlight = True
                        self.buttons[i].highlight = False
                        break
                    else:
                        # uncomment these line to loop throug the buttons
                        # self.buttons[0].highlight = True
                        # self.buttons[i].highlight = False
                        pass
        if self.game.keys['DOWN']:
            self.game.keys['DOWN'] = False
            for i in range(len(self.buttons)):
                if self.buttons[i].highlight:
                    if i != 0:
                        self.buttons[i-1].highlight = True
                        self.buttons[i].highlight = False
                        break
                    else:
                        # uncomment these line to loop throug the buttons (dont forgot the break it took me half an hour)
                        # self.buttons[4].highlight = True
                        # self.buttons[0].highlight = False
                        # break
                        pass
        if self.game.keys['RETURN']:
            self.game.keys['RETURN'] = False
            # if there is multiple buttons highlighted, they are all called. That should'nt append but who knows
            for button in self.buttons:
                if button.highlight:
                    button.fonction()
                    break

        for button in self.buttons:
            button.update()   # update every text button if highlighted or not

    
    def render(self) -> None:
        self.canvas = self.prev_state.canvas.copy()   # last state's canvas

        self.transparency: pygame.Surface = pygame.Surface(size=(settings.WIDTH, settings.HEIGHT))
        self.transparency.fill(("#00ff00"))
        self.transparency.set_alpha(150)   # 0 is fully transparent, 255 is fully opaque
        self.canvas.blit(self.transparency, dest=(0, 0))

        # blit the win !!! text
        self.canvas.blit(self.win_text_surface, dest=(
            settings.WIDTH/2 - self.win_text_surface.get_rect().width/2, 
            settings.HEIGHT/10
        ))
        # blit the buttons
        for i, button in enumerate(self.buttons):
            # center this shit is a pain in the ass
            x = settings.WIDTH/2 - button.rect.width/2   # center button in X axis
            y = (settings.HEIGHT/2 - (button.rect.height/2) * ((3*i)+1) ) + (len(self.buttons)/2) * (button.rect.height)
            button.render(x, y)
        # blit the score
        self.canvas.blit(self.score_text_surf, dest=(
            settings.WIDTH/2 - self.score_text_surf.get_rect().width/2, 
            settings.HEIGHT-(2 * settings.HEIGHT/10)
        ))

        self.game.canvas = self.canvas


class Pause(State):
    def __init__(self, game) -> None:
        super().__init__(game)
        self.canvas = pygame.Surface(size=(settings.WIDTH, settings.HEIGHT))
        self.canvas.fill(settings.PAUSE_COLOR)

        # background
        self.transparency: pygame.Surface = pygame.Surface(size=(settings.WIDTH, settings.HEIGHT))
        self.transparency.fill(settings.PAUSE_COLOR)
        self.transparency.set_alpha(150)   # 0 is fully transparent, 255 is fully opaque
        
        # init buttons
        self.buttons: list[Button] = []
        # dont forgot to set ONE button highlight
        # the first button declared here is the bottom one, the last is on top.
        menu_button = Button(self.game, self, 'menu', self.buttons, self.to_mainmenu)
        settings_button = Button(self.game, self, 'settings', self.buttons, self.to_settings)
        return_button = Button(self.game, self, 'resume', self.buttons, self.resume, highlight=True)

        # score
        self.score_font = pygame.font.Font('font/PixeloidSans.ttf', 50)
        self.score_text_surf = self.score_font.render(f'score : {self.prev_state.score}', False, color=('#000000'))


    # fonctions to pass to the buttons
    def resume(self) -> None:
        self.prev_state.countdown_in_frames = settings.COUNTDOWN*settings.FPS
        self.exit_state()


    def to_mainmenu(self) -> None:
        self.exit_state()
        self.exit_state()
    

    def to_settings(self) -> None:
        raise NotImplementedError

    
    def update(self) -> None:
        if self.game.keys['ESCAPE']:
            self.game.keys['ESCAPE'] = False # prevent to go back in pause
            self.resume()
        
        if self.game.keys['UP']:
            self.game.keys['UP'] = False
            for i in range(len(self.buttons)):
                if self.buttons[i].highlight:
                    if i != len(self.buttons)-1:
                        self.buttons[i+1].highlight = True
                        self.buttons[i].highlight = False
                        break
                    else:
                        # uncomment these line to loop throug the buttons
                        # self.buttons[0].highlight = True
                        # self.buttons[i].highlight = False
                        pass
        if self.game.keys['DOWN']:
            self.game.keys['DOWN'] = False
            for i in range(len(self.buttons)):
                if self.buttons[i].highlight:
                    if i != 0:
                        self.buttons[i-1].highlight = True
                        self.buttons[i].highlight = False
                        break
                    else:
                        # uncomment these line to loop throug the buttons (dont forgot the break it took me half an hour)
                        # self.buttons[4].highlight = True
                        # self.buttons[0].highlight = False
                        # break
                        pass
        if self.game.keys['RETURN']:
            self.game.keys['RETURN'] = False
            # if there is multiple buttons highlighted, they are all called. That should'nt append but who knows
            for button in self.buttons:
                if button.highlight:
                    button.fonction()
                    break

        for button in self.buttons:
            button.update()   # update every text button if highlighted or not


    def render(self) -> None:

        self.canvas = self.prev_state.canvas.copy()   # last state's canvas

        # blit the transparent background
        self.canvas.blit(self.transparency, dest=(0, 0))

        # blit the buttons
        for i, button in enumerate(self.buttons):
            # center this shit is a pain in the ass
            x = int(settings.WIDTH/2 - button.rect.width/2)   # center button in X axis
            y = int((settings.HEIGHT/2 - (button.rect.height/2) * ((3*i)+1) ) + (len(self.buttons)/2) * (button.rect.height))
            button.render(x, y)
        
        # blit the score
        self.canvas.blit(self.score_text_surf, dest=(
            settings.WIDTH/2 - self.score_text_surf.get_rect().width/2, 
            settings.HEIGHT-(2 * settings.HEIGHT/10)
        ))

        self.game.canvas = self.canvas


class Button(pygame.sprite.Sprite):
    def __init__(self, game, state, text: str, group: list, fonction, highlight: bool=False) -> None:
        ''' render on the given state '''
        super().__init__()
        group.append(self)
        self.game = game
        self.state = state
        self.text = text
        self.highlight: bool = highlight
        self.image: pygame.Surface = self.game.font.render(self.text, False, color=(0, 0, 0))
        self.rect: pygame.Rect = self.image.get_rect()
        self.fonction = fonction
    

    def update(self) -> None:
        if self.highlight:
            self.image = self.game.font.render(('>'+self.text+'<'), False, color=(50, 50, 50))
        else:
            self.image = self.game.font.render(self.text, False, color=(0, 0, 0))
        self.rect = self.image.get_rect()


    def render(self, pos_x: int, pos_y: int) -> None:
        self.state.canvas.blit(self.image, dest=(pos_x, pos_y))
