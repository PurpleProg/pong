import pygame
import settings
import random
import math  # for bounce angle calc


class Ball(pygame.sprite.Sprite):
    def __init__(self, game, group: pygame.sprite.Group, pos: pygame.Vector2 | None = None) -> None:
        super().__init__()

        self.group = group
        self.group.add(self)
        self.game = game
        self.speed: int = settings.BALL_SPEED
        self.direction: pygame.Vector2 = pygame.Vector2(0, -1)
        
        self.image: pygame.Surface = pygame.image.load('assets/Balls/Glass/Ball_Blue_Glass-32x32.png').convert()
        self.image.set_colorkey('#ff00ff')

        self.rect: pygame.Rect = self.image.get_rect()
        if pos == None:
            self.pos: pygame.Vector2 = pygame.Vector2(
                settings.WIDTH/2 - self.rect.width/2, 
                settings.HEIGHT - settings.HEIGHT/6
                )
        else:
            self.pos: pygame.Vector2 = pos
        self.rect.topleft = int(self.pos.x), int(self.pos.y)


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
            match random.randint(0, 20):
                case 1:
                    powerups.add(Paddle_growup(self.game, brick_list[brick_index].rect.center))
                case 2:
                    powerups.add(Multiple_balls(self.game, brick_list[brick_index].rect.center))

            bricks.remove(brick_list[brick_index])
            self.game.stack[-1].bricks_breaked += 1    # assuming that the ball is ONLY used from gameplay

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
        self.image.fill('#ffff00')
        self.rect: pygame.Rect = pygame.Rect(pos[0], pos[1], 16, 16)


    def activate(self) -> None:
        '''make it invisible and apply the powerup'''
        self.image.set_alpha(0)
        self.rect.y = 0
        self.active = True
        self.powerup()


    def powerup(self) -> None:
        raise NotImplementedError("this is a parent class and shall not be used as is.")


    def update(self) -> None:
        self.rect.y += settings.POWERUP_SPEED
        if self.rect.top > settings.HEIGHT:
            self.kill()    # i feel bat about this poor guy


    def render(self, canvas: pygame.Surface) -> None:
        canvas.blit(self.image, self.rect)


class Paddle_growup(Powerup):
    def __init__(self, game, pos: tuple) -> None:
        super().__init__(game, pos)
        self.image.fill('#00ffff')
        self.countdown_in_frames = settings.POWERUP_BIG_PADLLE_DURATION * settings.FPS
    

    def update(self) -> None:
        ''' overwrite for use a countdown '''
        if not self.active:
            self.rect.y += settings.POWERUP_SPEED
            if self.rect.top > settings.HEIGHT:
                self.kill()    # i feel bat about this poor guy
        
        if self.active:
            self.countdown_in_frames -= 1
            if self.countdown_in_frames < 0:
                self.unpowerup()
                self.kill()


    def powerup(self) -> None:
        ''' add 20% to the paddle size '''
        # center it
        self.game.stack[-1].paddle.rect.x -= self.game.stack[-1].paddle.rect.width * 0.1
        self.game.stack[-1].paddle.pos.x = self.game.stack[-1].paddle.rect.x
        # make it bigger
        self.game.stack[-1].paddle.rect.width *= 1.2
        # corect the image
        self.game.stack[-1].paddle.image = pygame.Surface(size=(self.game.stack[-1].paddle.rect.width, self.game.stack[-1].paddle.rect.height))
        self.game.stack[-1].paddle.image.fill(settings.PADDLE_COLOR)


    def unpowerup(self) -> None: 
        # change size
        self.game.stack[-1].paddle.rect.width /= 1.2
        # center
        self.game.stack[-1].paddle.rect.x += self.game.stack[-1].paddle.rect.width * 0.1
        self.game.stack[-1].paddle.pos.x = self.game.stack[-1].paddle.rect.x
        # correct image
        self.game.stack[-1].paddle.image = pygame.Surface(size=(self.game.stack[-1].paddle.rect.width, self.game.stack[-1].paddle.rect.height))
        self.game.stack[-1].paddle.image.fill(settings.PADDLE_COLOR)


class Multiple_balls(Powerup):
    def __init__(self, game, pos: tuple) -> None:
        super().__init__(game, pos)
    

    def powerup(self) -> None:
        tmp_grp: pygame.sprite.Group = pygame.sprite.Group()
        for ball in self.game.stack[-1].balls:
            for _ in range(2):
                ball = Ball(self.game, tmp_grp, pos=pygame.Vector2(ball.pos.x + 2, ball.pos.y + 2))
                ball.direction = pygame.Vector2(random.choice([-1, 1]), random.choice([-1, 1]))
        for ball in tmp_grp:
            self.game.stack[-1].balls.add(ball)
        
        self.kill()
