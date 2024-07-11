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

    
    def update(self) -> None:
        if self.game.keys['RETURN']:
            gameplay = Gameplay(self.game)
            gameplay.enter_state()


    def render(self) -> None:
        self.game.canvas = self.canvas


class Gameplay(State):
    def __init__(self, game) -> None:
        super().__init__(game)
        self.game = game
        self.canvas = pygame.Surface(size=(settings.WIDTH, settings.HEIGHT))

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


    def update(self) -> None:
        if self.game.keys['ESCAPE']:
            self.exit_state()

    
    def render(self) -> None:
        self.game.canvas = self.canvas
