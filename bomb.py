from pico2d import load_image
import game_framework
import game_world
import math


class Bomb:
    image = None

    def __init__(self, start_x, start_y, target_x, target_y):
        if Bomb.image == None:
            Bomb.image = load_image('bomb.png')

        self.x = start_x
        self.y = start_y
        self.start_x = start_x
        self.start_y = start_y
        self.target_x = target_x
        self.target_y = target_y

        # 이동 시간 및 속도 계산
        self.flight_time = 1.0  # 1초 동안 비행
        self.elapsed_time = 0

        # 수평 거리와 속도
        self.dx = target_x - start_x
        self.dy_ground = target_y - start_y
        self.horizontal_speed = self.dx / self.flight_time
        self.vertical_ground_speed = self.dy_ground / self.flight_time

        # 포물선을 위한 초기 수직 속도 (위로 올라갔다 내려옴)
        self.initial_vertical_velocity = 200  # 위로 200 픽셀/초
        self.gravity = 400  # 중력 가속도

    def update(self):
        self.elapsed_time += game_framework.frame_time

        # 비행 시간 종료 시 폭탄 제거
        if self.elapsed_time >= self.flight_time:
            game_world.remove_object(self)
            return

        # 수평 이동 (등속 운동)
        self.x = self.start_x + self.horizontal_speed * self.elapsed_time

        # 수직 이동 (포물선 운동)
        # y = y0 + v0*t - 0.5*g*t^2 + (목표 지면 높이까지의 선형 이동)
        parabola_y = self.initial_vertical_velocity * self.elapsed_time - 0.5 * self.gravity * (self.elapsed_time ** 2)
        ground_y = self.start_y + self.vertical_ground_speed * self.elapsed_time

        self.y = ground_y + parabola_y

    def draw(self, camera=None):
        # 스크롤링: 플레이어 기준으로 화면 좌표 계산 (줌 적용)
        from pico2d import get_canvas_width, get_canvas_height, clamp
        import common

        zoom = common.background.zoom
        camera_width = common.background.camera_width
        camera_height = common.background.camera_height

        window_left = clamp(0, int(common.player.x) - camera_width // 2, 2048 - camera_width)
        window_bottom = clamp(0, int(common.player.y) - camera_height // 2, 2048 - camera_height)

        draw_x = (self.x - window_left) * zoom
        draw_y = (self.y - window_bottom) * zoom

        self.image.draw(draw_x, draw_y, int(30 * zoom), int(30 * zoom))

    def get_bb(self):
        return self.x - 15, self.y - 15, self.x + 15, self.y + 15

    def handle_collision(self, group, other):
        pass