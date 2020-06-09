TITLE = "UpGame"
WIDTH = 480
HEIGHT = 640
FPS = 60
#FONT_NAME = 'JetBrains Mono'
FONT_1 = 'fonts\Birdy Game.ttf'
FONT_JB = 'fonts\Jetbrains Mono\JetBrainsMono-Regular.ttf'
FONT_TT_BOLD = 'fonts\TTNorms\TTNorms-Bold.ttf'
FONT_TT_MED = 'fonts\TTNorms\TTNorms-Medium.ttf'
HS_FILE = "highscore.txt"
SPRITESHEET = "spritesheet_jumper.png"

# настройки игрока
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12
PLAYER_GRAV = 0.8
PLAYER_JUMP = 20
# настройки механики
BOOST_POWER = 60
POW_SPAWN_PCT = 7
MOB_FREQ = 5000
PLAYER_LAYER = 2
PLATFORM_LAYER = 1
POW_LAYER = 1
MOB_LAYER = 2
CLOUD_LAYER = 0
PLATFORM_LIST = [(0, HEIGHT-60),
                 (WIDTH/2-50, HEIGHT*3/4),
                 (125, HEIGHT-350),
                 (350, 200),
                 (175, 100)]

# набор цветов
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)
LIGHTBLUE = (0, 155, 155)
NEWBLUE = (181, 239, 255)
NEWBLUE_2 = (150, 239, 255)
BGCOLOR = NEWBLUE_2
DARKBLUE = (0, 80, 137)
DARKGREY = (100, 100, 100)
TEXTCOLOR = DARKGREY