from pico2d import load_image, draw_rectangle
import game_framework
import game_world
import play_mode


class BossRoot:
    """보스의 뿌리 공격"""
    image = None

    def __init__(self, target_x, target_y):
        if BossRoot.image is None:
            BossRoot.image = load_image('2DGP_resource/forestboss/forest_boss_root.png')

        # 맨 아래 좌표를 타겟 위치에 맞춤
        self.x = target_x
        self.bottom_y = target_y
        # 중심 y 좌표 계산 (32x96 크기이므로 중심은 bottom + 48)
        self.y = self.bottom_y + 48

        # 애니메이션
        self.frame = 0
        self.total_frames = 9
        self.animation_speed = 18  # 9프레임 * 2 = 초당 18 업데이트

        # 경고 시간
        self.warning_time = 1.0  # 1초 동안 첫 프레임 표시
        self.warning_timer = 0
        self.is_warning = True

        # 히트박스 활성화
        self.hitbox_active = False
        self.has_hit = False

        # 애니메이션 종료
        self.is_finished = False

    def update(self):
        if self.is_warning:
            # 경고 중 (1초 동안 첫 프레임)
            self.warning_timer += game_framework.frame_time
            if self.warning_timer >= self.warning_time:
                self.is_warning = False
                self.hitbox_active = True
                self.frame = 0
        else:
            # 애니메이션 재생
            self.frame += self.animation_speed * game_framework.frame_time

            # 애니메이션 종료
            if self.frame >= self.total_frames:
                self.is_finished = True
                game_world.remove_object(self)
                return

    def draw(self, camera=None):
        # 스크롤링 적용
        if hasattr(play_mode, 'background') and play_mode.background:
            screen_x = (self.x - play_mode.background.window_left) * play_mode.background.zoom
            screen_y = (self.y - play_mode.background.window_bottom) * play_mode.background.zoom
            width = int(32 * play_mode.background.zoom)
            height = int(96 * play_mode.background.zoom)
            bb_half_width = int(16 * play_mode.background.zoom)
            bb_half_height = int(48 * play_mode.background.zoom)
        else:
            screen_x = self.x
            screen_y = self.y
            width = 32
            height = 96
            bb_half_width = 16
            bb_half_height = 48

        # 뿌리 그리기
        frame_index = int(self.frame) if not self.is_warning else 0
        if frame_index < self.total_frames:
            self.image.clip_draw(
                frame_index * 32, 0, 32, 96,
                screen_x, screen_y, width, height
            )

        # 바운딩 박스 (히트박스 활성화 시에만)
        # if self.hitbox_active:
        #     draw_rectangle(
        #         screen_x - bb_half_width, screen_y - bb_half_height,
        #         screen_x + bb_half_width, screen_y + bb_half_height
        #     )

    def get_bb(self):
        """바운딩 박스 (히트박스 활성화 시에만)"""
        if self.hitbox_active and not self.is_finished:
            return self.x - 16, self.y - 48, self.x + 16, self.y + 48
        else:
            # 비활성화 시 충돌 없음
            return 0, 0, 0, 0

    def handle_collision(self, group, other):
        if group == 'boss_attack:player' and self.hitbox_active and not self.has_hit:
            self.has_hit = True
            # 플레이어에게 데미지
            if hasattr(other, 'take_damage'):
                other.take_damage(10)
