from pico2d import load_image, draw_rectangle
import game_framework
import play_mode


class Gate:
    """맵 전환용 게이트"""
    image = None

    def __init__(self, x, y):
        if Gate.image is None:
            Gate.image = load_image('gate.png')

        self.x = x
        self.y = y
        self.frame = 0
        self.total_frames = 7
        self.animation_speed = 14  # 7프레임 * 2 = 초당 14 업데이트

    def update(self):
        # 애니메이션 프레임 업데이트
        self.frame = (self.frame + self.animation_speed * game_framework.frame_time) % self.total_frames

    def draw(self, camera=None):
        # 스크롤링 적용
        if hasattr(play_mode, 'background') and play_mode.background:
            screen_x = (self.x - play_mode.background.window_left) * play_mode.background.zoom
            screen_y = (self.y - play_mode.background.window_bottom) * play_mode.background.zoom
            draw_width = int(48 * play_mode.background.zoom)
            draw_height = int(64 * play_mode.background.zoom)
            bb_half_width = int(24 * play_mode.background.zoom)
            bb_half_height = int(32 * play_mode.background.zoom)
        else:
            screen_x = self.x
            screen_y = self.y
            draw_width = 48
            draw_height = 64
            bb_half_width = 24
            bb_half_height = 32

        # 애니메이션 프레임 그리기 (48x64 크기, 7프레임)
        frame_index = int(self.frame)
        self.image.clip_composite_draw(
            frame_index * 48, 0, 48, 64,
            0, '',
            screen_x, screen_y, draw_width, draw_height
        )

        # 바운딩 박스 그리기
        # draw_rectangle(
        #     screen_x - bb_half_width, screen_y - bb_half_height,
        #     screen_x + bb_half_width, screen_y + bb_half_height
        # )

    def get_bb(self):
        """바운딩 박스 (48x64)"""
        return self.x - 24, self.y - 32, self.x + 24, self.y + 32

    def handle_collision(self, group, other):
        """플레이어와 충돌 시 맵 전환"""
        if group == 'player:gate':
            print(f"Player collided with gate at ({self.x}, {self.y})")
            # 맵 전환은 play_mode에서 처리
