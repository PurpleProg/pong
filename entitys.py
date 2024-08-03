''' Define elements of the game, like a ball '''
import math  # for bounce angle calc
import random
from abc import abstractmethod, ABC
import pygame
import settings


class Ball:
    """ ball class, collide with other entities """
    def __init__(self, game, gameplay, pos: pygame.Vector2) -> None:
        super().__init__()

        self.game = game
        self.gameplay = gameplay
        self.speed: int = settings.BALL_SPEED
        self.direction: pygame.Vector2 = pygame.Vector2(random.uniform(-1, 1), -1)

        self.image: pygame.Surface = pygame.image.load(
            file='assets/Balls/Glass/Ball_Blue_Glass-32x32.png'
        ).convert()
        self.image.set_colorkey('#ff00ff')

        self.rect: pygame.Rect = self.image.get_rect()
        self.pos = pos

        self.rect.centerx = int(self.pos.x)
        self.rect.centery = int(self.pos.y)

    def update(
        self,
        paddle,
        bricks: pygame.sprite.Group,
        powerups: pygame.sprite.Group
    ) -> None:
        '''change the position of the ball'''

        self.pos.x += self.speed * self.direction.x
        self.pos.y += self.speed * self.direction.y
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)

        self.collide(paddle, bricks, powerups)

    def collide(
        self,
        paddle,
        bricks: pygame.sprite.Group,
        powerups: pygame.sprite.Group
    ) -> None:
        """
        bounce on walls, bricks and paddle.
        Spawns the powerups and kill the bricks.
        """

        self.collide_with_walls()
        self.collide_with_paddle(paddle=paddle)
        self.collide_with_briks(bricks=bricks, powerups=powerups)

    def collide_with_walls(self) -> None:
        """ bounce on walls and ceiling """
        if self.rect.left < 0 or self.rect.right > settings.WIDTH :
            self.direction.x *= -1
            # prevent the ball from going out of bounce
            if self.rect.right > settings.WIDTH:
                self.rect.right = settings.WIDTH
                self.direction.x = -1
            elif self.rect.left < 0:
                self.rect.left = 0
                self.direction.x = 1
        # ceiling
        if self.rect.top < 0:
            self.rect.top = 0
            self.direction.y = 1
        # bounce on the bottom too IF cheats are enable in settings
        # gameover is detected on gameplay.update
        if self.rect.bottom > settings.HEIGHT and settings.INVISIBILITY:
            self.direction.y = -1
            self.rect.bottom = settings.HEIGHT

    def collide_with_paddle(self, paddle) -> None:
        """ bounce on paddle, calculate bounce angle """
        if self.rect.colliderect(paddle.rect):
            # calculate angle
            distance = self.rect.x - paddle.rect.centerx
            normalized_distance = distance/(paddle.rect.width/2)
            bounce_angle = settings.MAX_BOUNCE_ANGLE * normalized_distance
            bounce_angle_in_radian = math.radians(bounce_angle)

            self.direction.x = math.sin(bounce_angle_in_radian)
            self.direction.y = -math.cos(bounce_angle_in_radian)

    def collide_with_briks(
        self,
        bricks: list,
        powerups: list,
    ) -> None:
        """ bounce, spawn powerups and kill bricks """
        colliding_bricks_index =  self.rect.collidelistall(bricks)

        if colliding_bricks_index:
            # spawn powerup
            r = random.randint(1, 100)
            if r <= settings.POWERUP_PADDLE_CHANCE:
                powerups.append(PaddleGrowup(
                    game=self.game,
                    gameplay=self.gameplay,
                    pos=bricks[colliding_bricks_index[0]].rect.center
                ))
            elif r >= (100-settings.POWERUP_BALL_CHANCE):
                powerups.append(MultipleBalls(
                    game=self.game,
                    gameplay=self.gameplay,
                    pos=self.rect.center
                ))

            ### get the incoming direction ###
            # X axis
            if self.direction.x > 0:
                delta_x = self.rect.right - bricks[colliding_bricks_index[0]].rect.left
            else:
                delta_x = bricks[colliding_bricks_index[0]].rect.right - self.rect.left
            # Y axis
            if self.direction.y > 0:
                delta_y = self.rect.bottom - bricks[colliding_bricks_index[0]].rect.top
            else:
                delta_y = bricks[colliding_bricks_index[0]].rect.bottom - self.rect.top

            #  change the direction
            if abs(delta_x - delta_y) < 10:   # corner (aproximation)
                self.direction.x *= -1
                self.direction.y *= -1
            elif delta_x > delta_y:   # comming from the top of the block
                self.direction.y *= -1
            else:                      # comming from the sides
                self.direction.x *= -1

            # removes brick from the game
            bricks.remove(bricks[colliding_bricks_index[0]])
            self.gameplay.bricks_breaked += 1

            self.direction.normalize_ip()

    def render(self, canvas: pygame.Surface) -> None:
        """ blit it's image to a surface """
        canvas.blit(self.image, self.rect)


