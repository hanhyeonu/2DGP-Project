from pico2d import load_image, draw_rectangle
import game_world
import game_framework
import play_mode
import math

# Arrow Speed
PIXEL_PER_METER = (10.0 / 0.3)
ARROW_SPEED_KMPH = 60.0
ARROW_SPEED_MPM = (ARROW_SPEED_KMPH * 1000.0 / 60.0)
ARROW_SPEED_MPS = (ARROW_SPEED_MPM / 60.0)
ARROW_SPEED_PPS = (ARROW_SPEED_MPS * PIXEL_PER_METER)

MAX_DISTANCE = 250


class Arrow:
    image = None

    def __init__(self, x, y, face_dir, custom_angle=None):
        if Arrow.image == None:
            Arrow.image = load_image('arrow.png')

        self.x, self.y = x, y
        self.face_dir = face_dir
        self.start_x, self.start_y = x, y

        self.dir_x = 0
        self.dir_y = 0
        self.angle = 0

        if custom_angle is not None:
            self.angle = custom_angle
            self.dir_x = math.cos(custom_angle)
            self.dir_y = math.sin(custom_angle)
        else:
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

        # 벽 충돌 체크 (타일맵 기반)
        import common
        if common.background.is_wall_at(self.x, self.y):
            game_world.remove_object(self)
            return

    def draw(self, camera=None):
        if hasattr(play_mode, 'background') and play_mode.background:
            screen_x = self.x - play_mode.background.window_left
            screen_y = self.y - play_mode.background.window_bottom
        else:
            screen_x = self.x
            screen_y = self.y

        self.image.composite_draw(self.angle, '', screen_x, screen_y, 20, 20)

        # 바운딩 박스 그리기
        bb_half_size = 10
        draw_rectangle(
            screen_x - bb_half_size, screen_y - bb_half_size,
            screen_x + bb_half_size, screen_y + bb_half_size
        )

    def get_bb(self):
        return self.x - 10, self.y - 10, self.x + 10, self.y + 10

    def handle_collision(self, group, other):
        # 화살의 충돌 처리 (벽은 타일맵 체크로 처리됨)
        pass