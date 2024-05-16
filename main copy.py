import time
import pygame as pg
import random

pg.init()
pg.mixer.init()

# константы
SIZE = (400, 600)

# здесь записан порядок нот и их длительность для каждой песни

CHRISTMAS_TREE_NOTES = ["c4", "a4", "a4", "g4", "a4", "f4", "c4", "c4", "c4", "a4", "a4", "a-4", "g4", "c5",
                        "c5", "d4", "d4", "a-4", "a-4", "a4", "g4", "f4", "c4", "a4", "a4", "g4", "a4", "f4"]
CHRISTMAS_TREE_DURATION = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2,
                           1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2]

BIRCH_NOTES = ["a4", "a4", "a4", "a4", "g4", "f4", "f4", "e4", "d4",
               "a4", "a4", "c5", "a4", "g4", "g4", "f4", "f4", "e4", "d4",
               "e4", "f4", "g4", "f4", "f4", "e4", "d4",
               "e4", "f4", "g4", "f4", "f4", "e4", "d4"]
BIRCH_DURATION = [1, 1, 1, 1, 2, 1, 1, 2, 2,
                  1, 1, 1, 1, 1, 1, 1, 1, 2, 2,
                  2, 1, 2, 1, 1, 2, 2,
                  2, 1, 2, 1, 1, 2, 2]

MORNING_NOTES = ["c5", "a4", "g4", "f4", "g4", "a4", "c5", "a4", "f4", "g4", "a4", "g4", "a4", "c5", "a4",
                 "c5", "d5", "a4", "d5", "c5", "a4", "f4", "c4", "a3", "g3", "f3", ]
MORNING_DURATION = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2]


class Tile(pg.sprite.Sprite):
    # загрузка всех картинок для плиток
    short_tile = pg.image.load("images/short_tile.png")
    short_tile = pg.transform.scale(short_tile, (SIZE[0] // 4, SIZE[1] // 3.5))
    short_tile_pressed = pg.image.load("images/short_tile_pressed.png")
    short_tile_pressed = pg.transform.scale(short_tile_pressed, (SIZE[0] // 4, SIZE[1] // 3.5))

    long_tile = pg.image.load("images/long_tile.png")
    long_tile = pg.transform.scale(long_tile, (SIZE[0] // 4, SIZE[1] // 2.2))
    long_tile_pressed = pg.image.load("images/long_tile_pressed.png")
    long_tile_pressed = pg.transform.scale(long_tile_pressed, (SIZE[0] // 4, SIZE[1] // 2.2))

    def __init__(self, long=False):
        '''
        Класс плитки может создавать их двух разных размеров: короткие и длинные.
        Если нужно создать длинную плитку, параметр long должен иметь значение True. По умолчанию плитки короткие.

        Длинная плитка имеет дополнительную переменную count - это сколько тиков уже прошло до того,
        как она посчитается сыгранной. Пока это время не прошло, длинную плитку нужно зажимать мышкой.
        '''
        super().__init__()

        if long:
            self.long = True
            self.image = Tile.long_tile
            self.count = 0
        else:
            self.long = False
            self.image = Tile.short_tile

        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, 3) * SIZE[0] // 4  # создаём плитку на случайной дорожке
        self.rect.y = -SIZE[1]

        # если плитка соприкосается с другими плитками, переставить её на свободную дорожку
        while pg.sprite.spritecollide(self, screen_notes, False):
            self.rect.x = random.randint(0, 3) * SIZE[0] // 4

        self.played = False

    def update(self):
        self.rect.y += 1

        # ставим длинные плитки в начальный цвет, чтобы если их перестали нажимать слишком рано,
        # они не застыли в нажатом положении
        if self.long and self.count > 0 and not self.played:
            self.image = Tile.long_tile

        mouse_pos = pg.mouse.get_pos()

        if pg.mouse.get_pressed()[0]:
            if self.rect.collidepoint(mouse_pos):
                self.press()

        if self.rect.y >= SIZE[1]:  # если плитка за пределами окна, она удаляется
            self.kill()

    def press(self):
        # нота плитки проигрывается если
        # 1. она на была проиграна раньше
        # 2. это длинная плитка и она ещё не отыграла ни одного тика
        # 3. это короткая плитка
        if not self.played:
            if self.long and self.count == 0:
                play_note()
            if not self.long:
                play_note()

        if self.long:
            # каждые несколько тиков при нажатии на длинную плитку её цвет меняется
            # когда нужное количество тиков пройдёт, то она навсегда поменяет цвет
            # и будет считаться нажатой

            self.count += 1
            if self.count % 5 == 0 and self.count * 2 < 255:
                self.image = Tile.long_tile_pressed
            else:
                self.image = Tile.long_tile
            if self.count >= 120:
                self.image = Tile.long_tile_pressed
                self.played = True
        else:
            # короткие плитки сразу меняют цвет и считаются сыгранными
            self.image = Tile.short_tile_pressed
            self.played = True


class Song:
    songs = []  # здесь будет хранится список всех доступных песен

    def __init__(self, name, notes, duration, rect, interval=0.5):
        self.name = name
        self.notes = notes
        self.duration = duration
        self.color = "pink"
        self.rect = pg.Rect(rect)
        
        self.interval = interval

        self.text = f1.render(self.name, True, "black")
        Song.songs.append(self)




screen = pg.display.set_mode(SIZE)

fps = 500
clock = pg.time.Clock()

next_note = 0  # номер ноты, которую нужно сыграть следующей
sound = None  # звук, который сейчас играет

pg.mixer.music.set_volume(0.3)

f1 = pg.font.Font(None, 38)



# создание песен
song1 = Song("В лесу родилась ёлочка", CHRISTMAS_TREE_NOTES, CHRISTMAS_TREE_DURATION, (20, 100, 360, 45))
song2 = Song("Во поле береза стояла", BIRCH_NOTES, BIRCH_DURATION, (20, 200, 360, 45), interval=0.7)
song3 = Song("Утро", MORNING_NOTES, MORNING_DURATION, (20, 300, 360, 45))


background_menu = pg.image.load("images/menu.png")
background_menu = pg.transform.scale(background_menu, SIZE)

is_play = False
mode = "menu"

#  Игровой цикл
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            quit()



    # Создадим меню для выбора песни
    if mode == "menu":


        # отрисовка фона
        screen.blit(background_menu, (0, 0))

        # выводим названия песен
        y = 1
        for song in Song.songs:
            pg.draw.rect(screen, pg.Color(song.color), song.rect, border_radius=4)
            screen.blit(song.text, (30, 100 * y + 5))
            y += 1


        # Выбор песни
        # Находим позицию курсора
        mouse_pos = pg.mouse.get_pos()
        for song in Song.songs:
            if song.rect.collidepoint(mouse_pos):
                song.color = "#59D5E0"
            else:
                song.color = "#FF71CD"

        # отслеживаем клик по заголовку песни
        if pg.mouse.get_pressed()[0]:

            for song in Song.songs:
                if song.rect.collidepoint(mouse_pos):
                    # Сбрасываем игровые параметры
                    screen_notes = pg.sprite.Group()
                    created_notes = 0
                    next_note = 0
                    timer = time.time()

                    playing_song = song
                    mode = "play"
                    print(playing_song)
    
    # Режим игры

    if mode == "play":
        print("Режим игры")


    pg.display.flip()
    clock.tick(fps)



