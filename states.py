import pygame
import settings
import sys  # for proper exit
from entitys import Ball, Paddle, Brick


class State:
    ''' Blueprint of state for the stack'''
    def __init__(self, game) -> None:
        self.game = game
    
    def update(self) -> None:
        raise NotImplementedError

    def render(self) -> None:
        raise NotImplementedError
    
    def enter_state(self) -> None:
        self.game.stack.append(self)
    
    def exit_state(self) -> None:
        self.game.stack.pop()


class Mainmenu(State):
    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.canvas = pygame.Surface(size=(settings.WIDTH, settings.HEIGHT))
        self.canvas.fill((0, 255, 255))   # yellow (i hope)  fuck it cyan works too

        # init buttons
        self.buttons: list = []
        exit_button = Button(self.game, 'exit', self.buttons, self.exit_game)
        play_button = Button(self.game, 'play', self.buttons, self.play, highlight=True)
    

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

        for i, button in enumerate(self.buttons):
            # center this shit is a pain in the ass
            x = settings.WIDTH/2 - button.rect.width/2   # center button in X axis
            y = (settings.HEIGHT/2 - (button.rect.height/2) * ((3*i)+1) ) + (len(self.buttons)/2) * (button.rect.height)
            button.render(x, y)
        
        self.game.canvas = self.canvas


class Gameplay(State):
    def __init__(self, game) -> None:
        super().__init__(game)
        self.game = game
        self.canvas = pygame.Surface(size=(settings.WIDTH, settings.HEIGHT))

        # timer
        self.countdown = settings.COUNTDOWN*settings.FPS   # 3 seconds

        # create objects
        self.ball = Ball()
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

        # process keys press
        if self.game.keys['ESCAPE']:
            self.game.keys['ESCAPE'] = False   # prevente the pause to immediatly quit
            pause = Pause(self.game)
            pause.enter_state()

        if self.countdown > 0:
            self.countdown -= 1
            countdown_in_seconds = self.countdown/settings.FPS
            if countdown_in_seconds == int(countdown_in_seconds):    # basicly print 3, 2, 1, 0!
                print(countdown_in_seconds)    # should re-use this in the UI somehow
        else:
            self.paddle.update(self.game.keys)
            self.ball.update(self.paddle, self.bricks)
            if self.check_game_over():
                self.game_over()
    

    def render(self) -> None:
        self.canvas.fill(color=settings.BACKGROUND_COLOR)
        for brick in self.bricks:
            brick.render(self.canvas)
        self.paddle.render(self.canvas)
        self.ball.render(self.canvas)

        self.game.canvas = self.canvas

    
    def check_game_over(self) -> bool:
        ''' check the ball pos '''
        if self.ball.pos.y > settings.HEIGHT:
            return True
        else:
            return False
    

    def game_over(self) -> None:
        '''remove current state from stack and immedialty add a gameover instead'''
        self.exit_state()
        gameoverstate = Gameover(self.game)
        gameoverstate.enter_state()


class Gameover(State):
    def __init__(self, game) -> None:
        super().__init__(game)
        self.canvas = pygame.Surface(size=(settings.WIDTH, settings.HEIGHT))
        self.canvas.fill((255, 0, 0))

        # setup buttons
        self.buttons: list = []
        menu = Button(self.game, 'menu', self.buttons, self.to_menu)
        replay = Button(self.game, 'replay', self.buttons, self.replay, highlight=True)

        # setup font
        big_game_over_font = pygame.font.Font('font/PixeloidSansBold.ttf', 80)
        self.game_over_text_surf = big_game_over_font.render('GAME OVER', False, color=('#000000'))
        


    def to_menu(self) -> None:
        self.exit_state()  # back to menu


    def replay(self) -> None:
        self.exit_state()   # back to menu
        gameplay = Gameplay(self.game)
        gameplay.enter_state()


    def update(self) -> None:
        if self.game.keys['ESCAPE']:
            self.exit_state()
        
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
        self.canvas.fill(("#ff0000"))

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

        self.game.canvas = self.canvas


class Pause(State):
    def __init__(self, game) -> None:
        super().__init__(game)
        self.canvas = pygame.Surface(size=(settings.WIDTH, settings.HEIGHT))
        self.canvas.fill(settings.PAUSE_COLOR)

        # init buttons
        self.buttons: list[Button] = []
        # dont forgot to set ONE button highlight
        # the first button declared here is the bottom one, the last is on top.
        menu_button = Button(self.game, 'menu', self.buttons, self.to_mainmenu)
        settings_button = Button(self.game, 'settings', self.buttons, self.to_settings)
        return_button = Button(self.game, 'return to game', self.buttons, self.exit_state, highlight=True)
    

    # fonctions to pass to the buttons
    def to_mainmenu(self) -> None:
        self.exit_state()
        self.exit_state()
    

    def to_settings(self) -> None:
        raise NotImplementedError

    
    def update(self) -> None:
        if self.game.keys['ESCAPE']:
            self.game.keys['ESCAPE'] = False # prevent to go back in pause
            self.exit_state()
        
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

        self.canvas.fill(settings.PAUSE_COLOR)

        for i, button in enumerate(self.buttons):
            # center this shit is a pain in the ass
            x = settings.WIDTH/2 - button.rect.width/2   # center button in X axis
            y = (settings.HEIGHT/2 - (button.rect.height/2) * ((3*i)+1) ) + (len(self.buttons)/2) * (button.rect.height)
            button.render(x, y)

        self.game.canvas = self.canvas


class Button(pygame.sprite.Sprite):
    def __init__(self, game, text: str, group: list, fonction: callable, highlight: bool=False) -> None:
        super().__init__()
        group.append(self)
        self.game = game
        self.text = text
        self.highlight: bool = highlight
        self.image = self.game.font.render(self.text, False, color=(0, 0, 0))
        self.rect = self.image.get_rect()
        self.fonction = fonction
    

    def update(self) -> None:
        if self.highlight:
            self.image = self.game.font.render(('>'+self.text+'<'), False, color=(50, 50, 50))
        else:
            self.image = self.game.font.render(self.text, False, color=(0, 0, 0))
        self.rect = self.image.get_rect()


    def render(self, pos_x: int, pos_y: int) -> None:
        self.game.canvas.blit(self.image, dest=(pos_x, pos_y))
