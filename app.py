import os
import time
import random
import cv2

import pygame
from pygame.image import load
from pygame.transform import scale
from pygame.mouse import get_pressed as mouse_press
from pygame.mouse import get_pos as mouse_pos
from pygame.font import SysFont

pygame.init()
pygame.font.init()

WIN_SCALE = 1.4

WIN_SIZE = WIDTH, HEIGHT = int(1000 * WIN_SCALE), int(600 * WIN_SCALE)
TILE_SIZE = int(50 * WIN_SCALE)
GRAVITY = 0.55
DEBUG = True
SCALE = 1.4
# Dino
DINO_WIDTH = 100 * SCALE
DINO_HEIGHT = 0.8 * DINO_WIDTH
DINO_DOWN_TIMER = 60

COMMANDS = ['alive']

# Obstcle
CACTUS_WIDTH = 40 * SCALE
CACTUS_HEIGHT = 1.5 * CACTUS_WIDTH

CRATE_WIDTH = 50 * SCALE
CRATE_HEIGHT = CRATE_WIDTH

STONE_WIDTH = 40 * SCALE
STONE_HEIGHT = 1.25 * STONE_WIDTH

# Helicopter

HELICOPTER_WIDTH = 150 * SCALE
HELICOPTER_HEIGHT = HELICOPTER_WIDTH / 3


class Tile:
    def __init__(self, tilemap, image, x: int, y: int):
        self.tilemap: TimeMap = tilemap
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed_force = 4

    def draw(self):
        self.tilemap.bg.scene.window.blit(self.image, self.rect)

    def update(self):
        self.rect.x -= self.tilemap.bg.speed  # * self.speed_force

        if self.rect.x <= - TILE_SIZE:
            self.rect.x = WIDTH + 2 * TILE_SIZE + self.rect.x  # % (self.tilemap.bg.speed * self.speed_force)


