from typing import NewType


Color = NewType('Color', str)

# cheats
INVISIBILITY = False

# screen
WIDTH = 1024
HEIGHT = 512
FPS = 60

COUNTDOWN = 3 - 1 # number of second before the gameplay start (starting form 0 so - 1)

# BG
BACKGROUND_COLOR = Color('#000000')  # to replace with assets
PAUSE_BACKGROUND_COLOR = Color('#ffff00')
MAINMENU_BACKGROUND_COLOR = Color('#00ffff')
GAMEOVER_BACKGROUND_COLOR = Color('#ff0000')
WIN_BACKGROUND_COLOR = Color('#00ff00')
SETTINGS_BACKGROUND_COLOR = Color('#00ffff')

# default font. There also is a bold and a mono variant.
FONT_NAME = 'font/PixeloidSans.ttf'
FONT_SIZE = 30
FONT_COLOR = Color('#000000')


# entities
MAX_BALLS = 255
POWERUP_SPEED = 2
POWERUP_BIG_PADLLE_DURATION = 10  # in second
BALL_MULTIPLYER = 2  # for every ball spawn X more ball

# percentages
POWERUP_PADDLE_SIZE = 1.2
POWERUP_PADDLE_CHANCE = 10
POWERUP_BALL_CHANCE = 10

MAX_BOUNCE_ANGLE = 60

BALL_SPEED = 5
BALL_RADIUS = 8

PADDLE_SPEED = 8

BRICK_SCORE = 10