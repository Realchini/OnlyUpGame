import pygame as pg
import random
from settings import *
from sprites import *
from os import path
import webbrowser


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
        # начало новой игры
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
        # ИГРОВОЙ ЦИКЛ (основа)
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
        # Апдейт
        self.all_sprites.update()

        # спавн врагов
        now = pg.time.get_ticks()
        if now - self.mob_timer > 5000 + random.choice([-1000, -500, 0, 500, 1000]):
            self.mob_timer = now
            Mob(self)
        # игрок касается врага
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

        # если игрок поднимается за экран
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

        # касание ускорителя
        pow_hits = pg.sprite.spritecollide(self.player, self.powerups, True)
        for pow in pow_hits:
            if pow.type == 'boost':
                self.boost_sound.play()
                self.player.vel.y = -BOOST_POWER
                self.player.jumping = False

        # если игрок падает
        if self.player.rect.bottom > HEIGHT:
            # self.playing = False
            #self.krik_sound.play()
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.krik_sound.play()
            self.playing = False

        # спавн новых платформ
        while len(self.platforms) < 6:
            width = random.randrange(50, 100)
            Platform(self, random.randrange(0, WIDTH - width),
                    random.randrange(-75, -30))
            #self.platforms.add(p)
            #self.all_sprites.add(p)

    def events(self):
        # игровой цикл ивенты
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
        # игровой цикл отрисовка
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

    # def show_menu(self):
    #     self.screen.fill(BGCOLOR)
    #     self.background = pg.image.load(path.join(self.img_dir, 'menu_background.png'))
    #     self.screen.blit(self.background, (0,0))
    #     self.draw_text(TITLE, 86, FONT_1, DARKBLUE, WIDTH / 2, HEIGHT * 1 / 5)
    #
    #     btn_start = Button(WIDTH/2, 280, 'Начать')
    #     btn_start.selected = True
    #     btn_start.draw()
    #     btn_info = Button(WIDTH / 2, 350, 'Инфо')
    #     btn_info.draw()
    #     btn_quit = Button(WIDTH / 2, 420, 'Выйти')
    #     btn_quit.draw()
    #     btn_list = [btn_start, btn_info, btn_quit]
    #     self.draw_text('Made by Roman Chavyr, 2020', 14, FONT_TT_MED, DARKGREY, WIDTH/2, HEIGHT-50)
    #
    #     waiting = True
    #     while waiting:
    #         for event in pg.event.get():
    #             if event.type == pg.KEYUP:
    #                 if event.key == pg.K_DOWN:
    #                     #self.draw_text('Made by Roman Chavyr, 2020', 14, FONT_TT_MED, DARKGREY, WIDTH / 2, HEIGHT - 70)
    #                     btn_list[2].selected = True
    #                     #btn_list[2].draw()
    #                     #pg.display.flip()
    #                     pg.display.flip()
    #
    #     pg.display.flip()
    #     self.wait_for_key()

    def show_menu(self):
        menu = Menu()
        menu.buttons[0].selected = True
        in_menu = True
        while in_menu:
            self.screen.fill(BGCOLOR)
            self.background = pg.image.load(path.join(self.img_dir, 'menu_background.png'))
            self.screen.blit(self.background, (0,0))
            self.draw_text(TITLE, 86, FONT_1, DARKBLUE, WIDTH / 2, HEIGHT * 1 / 5)
            self.draw_text('Made by Roman Chavyr, 2020', 14, FONT_TT_MED, DARKGREY, WIDTH / 2, HEIGHT - 50)

            # waiting = True
            # while waiting:
            #     for event in pg.event.get():
            #         if event.type == pg.KEYUP:
            #             if event.key == pg.K_DOWN:
            #                 menu.buttons[select].selected = True
            #                 select+=1
            #                 pg.display.flip()
            #                 waiting = False

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    in_menu = False
                    self.running = False
                if event.type == pg.KEYUP:
                    if event.key == pg.K_DOWN:
                        menu.next()
                    if event.key == pg.K_UP:
                        menu.prev()
                    if event.key == pg.K_RETURN:
                        if menu.selected == 0:
                            return
                        if menu.selected == 1:
                            webbrowser.open('https://github.com/Realchini/OnlyUpGame', new=2)
                        if menu.selected == 2:
                            in_menu = False
                            self.running = False

            # for event in pg.event.get():
            #     if event.type == pg.KEYUP:
            #         if event.key == pg.K_UP:
            #             menu.prev()
            #menu.buttons[menu.selected].selected = True
            for i in menu.buttons:
                #i.selected = True
                i.draw()

            pg.display.flip()
            #self.wait_for_key()

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
                    if event.key == pg.K_SPACE:
                        waiting = False

    def draw_text(self, text, size, font, color, x, y):
        #font = pg.font.Font(self.font_name, size)
        font = pg.font.Font(font, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    # def draw_button(self, image, text, size, font, color, x, y):
    #     #font = pg.font.Font(self.font_name, size)
    #     font = pg.font.Font(font, size)
    #     text_surface = font.render(text, True, color)
    #     text_rect = text_surface.get_rect()
    #     text_rect.midtop = (x, y)
    #     self.screen.blit(text_surface, text_rect)



class Button:
    def __init__(self, x, y, text, selected=False):
        self.dir = path.dirname(__file__)
        self.img_dir = path.join(self.dir, 'img')
        self.selected = selected
        # if self.selected:
        #     self.image = pg.image.load(path.join(self.img_dir, 'ground_grass_for_menu_selected.png'))
        # else:
        #     self.image = pg.image.load(path.join(self.img_dir, 'ground_grass_for_menu.png'))
        self.x = x
        self.y = y
        self.text = text

    def draw(self):
        #mouse = pg.mouse.get_pos()
        #click = pg.mouse.get_pressed()
        if self.selected:
            self.image = pg.image.load(path.join(self.img_dir, 'ground_grass_for_menu_selected.png'))
        else:
            self.image = pg.image.load(path.join(self.img_dir, 'ground_grass_for_menu.png'))
        self.image_rect = self.image.get_rect()
        self.image_rect.center = (self.x, self.y)

        if self.selected:
            font = pg.font.Font(FONT_TT_BOLD, 28)
        else:
            font = pg.font.Font(FONT_TT_BOLD, 22)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (self.x, self.y)

        g.screen.blit(self.image, self.image_rect)
        g.screen.blit(text_surface, text_rect)



class Menu:
    def __init__(self):
        self.selected = 0
        self.buttons = [Button(WIDTH / 2, 280, 'Начать'), Button(WIDTH / 2, 350, 'Инфо'), Button(WIDTH / 2, 420, 'Выйти')]

    def next(self):
        if self.selected < 2:
            self.selected += 1
        else:
            self.selected = 0
        self.buttons[self.selected].selected = True
        for i in self.buttons:
            if i != self.buttons[self.selected]:
                i.selected = False

    def prev(self):
        if self.selected > 0:
            self.selected -= 1
        else:
            self.selected = 2
        self.buttons[self.selected].selected = True
        for i in self.buttons:
            if i != self.buttons[self.selected]:
                i.selected = False


# class Button:
#     global sounds_on
#
#     def __init__(self, width, height):
#         self.width = width
#         self.height = height
#         self.inactive_color = (118, 4, 189)
#         self.active_color = (129, 9, 203)
#
#     def draw(self, game, x, y, message, action=None, font_size=30):
#         mouse = pg.mouse.get_pos()
#         click = pg.mouse.get_pressed()
#
#         if x < mouse[0] < x + self.width and y < mouse[1] < y + self.height:
#             pg.draw.rect(game.screen, self.active_color, (x, y, self.width, self.height))
#
#             if click[0] == 1:
#                 #if sounds_on:
#                 #    pg.mixer.Sound.play(sound_button_click)
#                 pg.time.delay(300)
#                 if action is not None:
#                     if action == quit:
#                         pg.quit()
#                         quit()
#                     else:
#                         action()
#
#         else:
#             pg.draw.rect(game.screen, self.inactive_color, (x, y, self.width, self.height))
#
#         self.print_text(message, x, y, font_size=font_size)
#
#     def print_text(message, x, y, font_color=(0, 0, 0), font_type='freesansbold.ttf', font_size=32):
#         font_type = pg.font.Font(font_type, font_size)
#         text = font_type.render(message, True, font_color)
#         g.screen.blit(text, (x, y))


g = Game()
#g.show_start_screen()
g.show_menu()
while g.running:
    g.new()
    #g.krik_sound.play()
    g.show_go_screen()

pg.quit()