class TimeMap:
    def __init__(self, bg):
        self.tileset = self.get_tileset()
        self.bg: Bg = bg

    def get_images(self) -> list:
        images = []
        for i in range(2, 6, 3):
            image = load(f"assets/deserttileset/Tile/{i}.png").convert_alpha()
            image = scale(image, (TILE_SIZE, TILE_SIZE))
            images.append(image)
        return images

    def get_tileset(self):
        tileset = []
        images = self.get_images()
        for index, image in enumerate(images):
            x = 0
            y = HEIGHT - (2 - index) * TILE_SIZE
            for i in range(WIDTH // TILE_SIZE + 2):
                tileset.append(Tile(self, image, x, y))
                x += TILE_SIZE
        return tileset

    def draw(self, screen: pygame.Surface = None):

        for tile in self.tileset:
            tile.draw()
            if not self.bg.scene.is_pause:
                tile.update()


class Bg:
    def __init__(self, scene):
        self.scene: Scene = scene
        self.image = self.get_image()
        self.rect = self.image.get_rect(topleft=(0, 0))

        self.tilemap = TimeMap(self)
        self.pause_btn: ImageButton = self.get_pause_btn()
        self.speed = 4

    def get_image(self):
        image = load("assets/deserttileset/BG.png").convert_alpha()
        image = scale(image, WIN_SIZE)
        return image

    def draw(self):
        self.scene.window.blit(self.image, self.rect)
        self.scene.window.blit(self.image, (self.rect.x + self.rect.width, self.rect.y))

        self.tilemap.draw()

        if not self.scene.is_pause and self.scene.dino.alive:
            self.pause_btn.draw(self.scene.window, x=WIDTH - self.pause_btn.rect.width - 20, y=20)
            if self.pause_btn.is_clicked:
                self.pause_btn.is_clicked = False
                self.scene.is_pause = True
                self.scene.pause_screen = PauseScreen(self.scene)

    def get_pause_btn(self):
        image = load("assets/others/pause.png").convert_alpha()
        image = scale(image, (60, 60))
        button = ImageButton(image, WIDTH - image.get_width() - 20, 20)
        return button

    def update(self):
        self.rect.x -= self.speed // 2
        if self.rect.x < -WIDTH:
            self.rect.x = 0

    def get_ground(self):
        return self.tilemap.tileset[0]


class Obstacle:
    START_SPEED = 2
    SPEED = START_SPEED
    START_ANIM_SPEED = 3
    ANIM_SPEED = START_ANIM_SPEED

    def __init__(self, scene, x, y):
        self.scene: Scene = scene

        self.obstacle_names = ("Crate", "StoneBlock", "Stone", "Cactus (1)", "Cactus (3)",)
        self.images: dict = self.get_images()
        self.image_name = random.choice(tuple(self.images.keys()))
        self.frame_index = 0
        self.image: pygame.Surface = self.images[self.image_name][self.frame_index]
        self.rect = self.image.get_rect(midbottom=(x, y))

        self.rotate_speed = self.SPEED
        self.anim_speed = self.ANIM_SPEED

        self.is_active = True

    @classmethod
    def add_speed(cls):
        cls.SPEED += 1

    @classmethod
    def retry_speed(cls):
        cls.SPEED = cls.START_SPEED

    @classmethod
    def change_anim_speed(cls):
        if cls.ANIM_SPEED > 1:
            cls.ANIM_SPEED -= 1

    @classmethod
    def retry_anim_speed(cls):
        cls.ANIM_SPEED = cls.START_ANIM_SPEED

    def get_images(self) -> dict:
        image_dict = dict()

        for name in self.obstacle_names:
            image = load(f"assets/deserttileset/Objects/{name}.png").convert_alpha()
            img_list = []
            if name.startswith("Cactus"):
                image = scale(image, (CACTUS_WIDTH, CACTUS_HEIGHT))
            elif name in ("Crate", "StoneBlock"):
                image = scale(image, (CRATE_WIDTH, CRATE_HEIGHT))
                r0_image = pygame.transform.rotate(image, 5)
                r1_image = pygame.transform.rotate(image, 15)
                r2_image = pygame.transform.rotate(image, 25)
                r3_image = pygame.transform.rotate(image, 35)
                r4_image = pygame.transform.rotate(image, 45)
                r5_image = pygame.transform.rotate(image, 55)
                r6_image = pygame.transform.rotate(image, 65)
                r7_image = pygame.transform.rotate(image, 75)
                r8_image = pygame.transform.rotate(image, 85)
                img_list += [r0_image, r1_image, r2_image, r3_image, r4_image, r5_image, r6_image, r7_image, r8_image]
            else:
                image = scale(image, (STONE_WIDTH, STONE_HEIGHT))
            img_list.insert(0, image)
            image_dict[name] = img_list

        return image_dict

    def draw(self):
        self.scene.window.blit(self.image, self.rect)

    def update(self):
        self.rect.x -= self.scene.bg.speed  # * self.scene.bg.tilemap.tileset[0].speed_force
        if self.rect.x + 4 * self.rect.width < 0:
            self.is_active = False
            pass

        if self.image_name in ("Crate", "StoneBlock"):
            self.rect.x -= self.rotate_speed
            if self.rotate_speed > 0:
                self.animate()
            else:
                self.image = self.images[self.image_name][0]

    def animate(self):
        self.frame_index += 1

        if self.frame_index == len(self.images[self.image_name]) * self.anim_speed - 1:
            self.frame_index = 0

        self.image = self.images[self.image_name][self.frame_index // self.anim_speed]


class Helicopter:
    START_SPEED = 2
    SPEED = START_SPEED

    def __init__(self, scene, width: int, height: int, x, y):
        self.scene: Scene = scene
        self.images: tuple = self.get_images(width, height)
        self.frame_index = 0
        self.image: pygame.Surface = self.images[self.frame_index]
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.anim_speed = 2
        self.speed = self.SPEED
        self.is_active = True

    @classmethod
    def add_speed(cls):
        cls.SPEED += 1

    @classmethod
    def retry_speed(cls):
        cls.SPEED = cls.START_SPEED

    def get_images(self, width: int, height: int) -> tuple:
        images = []
        for i in range(1, 5):
            image = load(f"assets/separated_frames/helicopter_{i * 2}.png").convert_alpha()
            image = scale(image, (width, height))
            image = pygame.transform.flip(image, True, False)
            images.append(image)
        return tuple(images)

    def draw(self):
        self.scene.window.blit(self.image, self.rect)
        # pygame.draw.rect(self.scene.window, "red", self.rect, 2)

    def update(self):
        self.animate()
        if self.rect.x > -self.rect.width:
            self.rect.x -= (self.scene.bg.speed + self.speed)
        else:
            self.is_active = False

    def animate(self):
        self.frame_index += 1

        if self.frame_index == len(self.images) * self.anim_speed - 1:
            self.frame_index = 0

        self.image = self.images[self.frame_index // self.anim_speed]


class Dino:
    def __init__(self, scene, x, y, width, height):
        self.scene: Scene = scene

        self.width = width
        self.height = height

        self.images = self.get_images()
        self.state = "Idle"
        self.frame_index = 0
        self.image: pygame.Surface = self.images[self.state][self.frame_index]
        self.rect: pygame.Rect = self.image.get_rect(midbottom=(x, y))

        self.anim_speed = 6
        self.jump_anim_sped = 3
        self.ANIM_SPEED = self.anim_speed
        self.direction = 0
        self.is_change_speed = False

        self.alive = True

        self.is_jumping = False
        self.on_ground = False
        self.jump_force = -12 * SCALE
        self.vel_y = 0

        self.down_timer = DINO_DOWN_TIMER
        self.down_ticks = 0
        self.down_counter = 0

        self.__cheet_live: bool = False

    def get_images(self) -> dict:
        image_dict: dict = {}
        main_path = "assets/dino"
        dino_dirs = os.listdir(main_path)

        for dino_dir in dino_dirs:
            image_list = []
            dir_length = len(os.listdir(f"{main_path}/{dino_dir}"))

            for i in range(dir_length):
                image = load(f"{main_path}/{dino_dir}/{dino_dir} ({i + 1}).png").convert_alpha()
                image = scale(image, (self.width, self.height))
                image_list.append(image)

            image_dict[dino_dir] = tuple(image_list)

        return image_dict

    def draw(self):
        self.scene.window.blit(self.image, self.rect)

    def update(self):
        self.animate()
        if self.scene.game_class.is_active_start:
            self.jump()
            self.collide_obstacle()
            self.check_down()
        else:
            self.walk()

    def animate(self):
        self.frame_index += 1
        if self.alive:

            if self.frame_index == len(self.images[self.state]) * self.anim_speed - 1:
                if self.state in ("Down", "Jump"):
                    self.frame_index -= 1
                else:
                    self.frame_index = 0
                    if self.is_change_speed and self.anim_speed > 2:
                        self.is_change_speed = not self.is_change_speed
                        self.anim_speed -= 1
                        self.ANIM_SPEED = self.anim_speed

        else:
            if self.frame_index > len(self.images[self.state]) * self.anim_speed - 1:
                self.frame_index = len(self.images[self.state]) * self.anim_speed - 1

        image = self.images[self.state][self.frame_index // self.anim_speed]
        self.image = pygame.transform.flip(image, flip_x=self.direction, flip_y=False)

    def jump(self):
        dy = 0
        if self.is_jumping:
            self.change_state("Jump")

            self.vel_y = self.jump_force
            self.is_jumping = False
            self.on_ground = False

        if not self.on_ground:
            self.vel_y += self.scene.game_class.GRAVITY
            dy += self.vel_y

        if self.rect.bottom + dy - self.rect.height // 7 > self.scene.bg.get_ground().rect.top:
            dy = self.scene.bg.get_ground().rect.top - self.rect.bottom + self.rect.height // 7
            self.on_ground = True
            if self.alive:
                self.change_state("Run")

        self.rect.y += dy

    def cheet_live_active(self, value: bool):
        if value is True:

            self.__cheet_live = True
        else:
            self.__cheet_live = False



    def collide_obstacle(self):
        if self.alive:
            for obstacle in self.scene.obstacle_list:
                y = self.rect.y
                if isinstance(obstacle, Obstacle):
                    if obstacle.rect.colliderect(self.rect.x + 15, y, self.rect.width // 2,
                                                 self.rect.height // 1.5):
                        if not self.__cheet_live:
                            self.alive = False
                            self.change_state("Dead")
                            self.scene.bg.speed = 0
                            obstacle.rotate_speed = 0


                else:
                    y = 0
                    if self.state == "Down":
                        y += 20

                    if (
                            obstacle.rect.x - self.rect.width // 3 < self.rect.x < obstacle.rect.x - self.rect.width // 3 + obstacle.rect.width // 2) and \
                            self.rect.top + 10 + y < obstacle.rect.bottom:
                        if not self.__cheet_live:
                            self.alive = False
                            self.change_state("Dead")
                            self.scene.bg.speed = 0
                            obstacle.rotate_speed = 0


    def change_state(self, new_state: str):
        if self.state != new_state:
            self.state = new_state
            self.frame_index = 0
            self.anim_speed = self.ANIM_SPEED
            if self.state == "Jump":
                self.anim_speed = self.jump_anim_sped

    def walk(self):
        if self.state == "Walk":

            if self.direction == 0:
                if self.rect.midbottom[0] < WIDTH - (100 * self.scene.game_class.start_screen.animate_dino_scale) / 2:
                    self.rect.x += 2
                else:
                    self.change_state("Idle")
                    self.direction = 0 if self.direction == 1 else 1
            else:
                if self.rect.midbottom[0] > (100 * self.scene.game_class.start_screen.animate_dino_scale) / 2:
                    self.rect.x -= 2
                else:
                    self.change_state("Idle")
                    self.direction = 0 if self.direction == 1 else 1

    def check_down(self):
        if self.alive and self.state == "Down":
            self.down_counter += 1
            if self.down_counter > self.down_timer:
                self.down_counter = 0
                self.change_state("Run")


class Button:
    def __init__(self, image, x, y):
        self.image: pygame.Surface = image
        self.rect = self.image.get_rect(topleft=(x, y))

        self.size = self.rect.size
        self.btn_bg_color = "brown"
        self.is_clicked = False

    def draw(self, window: pygame.Surface):
        pygame.draw.rect(window, self.btn_bg_color,
                         (
                             self.rect.x - 10,
                             self.rect.y - 10,
                             self.rect.width + 20,
                             self.rect.height + 20),
                         border_radius=20,
                         )

        window.blit(self.image, self.rect)
        if self.rect.x < mouse_pos()[0] < self.rect.x + self.rect.width and \
                self.rect.y < mouse_pos()[1] < self.rect.y + self.rect.height:
            self.btn_bg_color = "white"
            if not self.is_clicked and mouse_press()[0] == 1:
                self.is_clicked = True
        else:
            self.btn_bg_color = "brown"

        return self.is_clicked


class ImageButton(Button):
    def __init__(self, image, x, y):
        super().__init__(image, x, y)

    def draw(self, window: pygame.Surface, x: int = None, y: int = None, rect: pygame.Rect = None):
        if not x and not y:
            x = (window.get_width() - self.rect.width) // 2
            y = (window.get_height() - self.rect.height) // 2

        window.blit(self.image, (x, y))
        dx = self.rect.x
        dy = self.rect.y
        if rect:
            dx = rect.x + rect.width - self.rect.width - 10
            dy = rect.y + 10
        if dx < mouse_pos()[0] < dx + self.rect.width and \
                dy < mouse_pos()[1] < dy + self.rect.height:
            # print(mouse_pos())
            if not self.is_clicked and mouse_press()[0] == 1:
                self.is_clicked = True


class Console:
    def __init__(self, _class):
        self._class: PauseScreen = _class
        self.font = SysFont("sans", 20)
        self.surface = pygame.Surface(self._class.rect.size)
        self.rect = self.surface.get_rect(topleft=(0, 0))
        self.commands = self._class.scene.game_class.commands
        self.command: pygame.Surface = None
        self.text: str = ""

        self.input_active = False
        self.color = "grey"
        self.input_table = self.font.render(self.text, True, "white")

        self.input_rect = pygame.Rect(
            self.rect.x + 20,
            self.rect.height - self.input_table.get_height() - 20,
            self.rect.width - 40,
            self.input_table.get_height()
        )

        self.console_text = self.font.render("Console", True, "White")
        self.console_text_rect = self.console_text.get_rect(topleft=(
            (self.rect.width - self.console_text.get_width()) // 2,
            0 + 20)
        )

        self.close_btn = self.get_close_button()

    def draw(self):
        self._class.surface.blit(self.surface, self.rect)
        self.surface.fill("black")
        if self.commands:
            y = self.console_text_rect.height + 40
            for command in self.commands:
                self.surface.blit(command, (20, y))
                y += 35
                if y > self.rect.height - self.console_text_rect.height - 20:
                    self.commands = self.commands[-1:]
                    y = self.console_text_rect.height + 40

        rect = self.console_text_rect
        pygame.draw.rect(self.surface, "blue",
                         (self.rect.x + 10, self.rect.y + 10, self.rect.width - 20, rect.height + 20))
        self.surface.blit(self.console_text, self.console_text_rect)

        pygame.draw.rect(self.surface, self.color,
                         (self.input_rect.x - 10, self.input_rect.y - 10,
                          self.input_rect.width + 20, self.input_rect.height + 20), 5)

        self.close_btn.draw(
            self.surface,
            x=self.rect.width - self.close_btn.rect.width - 10,
            y=10,
            rect=self._class.rect
        )
        if self.close_btn.is_clicked:
            self._class.console_active = False
            self.close_btn.is_clicked = False

        self.input_text()

    def input_text(self):
        if mouse_press()[0] == 1:
            if self._class.rect.x + 20 < mouse_pos()[0] < self._class.rect.x + self._class.rect.width - 40 and \
                    self._class.rect.y + self.rect.height - self.input_table.get_height() - 20 < mouse_pos()[1] < \
                    self._class.rect.y + self.rect.height - 20:
                self.input_active = True
            else:
                self.input_active = False

        self.color = "grey"
        if self.input_active:
            self.color = "red"
            text = self.text + "|"
            self.input_table = self.font.render(text, False, "white")
            self.surface.blit(self.input_table, self.input_rect)

    def get_close_button(self):
        image = load("assets/others/close.png").convert_alpha()
        image = scale(image, (40, 40))
        return ImageButton(image, 0, 0)

    def check_command(self, command: str):

        command, value = command.strip().split(" ")
        if command == "alive":
            if value == "1":
                self._class.scene.dino.cheet_live_active(True)
            else:
                self._class.scene.dino.cheet_live_active(False)

class Write:
    def __init__(self, scene, text: str):
        self.scene: Scene = scene
        self.font = SysFont("tlwgtypo", int(40 * WIN_SCALE), True)
        self.text = text
        self.value = 0

    def draw(self, x: int, y: int, value: int | str, color: str | tuple = "darkred"):
        if self.value < value:
            self.value = value
        self.text_render = self.font.render(f"{self.text}: {self.value}", True, color)
        self.scene.window.blit(self.text_render, (x, y))

    def draw_timer(self, x: int, y: int, value: int | str, color: str | tuple = "white"):
        minutes = 0
        if value > 60:
            minutes = value // 60
            seconds = value % 60
        else:
            seconds = value

        if minutes < 10:
            minutes = "0" + str(minutes)
        if seconds < 10:
            seconds = "0" + str(seconds)

        self.text_render = self.font.render(f"{self.text}: {minutes}:{seconds}", True, color)
        self.scene.window.blit(self.text_render, (x, y))


class StartScreen:
    def __init__(self, game_class, is_restart: bool = False):
        self.game_class: Game = game_class
        self.running = True
        self.window = pygame.display.get_surface()
        self.clock = pygame.time.Clock()

        self.font = SysFont("tlwgtypo", int(50 * WIN_SCALE), True)
        self.font2 = SysFont("tlwgtypo", int(300 * WIN_SCALE), True)
        self.image = self.get_bg_image()
        self.rect = self.image.get_rect(topleft=(0, 0))

        self.start_btn: Button = self.get_start_button()
        self.quit_btn: Button = self.get_quit_button()

        self.loading_width = 300
        self.l_width = 0
        self.loading_height = 70
        self.is_loaded = False
        self.load_speed = 7

        self.surface_right = pygame.Surface((WIDTH // 2, HEIGHT))
        self.surface_right.set_alpha(240)
        self.surface_left = pygame.Surface((WIDTH // 2, HEIGHT))
        self.surface_left.set_alpha(240)

        self.surface_rect_right = self.surface_right.get_rect(topleft=(0, 0))
        self.surface_rect_left = self.surface_left.get_rect(topleft=(WIDTH // 2, 0))

        self.surface_right.fill("black")
        self.surface_left.fill("black")

        self.surface_speed = 1.5
        self.is_feed = True

        self.is_restart = is_restart
        self.change_state_timer = random.randint(5000, 10000)
        self.change_state_counter = pygame.time.get_ticks()
        self.animate_dino_scale = 6 * WIN_SCALE
        self.animate_dino = Dino(self.game_class.scene, (100 * self.animate_dino_scale) / 2, HEIGHT - 100 * WIN_SCALE,
                                 100 * self.animate_dino_scale, 80 * self.animate_dino_scale)

    def get_bg_image(self):
        bg_image = load("assets/deserttileset/BG2.png").convert_alpha()
        bg_image = scale(bg_image, WIN_SIZE).convert()

        return bg_image

    def get_start_button(self, color: str | tuple = "black") -> Button:
        image = self.font.render(f"Start", True, color)
        btn = Button(
            image,
            x=WIDTH - image.get_width() - 40,
            y=(HEIGHT - image.get_height()) - 40,
        )

        return btn

    def get_quit_button(self, color: str | tuple = "black") -> Button:
        image = self.font.render(f"Quit", True, color)
        btn = Button(
            image,
            x=40,
            y=(HEIGHT - image.get_height()) - 40,
        )

        return btn

    def draw_surface(self):

        self.window.blit(self.surface_right, self.surface_rect_right)
        self.window.blit(self.surface_left, self.surface_rect_left)
        if self.surface_rect_left.x < WIDTH + 50:
            self.surface_rect_right.x -= self.surface_speed
            self.surface_rect_left.x += self.surface_speed
        else:
            self.is_feed = False

    def get_dino_text(self, color: str | tuple = "black"):
        image = self.font2.render("DINO", 1, color)
        rect = image.get_rect(topleft=((WIDTH - image.get_width()) // 2, (HEIGHT - image.get_height()) // 2))

        return image, rect

    def draw_bg(self):

        if self.start_btn.draw(self.window):
            self.game_class.is_active_start = True
            self.running = False

        elif self.quit_btn.draw(self.window):
            self.running = False
            self.game_class.play = False

    def draw_loading(self):
        pygame.draw.rect(self.window, 'black',
                         rect=(
                             (WIDTH - self.loading_width) // 2 - 15,
                             (HEIGHT - self.loading_height) // 2 - 15,
                             self.loading_width + 30,
                             self.loading_height + 30,
                         ),
                         border_radius=10, )
        pygame.draw.rect(self.window, "brown",
                         rect=(
                             (WIDTH - self.loading_width) // 2,
                             (HEIGHT - self.loading_height) // 2,
                             self.l_width,
                             self.loading_height,

                         ),
                         border_radius=10, )

    def run(self):

        dino_text_image, dino_text_rect = self.get_dino_text("lime")

        while self.running:
            self.window.fill("white")
            self.window.blit(self.image, self.rect)
            self.window.blit(dino_text_image, dino_text_rect)

            if self.is_feed and not self.is_restart:
                self.draw_surface()
            else:
                if not self.is_loaded and not self.is_restart:
                    if self.l_width < self.loading_width:
                        self.l_width += self.load_speed
                        if self.load_speed > 2.9:
                            self.load_speed -= 0.4
                    else:
                        self.l_width = 0
                        self.is_loaded = True
                    self.draw_loading()
                    self.change_state_counter = pygame.time.get_ticks()
                else:
                    self.draw_bg()
                    current_time_counter = pygame.time.get_ticks()
                    if current_time_counter - self.change_state_counter > self.change_state_timer:
                        self.change_state_counter = pygame.time.get_ticks()
                        self.change_state_timer = random.randint(5000, 10000)
                        self.animate_dino.change_state("Walk")

                    self.animate_dino.draw()
                    self.animate_dino.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.game_class.play = False
                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_t:
                        self.game_class.scene.take_screenshot()
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        self.game_class.play = False

                    if event.key == pygame.K_RETURN and self.is_loaded:
                        self.game_class.is_active_start = True
                        self.running = False

            pygame.display.update()
            self.clock.tick(self.game_class.FPS)


class FailScreen:
    def __init__(self, scene, font_name: str = None, font_size: int = None):
        self.scene: Scene = scene
        self.font = SysFont(font_name, int(font_size * WIN_SCALE), True)

        self.surface = pygame.Surface(WIN_SIZE)
        self.surface.fill("black")
        self.surface.set_alpha(200)
        self.rect = self.surface.get_rect(topleft=(0, -HEIGHT))
        self.surface_speed = 4

        self.restart_btn: Button = self.get_restart_button()
        self.quit_btn: Button = self.get_quit_button()
        self.start_screen_btn: Button = self.get_start_screen_button()

        self.taken_image = None

    def get_restart_button(self, color: str | tuple = "black") -> Button:
        image = self.font.render(f"Restart", True, color)
        btn = Button(
            image,
            x=(WIDTH - image.get_width()) // 2,
            y=(HEIGHT - image.get_height()) // 2 + 5,
        )

        return btn

    def get_taken_screenshot(self):
        image_name = os.listdir("screenshots")[-1]
        image = load(f"screenshots/{image_name}").convert_alpha()
        image = pygame.transform.smoothscale(image, (WIDTH // 3, HEIGHT // 3))
        image = pygame.transform.rotate(image, 15)
        return image

    def get_quit_button(self, color: str | tuple = "black") -> Button:
        image = self.font.render(f"Quit", True, color)
        btn = Button(
            image,
            x=(WIDTH - image.get_width()) // 2 + 70 * WIN_SCALE,
            y=(HEIGHT - image.get_height()) // 3 + 10,
        )

        return btn

    def get_start_screen_button(self, color: str | tuple = "black") -> Button:
        image = self.font.render(f"Home", True, color)
        btn = Button(
            image,
            x=(WIDTH - image.get_width()) // 2 - 70 * WIN_SCALE,
            y=(HEIGHT - image.get_height()) // 3 + 10,
        )

        return btn

    def draw_surface(self, color: str | tuple = "black"):

        self.scene.window.blit(self.surface, self.rect)
        if self.rect.bottom < HEIGHT:
            self.rect.y += self.surface_speed
        else:
            self.draw_buttons()
            self.scene.score_table.draw(20, 20, int(self.scene.score), "white")
            self.scene.bg_speed_table.draw(20, 70, int(self.scene.bg.speed), "white")
            self.scene.timer_table.draw_timer(20, 120, self.scene.timer, "white")

            if self.taken_image:
                self.scene.window.blit(self.taken_image, (25, HEIGHT // 4))

    def draw_buttons(self):

        if self.start_screen_btn.draw(self.scene.window):
            self.scene.running = False
            self.scene.game_class.scene = Scene(self.scene.game_class)
            self.scene.game_class.start_screen = StartScreen(self.scene.game_class, is_restart=True)
            self.scene.game_class.is_active_start = False
            self.scene.game_class.GRAVITY = GRAVITY

        elif self.quit_btn.draw(self.scene.window):
            self.scene.game_class.play = False
            self.scene.running = False

        elif self.restart_btn.draw(self.scene.window):
            self.scene.game_class.start_screen = StartScreen(self.scene.game_class, is_restart=True)
            self.scene.game_class.scene = Scene(self.scene.game_class)
            self.scene.running = False
            self.scene.game_class.GRAVITY = GRAVITY
            Helicopter.retry_speed()
            Obstacle.retry_anim_speed()
            Obstacle.retry_speed()


class PauseScreen:
    def __init__(self, scene):
        self.scene: Scene = scene

        self.font = SysFont("arial", int(40 * WIN_SCALE), True)

        self.surface = pygame.Surface((WIDTH // 2, HEIGHT // 2))
        self.surface.fill("white")
        self.surface.set_alpha(200)
        self.y = - self.surface.get_height()
        self.rect = self.surface.get_rect(topleft=(
            (WIDTH - self.surface.get_width()) // 2,
            (HEIGHT - self.surface.get_height()) // 2)
        )
        self.surface_speed = 5
        self.is_finished = False

        self.play_btn = self.get_play_button()
        self.console_btn = self.get_console_button()

        self.console = Console(self)
        self.console_active = False

    def draw_surface(self, color: str | tuple = "aqua"):
        # self.surface.fill(color)
        self.scene.window.blit(self.surface, self.rect)

        pygame.draw.rect(self.surface, color, (0, self.y, self.surface.get_width(), self.surface.get_height()))
        if self.y < 0:
            self.y += self.surface_speed
        else:
            self.is_finished = True

        if self.is_finished and not self.console_active:
            self.play_btn.draw(self.scene.window,
                               self.rect.x + (self.rect.width - self.play_btn.rect.width) // 2 - 75,
                               self.rect.y + (self.rect.height - self.play_btn.rect.height) // 2
                               )
            if self.play_btn.is_clicked:
                self.scene.is_pause = False
                self.play_btn.is_clicked = False

            self.console_btn.draw(self.scene.window,
                                  self.rect.x + (self.rect.width - self.console_btn.rect.width) // 2 + 75,
                                  self.rect.y + (self.rect.height - self.console_btn.rect.height) // 2
                                  )

            if self.console_btn.is_clicked:
                self.console_btn.is_clicked = False
                self.console_active = True

        if self.console_active:
            self.console.draw()

    def get_play_button(self):
        image = load("assets/others/play.png").convert_alpha()
        image = scale(image, (100, 100))
        return ImageButton(image,
                           self.rect.x + (self.rect.width - image.get_width()) // 2 - 75,
                           self.rect.y + (self.rect.height - image.get_height()) // 2
                           )

    def get_console_button(self):
        image = load("assets/others/command-line.png").convert_alpha()
        image = scale(image, (100, 100))
        return ImageButton(image,
                           self.rect.x + (self.rect.width - image.get_width()) // 2 + 75,
                           self.rect.y + (self.rect.height - image.get_height()) // 2
                           )


class Scene:

    def __init__(self, game_class):

        self.game_class: Game = game_class

        self.window: pygame.Surface = pygame.display.set_mode(WIN_SIZE)
        pygame.display.set_caption('Dino')
        self.clock = pygame.time.Clock()

        self.bg_speed = 4
        self.running = True
        self.is_pause = False
        self.is_freeze = True
        self.is_change_speed = False

        self.fail_screen = FailScreen(self, "tlwgtypo", int(40 * SCALE))
        self.pause_screen: PauseScreen = PauseScreen(self)
        self.dino = Dino(self, 200 * SCALE, HEIGHT - 3 * TILE_SIZE, DINO_WIDTH, DINO_HEIGHT)
        self.bg = Bg(self)

        self.obstacle_list: list = []
        self.obstacle_dict: dict = {}
        self.generate_duration: int = 200
        self.generate_ticks: int = 0
        self.generate_counter: int = 0

        self.rotate_ticks: int = 0
        self.generate_random: int = 0
        self.timer: int = 0
        self.timer_counter: int = 0

        self.font = SysFont("tlwgtypo", int(100 * WIN_SCALE), True)

        self.score: int = 0
        self.score_table = Write(self, "Score")
        self.bg_speed_table = Write(self, "BG Speed")
        self.timer_table = Write(self, "Timer")
        self.take_scr = True
        self.saved_key = None

    def take_screenshot(self):
        os.makedirs("screenshots", exist_ok=True)
        # time_taken = time.asctime(time.localtime(time.time()))
        # time_taken = time_taken.replace(" ", "_")
        # time_taken = time_taken.replace(":", "_")
        generate = 1
        file_name = f"{generate}.png"
        while file_name in os.listdir("screenshots"):
            file_name = f"{generate}.png"
            generate += 1
        save_file = f"screenshots/{file_name}"
        pygame.image.save(self.window, save_file)

    def get_freeze_state(self, freeze_start_time, seconds=4):
        current_freeze_time = time.perf_counter()
        if current_freeze_time - freeze_start_time < seconds:
            self.bg.speed = 0
            self.dino.change_state("Idle")
        else:
            self.bg.speed = self.bg_speed
            self.dino.change_state("Run")
            self.is_freeze = False

        return int((current_freeze_time - freeze_start_time) // 1), seconds

    def generate_obstacle(self):
        generate_type_number = random.randint(1, 10)

        if self.generate_counter > self.generate_duration:
            self.generate_counter = 0
            if generate_type_number < 8:
                x = random.randint(WIDTH + self.generate_random, WIDTH + 100 + self.generate_random)
                obstacle = Obstacle(self, x, HEIGHT - 2 * TILE_SIZE + 5)
            else:
                x = random.randint(WIDTH + 10, WIDTH + 20)
                obstacle = Helicopter(self, HELICOPTER_WIDTH, int(HELICOPTER_HEIGHT), x,
                                      HEIGHT - 2 * TILE_SIZE - self.dino.height // 1.5)

            self.obstacle_list.append(obstacle)
            self.generate_ticks = pygame.time.get_ticks()

    def draw_freeze_time(self, freeze_time):
        result = freeze_time[1] - freeze_time[0] - 1

        if result < 1:
            result = "GO GO"
        text = f"{result}"
        image = self.font.render(text, True, "darkred")
        rect = image.get_rect(topleft=((WIDTH - image.get_width()) // 2, (HEIGHT - image.get_height()) // 2))

        self.window.blit(image, rect)

    def run(self):
        freeze_start_time = time.perf_counter()
        self.generate_ticks = pygame.time.get_ticks()
        self.rotate_ticks = pygame.time.get_ticks()

        image = cv2.imread("screenshots/1.png")

        while self.running:
            self.window.fill("white")

            self.bg.draw()
            if not self.is_pause:
                self.bg.update()

            self.score_table.draw(20, 20, int(self.score))
            self.bg_speed_table.draw(20, 70, self.bg.speed)
            self.timer_table.draw_timer(20, 120, self.timer, "black")

            if self.is_freeze and not self.is_pause:
                freeze_time = self.get_freeze_state(freeze_start_time)
                self.draw_freeze_time(freeze_time)
            else:
                freeze_start_time = time.perf_counter()

            if self.dino.alive and not self.is_pause and not self.is_freeze:
                self.generate_obstacle()
                self.generate_counter += 1
                self.timer_counter += 1

                if self.timer_counter >= self.game_class.FPS:
                    self.timer_counter = 0
                    self.timer += 1

            if self.obstacle_list:
                for index, obstacle in enumerate(self.obstacle_list):
                    if obstacle.is_active:
                        obstacle.draw()

                        if self.dino.alive and not self.is_pause:
                            obstacle.update()
                    # else:
                    #     self.obstacle_list.pop(index)

            self.dino.draw()
            if not self.is_pause:
                self.dino.update()

            if not self.is_freeze and not self.is_pause and self.dino.alive:
                self.score += 0.1 * 20

                self.dino.jump_force = -12 * SCALE - 20
                self.game_class.GRAVITY = 0.55 * SCALE + 2

                if int(self.score) != 0:
                    if not round(self.score, 2) % 100:
                        if self.bg.speed < 16:
                            self.bg.speed += 1
                            # self.dino.jump_force -= 1
                            # self.game_class.GRAVITY += 0.1

                        if self.dino.down_timer > 20:
                            self.dino.down_timer -= 2

                    if not round(self.score, 2) % 175 and self.dino.anim_speed > 2:
                        self.dino.is_change_speed = True

                    if not round(self.score, 2) % 250 and self.generate_duration > 33:
                        self.generate_duration -= 20
                        if self.generate_duration < 33:
                            self.generate_duration = 33

                    if not round(self.score, 2) % 200:
                        if Helicopter.SPEED < 3:
                            Helicopter.add_speed()
                        if Obstacle.SPEED < 3:
                            Obstacle.add_speed()
                        Obstacle.change_anim_speed()

            if self.is_pause:
                self.pause_screen.draw_surface()

            if not self.dino.alive and not self.is_pause:
                self.fail_screen.draw_surface()
                if self.take_scr:
                    self.take_screenshot()
                    self.fail_screen.taken_image = self.fail_screen.get_taken_screenshot()
                    self.take_scr = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.game_class.play = False

                if event.type == pygame.KEYDOWN:
                    if self.pause_screen.console_active and self.pause_screen.console.input_active:
                        key = event.key
                        if event.key in (1073742053, 1073742049):
                            self.saved_key = event.key
                            continue
                        if self.saved_key is not None:
                            self.saved_key = None
                            if event.key == 45:
                                key += 50
                            elif event.key == 59:
                                key -= 1
                        if event.key == 8:
                            self.pause_screen.console.text = self.pause_screen.console.text[:-1]
                        else:
                            try:
                                self.pause_screen.console.text += event.unicode
                            except Exception as e:
                                print(e)
                        if event.key == pygame.K_RETURN:
                            self.pause_screen.console.commands.append(
                                self.pause_screen.console.font.render(
                                    self.pause_screen.console.text,
                                    True,
                                    'white'
                                )
                            )
                            self.pause_screen.console.check_command(self.pause_screen.console.text)
                            self.pause_screen.console.text = ""

                    if event.key == pygame.K_ESCAPE:
                        if self.pause_screen.console_active:
                            self.pause_screen.console_active = False
                        elif self.is_pause:
                            self.is_pause = False
                        else:
                            self.running = False
                            self.game_class.play = False

                    if event.key == pygame.K_t:
                        self.take_screenshot()


                    if not self.is_pause:

                        if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                            if self.dino.alive and self.dino.on_ground and self.dino.state != "Idle":
                                self.dino.is_jumping = True

                        if event.key in (pygame.K_s, pygame.K_DOWN) and self.dino.state not in ("Idle", "Down", "Jump"):
                            self.dino.change_state("Down")
                            self.dino.down_ticks = pygame.time.get_ticks()

                        if event.key == pygame.K_r:
                            self.is_pause = not self.is_pause

            pygame.display.update()
            self.clock.tick(self.game_class.FPS)


class Game:

    def __init__(self):
        self.FPS = 60
        self.play = True
        self.commands = []

        self.GRAVITY = GRAVITY * SCALE

        self.scene = Scene(self)
        self.start_screen = StartScreen(self, )
        self.is_active_start = True if DEBUG else False

    def remove_dirs(self):
        image_names = os.listdir("screenshots")
        while image_names:
            image_name = image_names.pop()
            os.remove(f"screenshots/{image_name}")

    def run(self):
        while self.play:
            self.remove_dirs()
            if self.is_active_start:
                self.scene.run()
            else:
                self.start_screen.run()
                # self.scene.run()


if __name__ == '__main__':
    game = Game()
    game.run()
    pygame.quit()
