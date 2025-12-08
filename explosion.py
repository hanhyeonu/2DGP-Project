from pico2d import load_image, draw_rectangle
import game_framework
import game_world
import play_mode


class Explosion:
    """폭발 애니메이션 및 히트박스"""
    image = None

    def __init__(self, x, y):
        if Explosion.image is None:
            Explosion.image = load_image('explode.png')

        self.x = x
        self.y = y
        self.frame = 0
        self.total_frames = 7
        self.animation_speed = 14  # 7프레임 * 2 = 초당 14 업데이트 (0.5초 재생)
        self.is_finished = False

        # 히트박스 크기 (64x64로 2배)
        self.hitbox_size = 64
        self.has_hit_player = False  # 플레이어를 이미 때렸는지 체크

    def update(self):
        # 애니메이션 프레임 업데이트
        self.frame += self.animation_speed * game_framework.frame_time

        # 애니메이션 종료
        if self.frame >= self.total_frames:
            self.is_finished = True
            game_world.remove_object(self)

    def draw(self, camera=None):
        # 스크롤링 적용
        if hasattr(play_mode, 'background') and play_mode.background:
            screen_x = (self.x - play_mode.background.window_left) * play_mode.background.zoom
            screen_y = (self.y - play_mode.background.window_bottom) * play_mode.background.zoom
            draw_width = int(64 * play_mode.background.zoom)  # 2배 크기
            draw_height = int(64 * play_mode.background.zoom)  # 2배 크기
            bb_half_size = int(32 * play_mode.background.zoom)  # 2배 크기
        else:
            screen_x = self.x
            screen_y = self.y
            draw_width = 64  # 2배 크기
            draw_height = 64  # 2배 크기
            bb_half_size = 32  # 2배 크기

        # 현재 프레임 그리기
        frame_index = int(self.frame)
        if frame_index < self.total_frames:
            self.image.clip_draw(frame_index * 32, 0, 32, 32, screen_x, screen_y, draw_width, draw_height)

        # 바운딩 박스 그리기
        draw_rectangle(
            screen_x - bb_half_size, screen_y - bb_half_size,
            screen_x + bb_half_size, screen_y + bb_half_size
        )

    def get_bb(self):
        """바운딩 박스 (64x64로 2배)"""
        return self.x - 32, self.y - 32, self.x + 32, self.y + 32

    def handle_collision(self, group, other):
        """플레이어와 충돌 시 데미지"""
        if group == 'explosion:player' and not self.has_hit_player:
            self.has_hit_player = True
            # 플레이어의 take_damage 함수를 호출
            if hasattr(other, 'take_damage'):
                other.take_damage(10)
