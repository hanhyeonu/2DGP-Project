from pico2d import load_image, draw_rectangle
import game_framework
import game_world
import play_mode
import math


class BossSeed:
    """보스의 씨앗 공격"""
    image = None

    def __init__(self, x, y, angle):
        if BossSeed.image is None:
            BossSeed.image = load_image('2DGP_resource/forestboss/forest_boss_spike.png')

        self.x = x
        self.y = y
        self.angle = angle  # 날아가는 방향 (라디안)

        # 속도 (화살보다 느림)
        self.speed = 150  # 픽셀/초

        # 방향 벡터 계산
        self.dir_x = math.cos(angle)
        self.dir_y = math.sin(angle)

        # 히트 여부
        self.has_hit = False

    def update(self):
        # 이동
        self.x += self.dir_x * self.speed * game_framework.frame_time
        self.y += self.dir_y * self.speed * game_framework.frame_time

        # 화면 밖으로 나가면 제거
        if self.x < -100 or self.x > 2148 or self.y < -100 or self.y > 2148:
            game_world.remove_object(self)

    def draw(self, camera=None):
        # 스크롤링 적용
        if hasattr(play_mode, 'background') and play_mode.background:
            screen_x = (self.x - play_mode.background.window_left) * play_mode.background.zoom
            screen_y = (self.y - play_mode.background.window_bottom) * play_mode.background.zoom
            size = int(20 * play_mode.background.zoom)
            bb_half_size = int(10 * play_mode.background.zoom)
        else:
            screen_x = self.x
            screen_y = self.y
            size = 20
            bb_half_size = 10

        # 씨앗 그리기
        self.image.draw(screen_x, screen_y, size, size)

        # 바운딩 박스
        draw_rectangle(
            screen_x - bb_half_size, screen_y - bb_half_size,
            screen_x + bb_half_size, screen_y + bb_half_size
        )

    def get_bb(self):
        """바운딩 박스"""
        return self.x - 10, self.y - 10, self.x + 10, self.y + 10

    def handle_collision(self, group, other):
        if group == 'boss_attack:player' and not self.has_hit:
            self.has_hit = True
            # 플레이어에게 데미지
            if hasattr(other, 'take_damage'):
                other.take_damage(10)
            # 씨앗 제거
            game_world.remove_object(self)
