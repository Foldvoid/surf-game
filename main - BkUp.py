import math
import random

from kivy.config import Config
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout

Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '450')

from kivy.app import App
from kivy.core.window import Window
from kivy import platform
from kivy.clock import Clock
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.widget import Widget
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Quad, Triangle

Builder.load_file("menu.kv")


class MainWidget(RelativeLayout):
    from action_functions import keyboard_closed, on_keyboard_up, on_keyboard_down, on_touch_up, on_touch_down
    from transform import transform, transform2D, trasform_perspective

    title = StringProperty("S u r f l y")
    title_btn = StringProperty("Start")
    title_score = StringProperty("Score: 0")
    game_score = 0
    next_bonus = 100
    score_bonus = 1
    score_thousands = 0

    menu_widget = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    V_NB_LINES = 10
    V_LINES_SPACING = .5
    vertical_lines = []

    H_NB_LINES = 6
    H_LINES_SPACING = .1
    horizontal_lines = []
    current_offset_y = 0

    FPS = 60
    SPEED = .5
    SPEED_X = 1.2

    game_speed_y = 0
    game_speed_x = 0

    current_speed_x = 0
    current_offset_x = 0
    current_y_loop = 0

    NB_TILES = 16
    tiles = []
    tiles_coordinates = []

    PLR_WIDTH, PLR_HEIGHT, PLR_BASEY = .1, .035, .04
    plr = None
    plr_coordinates = [(0, 0), (0, 0), (0, 0)]

    game_start = False
    game_over = False

    sfx_start = None
    sfx_over = None
    music_menu = None
    music_loops = []
    music_idx = 0

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        # print("INIT W:", str(self.width), "INIT H:", str(self.height))
        self.init_audio()
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_plr()
        self.reset_game()

        if self.is_desktop():
            self._keyboad = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboad.bind(on_key_down=self.on_keyboard_down)
            self._keyboad.bind(on_key_up=self.on_keyboard_up)

        Clock.schedule_interval(self.update, 1 / self.FPS)

    def is_desktop(self):
        if platform in ('win', 'linux', 'macosx'):
            return True
        else:
            return False

    def init_audio(self):
        self.sfx_start = SoundLoader.load('./audio/game-start.mp3')
        self.sfx_over = SoundLoader.load('./audio/game-over.mp3')
        self.music_menu = SoundLoader.load('./audio/game-menu.mp3')
        self.music_loops = [
            SoundLoader.load('./audio/8-Bit-Mayhem.mp3'),
            SoundLoader.load('./audio/80s-Space-Game-Loop_v002.mp3'),
            SoundLoader.load('./audio/Hypnotic-Puzzle3.mp3'),
            SoundLoader.load('./audio/Hypnotic-Puzzle4.mp3'),
            SoundLoader.load('./audio/Puzzle-Dreams.mp3'),
            SoundLoader.load('./audio/Puzzle-Dreams-3.mp3'),
            SoundLoader.load('./audio/Runaway-Food-Truck.mp3')
        ]

        self.sfx_start.volume = .8
        self.sfx_over.volume = .8
        self.music_menu.volume = 1

        for music_loop in self.music_loops:
            music_loop.volume = 1

        Clock.schedule_once(self.play_game_menu_music, 0)

    def reset_game(self):
        self.current_offset_x = 0
        self.current_offset_y = 0
        self.current_y_loop = 0
        self.current_speed_x = 0

        self.game_score = 0

        self.game_speed_y = self.SPEED
        self.game_speed_x = self.SPEED_X

        self.tiles_coordinates = []
        self.generate_starting_tiles()
        self.generate_tile_coordinates()

        self.title_score = "Score: 0"
        self.game_over = False

    def init_plr(self):
        with self.canvas:
            Color(0, 1, 0)
            self.plr = Triangle()

    def update_plr(self):
        center_x = self.width / 2
        base_y = self.PLR_BASEY * self.width
        plr_width = self.PLR_WIDTH * self.width / 2
        plr_height = self.PLR_HEIGHT * self.height

        self.plr_coordinates[0] = (center_x - plr_width, base_y)
        self.plr_coordinates[1] = (center_x, base_y + plr_height)
        self.plr_coordinates[2] = (center_x + plr_width, base_y)

        x1, y1 = self.transform(*self.plr_coordinates[0])
        x2, y2 = self.transform(*self.plr_coordinates[1])
        x3, y3 = self.transform(*self.plr_coordinates[2])
        self.plr.points = [x1, y1, x2, y2, x3, y3]

    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.NB_TILES):
                self.tiles.append(Quad())

    def check_plr_on_tile(self, tile_x, tile_y):
        xmin, ymin = self.get_tile_coordinates(tile_x, tile_y)
        xmax, ymax = self.get_tile_coordinates(tile_x + 1, tile_y + 1)
        for i in range(0, len(self.plr_coordinates)):
            px, py = self.plr_coordinates[i]
            if xmin <= px <= xmax and ymin <= py <= ymax:
                return True
        return False

    def check_plr_on_track(self):
        for i in range(0, len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            if ti_y > self.current_y_loop + 1:
                return False
            if self.check_plr_on_tile(ti_x, ti_y):
                return True
        return False

    def generate_starting_tiles(self):
        staring_tiles = 10
        for i in range(0, staring_tiles):
            self.tiles_coordinates.append((0, i))

    def generate_tile_coordinates(self):
        last_x = 0
        last_y = 0

        start_idx = -int(self.V_NB_LINES / 2) + 1
        end_idx = start_idx + self.V_NB_LINES - 1

        for i in range(len(self.tiles_coordinates) - 1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]

        if len(self.tiles_coordinates) > 0:
            last_coordinates = self.tiles_coordinates[-1]
            last_x = last_coordinates[0]
            last_y = last_coordinates[1] + 1

        for i in range(len(self.tiles_coordinates), self.NB_TILES):
            r = random.randint(0, 2)
            self.tiles_coordinates.append((last_x, last_y))

            if r == 1:
                last_x += 1
                if last_x >= end_idx:
                    last_x = end_idx - 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            if r == 2:
                last_x -= 1
                if last_x < start_idx:
                    last_x = start_idx
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))


            last_y += 1

    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)

            for i in range(0, self.V_NB_LINES):
                self.vertical_lines.append(Line())

    def get_line_x_from_index(self, index):
        offset = index - 0.5
        spacing = self.V_LINES_SPACING * self.width
        central_line_x = self.perspective_point_x

        line_x = central_line_x + offset * spacing + self.current_offset_x
        return line_x

    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACING * self.height
        line_y = index * spacing_y - self.current_offset_y
        return line_y

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y -= self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    def update_tiles(self):
        for i in range(0, self.NB_TILES):
            tile = self.tiles[i]
            tile_coordinates = self.tiles_coordinates[i]
            xmin, ymin = self.get_tile_coordinates(tile_coordinates[0], tile_coordinates[1])
            xmax, ymax = self.get_tile_coordinates(tile_coordinates[0] + 1, tile_coordinates[1] + 1)

            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)

            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update_vertical_lines(self):
        start_idx = -int(self.V_NB_LINES / 2) + 1

        for i in range(start_idx, start_idx + self.V_NB_LINES):
            line_x = self.get_line_x_from_index(i)

            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)

            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)

            for i in range(0, self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self):
        start_idx = -int(self.V_NB_LINES / 2) + 1
        end_idx = start_idx + self.V_NB_LINES - 1

        x_min = self.get_line_x_from_index(start_idx)
        x_max = self.get_line_x_from_index(end_idx)

        spacing_y = self.H_LINES_SPACING * self.height

        for i in range(0, self.H_NB_LINES):
            line_y = i * spacing_y - self.current_offset_y

            x1, y1 = self.transform(x_min, line_y)
            x2, y2 = self.transform(x_max, line_y)

            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def game_speedup(self):
        self.game_speed_y += self.SPEED * pow(10, -2)
        self.game_speed_x += self.SPEED_X * pow(10, -2)

    def update(self, dt):
        time_factor = dt * 60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_plr()

        if not self.game_over and self.game_start:
            # speed_y = self.SPEED * self.height / 100
            speed_y = self.game_speed_y * self.height / 100
            self.current_offset_y += speed_y * time_factor

            spacing_y = self.H_LINES_SPACING * self.height
            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y

                self.current_y_loop += 1
                self.game_score += self.score_bonus
                self.title_score = "Score: " + str(self.game_score)

                score = int(self.title_score.split()[1])

                if score < 1000 and score % 100 == 0:
                    self.game_speedup()
                elif score < 10000 and score % 1000 == 0:
                    self.game_speedup()
                elif score < 100000 and score % 10000 == 0:
                    self.game_speedup()
                elif score < 1000000 and score % 100000 == 0:
                    self.game_speedup()

                if score % self.next_bonus == 0:
                    self.score_bonus *= 10
                    self.next_bonus *= 100

                self.generate_tile_coordinates()

            speed_x = self.current_speed_x * self.width / 100
            self.current_offset_x += speed_x * time_factor

        if not self.check_plr_on_track() and not self.game_over:
            self.game_over = True
            self.title = "G a m e  O v e r"
            self.title_btn = "Restart"
            self.menu_widget.opacity = 1

            self.stop_game_music()
            Clock.schedule_once(self.play_sfx_game_over, 1)
            Clock.schedule_once(self.play_game_menu_music, 22)

            print("GAME OVER!")

    def play_game_menu_music(self, dt):
        if self.game_over or not self.game_start:
            self.music_menu.loop = True
            self.music_menu.play()

    def stop_game_menu_music(self):
        self.music_menu.loop = False
        self.music_menu.stop()

    def play_game_music(self, dt):
        if not self.game_over:
            self.music_idx = random.randint(0, len(self.music_loops) - 1)
            self.music_loops[self.music_idx].loop = True
            self.music_loops[self.music_idx].play()

    def stop_game_music(self):
        self.music_loops[self.music_idx].loop = False
        self.music_loops[self.music_idx].stop()

    def play_sfx_game_start(self):
        self.sfx_start.play()

    def play_sfx_game_over(self, dt):
        if self.game_over:
            self.sfx_over.play()

    def start_btn_pressed(self):
        self.sfx_over.stop()
        self.reset_game()
        self.stop_game_menu_music()
        self.play_sfx_game_start()
        Clock.schedule_once(self.play_game_music, 1)
        self.game_start = True
        self.menu_widget.opacity = 0

class SurflyApp(App):
    pass


SurflyApp().run()
