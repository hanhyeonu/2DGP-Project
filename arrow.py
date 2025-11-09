from pico2d import load_image
import game_world
import game_framework
import math

PIXEL_PER_METER = (10.0 / 0.3)
ARROW_SPEED_KMPH = 60.0
ARROW_SPEED_MPM = (ARROW_SPEED_KMPH * 1000.0 / 60.0)
ARROW_SPEED_MPS = (ARROW_SPEED_MPM / 60.0)
ARROW_SPEED_PPS = (ARROW_SPEED_MPS * PIXEL_PER_METER)

MAX_DISTANCE = 500


class Arrow:
    image = None

    def __init__(self, x, y, face_dir):
        if Arrow.image == None:
            Arrow.image = load_image('arrow.png')

        self.x, self.y = x, y
        self.face_dir = face_dir
        self.start_x, self.start_y = x, y

        self.dir_x = 0
        self.dir_y = 0
        self.angle = 0

        if face_dir == 1:
            self.dir_x, self.dir_y = 1, 0
            self.angle = 0
        elif face_dir == -1:
            self.dir_x, self.dir_y = -1, 0
            self.angle = math.pi
        elif face_dir == 2:
            self.dir_x, self.dir_y = 1, 1
            self.angle = math.pi / 4
        elif face_dir == -2:
            self.dir_x, self.dir_y = -1, 1
            self.angle = math.pi * 3 / 4
        elif face_dir == 3:
            self.dir_x, self.dir_y = 1, -1
            self.angle = -math.pi / 4
        elif face_dir == -3:
            self.dir_x, self.dir_y = -1, -1
            self.angle = -math.pi * 3 / 4
        elif face_dir == 4:
            self.dir_x, self.dir_y = 0, 1
            self.angle = math.pi / 2
        elif face_dir == 0:
            self.dir_x, self.dir_y = 0, -1
            self.angle = -math.pi / 2

        length = math.sqrt(self.dir_x ** 2 + self.dir_y ** 2)
        if length > 0:
            self.dir_x /= length
            self.dir_y /= length

    def update(self):
        distance = math.sqrt((self.x - self.start_x) ** 2 + (self.y - self.start_y) ** 2)
        if distance > MAX_DISTANCE:
            game_world.remove_object(self)
            return

        self.x += self.dir_x * ARROW_SPEED_PPS * game_framework.frame_time
        self.y += self.dir_y * ARROW_SPEED_PPS * game_framework.frame_time

    def draw(self):
        self.image.composite_draw(self.angle, '', self.x, self.y, 20, 20)