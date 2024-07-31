import math  # for bounce angle calc
import random
from abc import abstractmethod
import pygame
import settings


class Ball(pygame.sprite.Sprite):
    def __init__(self, game, gameplay, pos: pygame.Vector2) -> None:
        super().__init__()

        self.game = game
        self.gameplay = gameplay
        self.speed: int = settings.BALL_SPEED
        self.direction: pygame.Vector2 = pygame.Vector2(random.uniform(-1, 1), -1)
        
        self.image: pygame.Surface = pygame.image.load('assets/Balls/Glass/Ball_Blue_Glass-32x32.png').convert()
        self.image.set_colorkey('#ff00ff')

        self.rect: pygame.Rect = self.image.get_rect()
        self.pos = pos

        self.rect.center = int(self.pos.x), int(self.pos.y)

    def update(self, paddle, bricks: pygame.sprite.Group, powerups: pygame.sprite.Group) -> None:
        '''change the position of the ball'''

        if self.pos.y > settings.HEIGHT and not settings.INVISIBILITY:
            self.kill()

        self.pos.x += self.speed * self.direction.x
        self.pos.y += self.speed * self.direction.y
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)

        self.collide(paddle, bricks, powerups)

    def collide(self, paddle, bricks: pygame.sprite.Group, powerups: pygame.sprite.Group) -> None:
        # walls
        if self.rect.left < 0 or self.rect.right > settings.WIDTH :
            self.direction.x *= -1
            if self.rect.right > settings.WIDTH:   # prevent a bug where you can push the ball into the wall
                self.rect.right = settings.WIDTH
                self.direction.x = -1
            elif self.rect.left < 0:
                self.rect.left = 0
                self.direction.x = 1
        if self.rect.top < 0:
            self.rect.top = 0
            self.direction.y = 1
        if self.rect.bottom > settings.HEIGHT and settings.INVISIBILITY:
            self.direction.y = -1
            self.rect.bottom = settings.HEIGHT

        # paddle
        if self.rect.colliderect(paddle.rect):
            self.rect.bottom = paddle.rect.top

            # calculate angle
            distance = self.rect.centerx - paddle.rect.centerx
            normalized_distance = distance/(paddle.rect.width/2)
            bounce_angle = settings.MAX_BOUNCE_ANGLE * normalized_distance
            bounce_angle_in_radian = math.radians(bounce_angle)

            self.direction.x = math.sin(bounce_angle_in_radian)
            self.direction.y = -math.cos(bounce_angle_in_radian)

        # bricks
        brick_list = bricks.sprites()
        bricks_that_collide: list = self.rect.collidelistall(brick_list)
        for brick_index in bricks_that_collide:
            # spawn powerup
            r = random.randint(1, 100)
            if r <= settings.POWERUP_PADDLE_CHANCE:
                powerups.add(Paddle_growup(
                    game=self.game, 
                    gameplay=self.gameplay, 
                    pos=brick_list[brick_index].rect.center
                ))
            elif r >= (100-settings.POWERUP_BALL_CHANCE):
                powerups.add(Multiple_balls(
                    game=self.game, 
                    gameplay=self.gameplay, 
                    pos=self.rect.center
                ))

            bricks.remove(brick_list[brick_index])
            self.gameplay.bricks_breaked += 1    # assuming that the ball is ONLY used from gameplay

            ### get the new direction ###
            # X axis
            if self.direction.x > 0:
                delta_x = self.rect.right - brick_list[brick_index].rect.left
            else:
                delta_x = brick_list[brick_index].rect.right - self.rect.left
            # Y axis
            if self.direction.y > 0:
                delta_y = self.rect.bottom - brick_list[brick_index].rect.top
            else:
                delta_y = brick_list[brick_index].rect.bottom - self.rect.top
            # check incoming direction
            if abs(delta_x - delta_y) < 10:   # corner (aproximation)
                self.direction.x *= -1
                self.direction.y *= -1
            elif delta_x > delta_y:   # comming from the top of the block 
                self.direction.y *= -1
            else:                      # comming from the sides
                self.direction.x *= -1

        if len(bricks_that_collide) >= 2:
            self.direction.y = 1
            # force going down on double collison

        self.direction.normalize_ip()

    def render(self, canvas: pygame.Surface) -> None:
        canvas.blit(self.image, self.rect)


