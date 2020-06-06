import pygame as pg
import random
from settings import *
from sprites import *
from os import path


class Game:
    def __init__(self):
        # инициализация окна и прочьего
        #pg.init()
        #pg.mixer.init()
        pg.mixer.pre_init(44100, -16, 2, 2048)
        pg.mixer.init()
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        #self.font_name = pg.font.match_font(FONT_NAME)
        #self.font_name = pg.font.Font('fonts\Birdy Game.ttf', 36)
        #font_dir = path.join('fonts')
        #self.font_name = pg.font.Font('Birdy Game.ttf', 36)
        self.load_data()

    def load_data(self):
        self.dir = path.dirname(__file__)
        self.img_dir = path.join(self.dir, 'img')
        with open(path.join(self.dir, HS_FILE), 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0
        self.spritesheet = Spritesheet(path.join(self.img_dir, SPRITESHEET))
        self.cloud_images = []
        for i in range(1, 4):
            self.cloud_images.append(pg.image.load(path.join(self.img_dir, 'cloud{}.png'.format(i))).convert())
        self.snd_dir = path.join(self.dir, 'sounds')
        self.jump_sound = pg.mixer.Sound(path.join(self.snd_dir, 'jump-c-05.wav'))
        self.boost_sound = pg.mixer.Sound(path.join(self.snd_dir, 'jetpack-3-overdrived.wav'))
        self.krik_sound = pg.mixer.Sound(path.join(self.snd_dir, 'krik.ogg'))

    def new(self):
        # start a new game
        self.score = 0
        #self.all_sprites = pg.sprite.Group()
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.platforms = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.clouds = pg.sprite.Group()
        self.player = Player(self)
        #self.all_sprites.add(self.player)
        # p1 = Platform(0, HEIGHT-40, WIDTH, 40)
        # self.all_sprites.add(p1)
        # self.platforms.add(p1)
        # p2 = Platform(WIDTH/2-50, HEIGHT*3/4, 100, 20)
        # self.all_sprites.add(p2)
        # self.platforms.add(p2)
        for plat in PLATFORM_LIST:
            #p = Platform(self, *plat)
            Platform(self, *plat)
            #self.all_sprites.add(p)
            #self.platforms.add(p)
        self.mob_timer = 0
        pg.mixer.music.load(path.join(self.snd_dir, 'Caketown 1.ogg'))
        for i in range(8):
            c = Cloud(self)
            c.rect.y += 500
        self.run()

    def run(self):
        # game loop
        pg.mixer.music.play(loops=-1)
        self.clock.tick(FPS)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pg.mixer.music.fadeout(200)

    def update(self):
        # game loop - Update
        self.all_sprites.update()

        #spawn a mob?
        now = pg.time.get_ticks()
        if now - self.mob_timer > 5000 + random.choice([-1000, -500, 0, 500, 1000]):
            self.mob_timer = now
            Mob(self)
        # hit mobs?
        mob_hits = pg.sprite.spritecollide(self.player, self.mobs, False)
        if mob_hits:
            self.krik_sound.play()
            self.playing = False

        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if self.player.pos.x < lowest.rect.right and \
                self.player.pos.x > lowest.rect.left:
                    if self.player.pos.y < lowest.rect.centery:
                        self.player.pos.y = lowest.rect.top + 1
                        self.player.vel.y = 0
                        self.player.jumping = False

        # if player reaches top 1/4 of screen
        if self.player.rect.top <= HEIGHT / 4:
            if random.randrange(100) < 15:
                Cloud(self)
            self.player.pos.y += max(abs(self.player.vel.y), 2)
            for cloud in self.clouds:
                prlx = random.randrange(20, 40) / 10
                cloud.rect.y += max(abs(self.player.vel.y/2), prlx)
            for mob in self.mobs:
                mob.rect.y += max(abs(self.player.vel.y), 2)
            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.vel.y), 2)
                if plat.rect.top >= HEIGHT:
                    plat.kill()
                    self.score += 10

        # if player hits powerup
        pow_hits = pg.sprite.spritecollide(self.player, self.powerups, True)
        for pow in pow_hits:
            if pow.type == 'boost':
                self.boost_sound.play()
                self.player.vel.y = -BOOST_POWER
                self.player.jumping = False

        # Die!
        if self.player.rect.bottom > HEIGHT:
            # self.playing = False
            self.krik_sound.play()
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.playing = False

        # spawn new platforms to keep average number
        while len(self.platforms) < 6:
            width = random.randrange(50, 100)
            Platform(self, random.randrange(0, WIDTH - width),
                    random.randrange(-75, -30))
            #self.platforms.add(p)
            #self.all_sprites.add(p)

    def events(self):
        # game loop - events
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()
                    #self.jump_sound.play()
            #if event.type == pg.KEYUP:
            #    if event.key == pg.K_SPACE:
            #        self.player.jump_cut()

    def draw(self):
        # game loop - draw
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        self.screen.blit(self.player.image, self.player.rect)
        self.draw_text(str(self.score), 22, FONT_1, TEXTCOLOR, WIDTH / 2, 15)
        # after drawing everything, flip the display
        pg.display.flip()

    def show_start_screen(self):
        #pg.mixer.music.load(path.join(self.snd_dir, 'Caketown 1.ogg'))
        self.screen.fill(BGCOLOR)
        #FONT_2 = pg.font.Font('font/Birdy Game.ttf', 36)
        self.draw_text(TITLE, 86, FONT_1, DARKBLUE, WIDTH / 2, HEIGHT * 1/3)
        self.draw_text("(Влево/вправо - стрелки, прыжок - пробел)", 16, FONT_TT_MED, TEXTCOLOR, WIDTH / 2, HEIGHT * 4 / 5)
        self.draw_text("Нажмите любую клавишу", 22, FONT_TT_BOLD, TEXTCOLOR, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Рекорд: " + str(self.highscore), 18, FONT_TT_MED, TEXTCOLOR, WIDTH / 2, 15)
        #for i in range(8):
        #    c = Cloud(self)
        #    c.rect.y += 500
        pg.display.flip()
        self.wait_for_key()

    def show_menu(self):
        self.screen.fill(BGCOLOR)
        #self.start_btn = Button(100, 30)
        btn_image = pg.image.load(path.join(self.img_dir, 'ground_grass_SCALED.png'))
        self.screen.blit(btn_image, (0, 0))
        pg.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        if not self.running:
            return
        self.screen.fill(BGCOLOR)
        self.draw_text("GAME OVER", 72, FONT_1, DARKBLUE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Счёт: " + str(self.score), 22, FONT_TT_BOLD, TEXTCOLOR, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Нажмите, чтобы играть снова", 22, FONT_TT_MED, TEXTCOLOR, WIDTH / 2, HEIGHT * 3 / 4)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("NEW HIGHEST SCORE!", 22, FONT_1, TEXTCOLOR, WIDTH / 2, HEIGHT / 2 + 40)
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.score))
        else:
            self.draw_text("Рекорд: " + str(self.highscore), 22, FONT_TT_MED, TEXTCOLOR, WIDTH / 2, HEIGHT / 2 + 40)
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(30)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False

    def draw_text(self, text, size, font, color, x, y):
        #font = pg.font.Font(self.font_name, size)
        font = pg.font.Font(font, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def draw_button(self, image, text, size, font, color, x, y):
        #font = pg.font.Font(self.font_name, size)
        font = pg.font.Font(font, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)



class Button:
    global sounds_on

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.inactive_color = (118, 4, 189)
        self.active_color = (129, 9, 203)

    def draw(self, x, y, message, action=None, font_size=30):
        mouse = pg.mouse.get_pos()
        click = pg.mouse.get_pressed()

        if x < mouse[0] < x + self.width and y < mouse[1] < y + self.height:
            pg.draw.rect(Game.screen, self.active_color, (x, y, self.width, self.height))

            if click[0] == 1:
                #if sounds_on:
                #    pg.mixer.Sound.play(sound_button_click)
                pg.time.delay(300)
                if action is not None:
                    if action == quit:
                        pg.quit()
                        quit()
                    else:
                        action()

        else:
            pg.draw.rect(Game.screen, self.inactive_color, (x, y, self.width, self.height))

        #print_text(message=message, x=x + 10, y=y + 10, font_size=font_size)


g = Game()
#g.show_start_screen()
g.show_menu()
while g.running:
    g.new()
    #g.krik_sound.play()
    g.show_go_screen()

pg.quit()
