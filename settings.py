''' constants and global var '''
from typing import NewType


Color = NewType('Color', str)

# cheats
INVISIBILITY = False

# screen
WIDTH = 1024
HEIGHT = 512
FPS = 60

WIDTH_BACKUP = WIDTH
HEIGHT_BACKUP = HEIGHT

COUNTDOWN = 1 # number of second before the gameplay start

# BACKGROUND COLORS
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
MAX_BALLS = 10


BALL_RADIUS = 8
BRICK_SCORE = 10

# those are change for each difficulties, default is normal difficultie.
####################################################################
POWERUP_BIG_PADLLE_DURATION = 10  # in second
POWERUP_SPEED = 2
BALL_MULTIPLYER = 2  # for every ball spawn X more ball

# percentages
POWERUP_PADDLE_SIZE = 1.2
POWERUP_PADDLE_CHANCE = 5
POWERUP_BALL_CHANCE = 5

MAX_BOUNCE_ANGLE = 60

BALL_SPEED = 5
PADDLE_SPEED = 8