class Paddle(pygame.sprite.Sprite):
    def __init__(self, game) -> None:
        super().__init__()

        self.game = game
        
        self.speed: int = settings.PADDLE_SPEED
        self.direction: int = 0

        self.image: pygame.Surface = pygame.image.load('assets/Paddles/Style B/Paddle_B_Purple_128x28.png').convert()
        self.image.set_colorkey('#ff00ff')
        self.pos: pygame.Vector2 = pygame.Vector2( ( (settings.WIDTH/2) -(self.image.get_width()/2) ), settings.HEIGHT-settings.HEIGHT/10)  # center the paddle on x and 10% of height on y
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.x, self.rect.y = int(self.pos.x), int(self.pos.y)
    
    def update(self, powerups: pygame.sprite.Group) -> None:

        # update direction with arrows
        if self.game.keys['RIGHT']:
            self.direction = 1
        elif self.game.keys['LEFT']:
            self.direction = -1
        else:
            self.direction = 0

        # move the paddle
        self.pos.x += self.speed * self.direction
        self.rect.x = int(self.pos.x)

        # collide powerups
        for powerup in powerups:
            if self.rect.colliderect(powerup.rect):
                powerup.activate()
     

        # prevent paddle from going out of bouds
        if self.rect.right > settings.WIDTH:
            self.rect.right = settings.WIDTH
            self.game.keys['RIGHT'] = False
            self.pos.x = self.rect.x
        elif self.rect.left < 0:
            self.rect.left = 0
            self.pos.x = self.rect.x

    def render(self, canvas: pygame.Surface) -> None:
        canvas.blit(self.image, self.rect)


class Brick(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y) -> None:
        super().__init__()
        self.pos: pygame.Vector2 = pygame.Vector2(pos_x, pos_y)
        self.image: pygame.Surface = pygame.image.load('assets/Bricks/Colored/Colored_Purple-64x32.png').convert()
        self.image.set_colorkey('#ffffff')
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.topleft = int(self.pos.x), int(self.pos.y)

    def render(self, canvas) -> None:
        canvas.blit(self.image, self.rect)


class Powerup(pygame.sprite.Sprite):
    '''parent class'''
    def __init__(self, game, pos: tuple) -> None:
        super().__init__()
        self.game = game
        self.active = False
        self.image: pygame.Surface = pygame.Surface(size=(16, 16))
        self.rect: pygame.Rect = pygame.Rect(pos[0], pos[1], 16, 16)

    def activate(self) -> None:
        '''make it invisible and apply the powerup'''
        self.image.set_alpha(0)
        self.rect.y = 0
        self.active = True
        self.powerup()

    @abstractmethod
    def powerup(self) -> None:
        pass

    def update(self) -> None:
        if not self.active:
            self.rect.y += settings.POWERUP_SPEED
            if self.rect.top > settings.HEIGHT:
                self.kill()

    def render(self, canvas: pygame.Surface) -> None:
        canvas.blit(self.image, self.rect)


class Paddle_growup(Powerup):
    def __init__(self, game, gameplay, pos: tuple) -> None:
        super().__init__(game, pos)
        self.gameplay = gameplay
        self.image.fill('#00ffff')
        self.countdown_in_frames = settings.POWERUP_BIG_PADLLE_DURATION * settings.FPS

    def update(self) -> None:
        ''' overwrite for use a countdown '''
        if not self.active:
            self.rect.y += settings.POWERUP_SPEED
            if self.rect.top > settings.HEIGHT:
                self.kill()
        
        if self.active:
            self.countdown_in_frames -= 1
            if self.countdown_in_frames < 0:
                self.unpowerup()
                self.kill()

    def powerup(self) -> None:
        ''' add X% to the paddle size '''
        paddle = self.gameplay.paddle
        
        # center it
        paddle.pos.x -= paddle.rect.width * 0.1
        # strech the image
        paddle.image = pygame.transform.scale(paddle.image, size=(paddle.rect.width*settings.POWERUP_PADDLE_SIZE, paddle.rect.height))
        # create a new rect
        paddle.rect = paddle.image.get_rect()
        paddle.rect.x = int(paddle.pos.x)
        paddle.rect.y = int(paddle.pos.y)

        self.gameplay.paddle = paddle

    def unpowerup(self) -> None: 
        paddle = self.gameplay.paddle
        # center
        paddle.pos.x += paddle.rect.width * 0.1
        # shrink the image
        paddle.image = pygame.transform.scale(paddle.image, size=(paddle.rect.width/settings.POWERUP_PADDLE_SIZE, paddle.rect.height))
        # create new rect
        paddle.rect = paddle.image.get_rect()
        paddle.rect.x = int(paddle.pos.x)
        paddle.rect.y = int(paddle.pos.y)

        self.gameplay.paddle = paddle


class Multiple_balls(Powerup):
    def __init__(self, game, gameplay, pos: tuple) -> None:
        super().__init__(game, pos)
        self.image.fill('#ffff00')
        self.gameplay = gameplay
    
    def powerup(self) -> None:
        tmp_grp: pygame.sprite.Group = pygame.sprite.Group()
        # be carefull dont modify something you're iterating
        for ball in self.gameplay.balls:
            for _ in range(settings.BALL_MULTIPLYER):
                if len(self.gameplay.balls.sprites()) >= settings.MAX_BALLS:
                    # linit exponential balls resulting in lag then crash 
                    break
                tmp_grp.add(Ball(
                    game=self.game, 
                    gameplay=self.gameplay, 
                    pos=pygame.Vector2(ball.pos.x, ball.pos.y)))
        for ball in tmp_grp:
            self.gameplay.balls.add(ball)
        
        self.kill()