class Paddle:
    """ move with keys, collide with walls and powerups """
    def __init__(self, game) -> None:
        super().__init__()

        self.game = game

        self.speed: int = settings.PADDLE_SPEED
        self.direction: int = 0

        self.image: pygame.Surface = pygame.image.load(
            file='assets/Paddles/Style B/Paddle_B_Purple_128x28.png'
        ).convert()
        self.image.set_colorkey('#ff00ff')
        self.pos: pygame.Vector2 = pygame.Vector2(
            x=settings.WIDTH / 2,
            y=settings.HEIGHT - (settings.HEIGHT / 10)
        )  # center the paddle on x and 10% of height on y

        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.centerx = int(self.pos.x)
        self.rect.centery = int(self.pos.y)

    def update(self, powerups: pygame.sprite.Group) -> None:
        """ change the direction, move and collide """
        # update direction with arrows
        if self.game.keys['RIGHT']:
            self.direction = 1
        elif self.game.keys['LEFT']:
            self.direction = -1
        else:
            self.direction = 0

        # move the paddle
        self.pos.x += self.speed * self.direction
        self.rect.centerx = int(self.pos.x)

        # collide powerups
        for powerup in powerups:
            if self.rect.colliderect(powerup.rect):
                powerup.activate()

        # prevent paddle from going out of bouds
        # collide with walls
        if self.rect.right > settings.WIDTH:
            self.rect.right = settings.WIDTH
            self.game.keys['RIGHT'] = False
            self.pos.x = self.rect.centerx
        elif self.rect.left < 0:
            self.rect.left = 0
            self.pos.x = self.rect.centerx

    def render(self, canvas: pygame.Surface) -> None:
        """ blit it's image to a surface """
        canvas.blit(self.image, self.rect)


class Brick:
    """ brick constructor """
    def __init__(self, pos_x, pos_y) -> None:
        super().__init__()
        self.pos: pygame.Vector2 = pygame.Vector2(pos_x, pos_y)
        self.image: pygame.Surface = pygame.image.load(
            file='assets/Bricks/Colored/Colored_Purple-64x32.png'
        ).convert()
        self.image.set_colorkey('#ffffff')
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.topleft = int(self.pos.x), int(self.pos.y)

    def update(self) -> None:
        """
        TODO:
        change image
        make a brick have multiple lifes
        """

    def render(self, canvas) -> None:
        """ blit it's image to a surface """
        canvas.blit(self.image, self.rect)


class Powerup(ABC):
    '''abstract parent class'''
    def __init__(self, game, gameplay, pos: tuple) -> None:
        super().__init__()
        self.game = game
        self.gameplay = gameplay
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
        """ every powerup shall overwrite this method """

    def update(self) -> None:
        ''' move the powerup down'''
        if not self.active:
            self.rect.y += settings.POWERUP_SPEED
            if self.rect.top > settings.HEIGHT:
                self.gameplay.powerups.remove(self)

    def render(self, canvas: pygame.Surface) -> None:
        """ blit it's image to a canvas """
        canvas.blit(self.image, self.rect)


class PaddleGrowup(Powerup):
    """ Bonus that makes the paddle bigger """
    def __init__(self, game, gameplay, pos: tuple) -> None:
        super().__init__(game, gameplay, pos)
        self.gameplay = gameplay
        self.image.fill('#00ffff')
        self.countdown_in_frames = settings.POWERUP_BIG_PADLLE_DURATION * settings.FPS

    def update(self) -> None:
        ''' overwrite for use a countdown '''
        if self.active:
            self.countdown_in_frames -= 1
            if self.countdown_in_frames < 0:
                self.unpowerup()
                self.gameplay.powerups.remove(self)
        else:
            self.rect.y += settings.POWERUP_SPEED
            if self.rect.top > settings.HEIGHT:
                self.gameplay.powerups.remove(self)

    def powerup(self) -> None:
        ''' add X% to the paddle size '''

        if (self.gameplay.paddle.rect.width * settings.POWERUP_PADDLE_SIZE) > settings.WIDTH:
            self.gameplay.powerups.remove(self)
            return

        # strech the image
        self.gameplay.paddle.image = pygame.transform.scale(
            surface=self.gameplay.paddle.image,
            size=(self.gameplay.paddle.rect.width*settings.POWERUP_PADDLE_SIZE, self.gameplay.paddle.rect.height)
        )
        # create a new rect
        self.gameplay.paddle.rect = self.gameplay.paddle.image.get_rect()
        # center it
        self.gameplay.paddle.rect.centerx = int(self.gameplay.paddle.pos.x)
        self.gameplay.paddle.rect.centery = int(self.gameplay.paddle.pos.y)

    def unpowerup(self) -> None:
        """ shrink the paddle """

        # shrink the image
        self.gameplay.paddle.image = pygame.transform.scale(
            surface=self.gameplay.paddle.image,
            size=(self.gameplay.paddle.rect.width/settings.POWERUP_PADDLE_SIZE, self.gameplay.paddle.rect.height)
        )
        # create new rect
        self.gameplay.paddle.rect = self.gameplay.paddle.image.get_rect()
        # center it
        self.gameplay.paddle.rect.centerx = int(self.gameplay.paddle.pos.x)
        self.gameplay.paddle.rect.centery = int(self.gameplay.paddle.pos.y)


class MultipleBalls(Powerup):
    """ Bonus that spawns more balls """
    def __init__(self, game, gameplay, pos: tuple) -> None:
        super().__init__(game, gameplay, pos)
        self.image.fill('#ffff00')
        self.gameplay = gameplay

    def powerup(self) -> None:
        tmp_list = []
        # be carefull dont modify something you're iterating
        for ball in self.gameplay.balls:
            for _ in range(settings.BALL_MULTIPLYER):
                if len(self.gameplay.balls) >= settings.MAX_BALLS:
                    # linit exponential balls resulting in lag then crash
                    break
                tmp_list.append(Ball(
                    game=self.game,
                    gameplay=self.gameplay,
                    pos=pygame.Vector2(ball.pos.x, ball.pos.y)))
        for ball in tmp_list:
            self.gameplay.balls.append(ball)

        self.gameplay.powerups.remove(self)
