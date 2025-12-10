from pico2d import load_image, draw_rectangle
import game_framework
import game_world
import play_mode
import math


class ForestBoss:
    """숲의 보스 몬스터"""

    # 이미지 로드 (클래스 변수)
    body_image = None
    hand_image = None
    face_wait_image = None
    face_attack_image = None
    face_damage_image = None
    health_bar_image = None
    ending_image = None

    def __init__(self, player=None):
        # 이미지 로드
        if ForestBoss.body_image is None:
            ForestBoss.body_image = load_image('2DGP_resource/forestboss/forest_boss.png')
            ForestBoss.hand_image = load_image('2DGP_resource/forestboss/forest_boss_hand.png')
            ForestBoss.face_wait_image = load_image('2DGP_resource/forestboss/forest_boss_face_wait.png')
            ForestBoss.face_attack_image = load_image('2DGP_resource/forestboss/forest_boss_face_attack.png')
            ForestBoss.face_damage_image = load_image('2DGP_resource/forestboss/forest_boss_face_damage.png')
            ForestBoss.health_bar_image = load_image('LifeBarUDying.png')
            ForestBoss.ending_image = load_image('opening.png')

        # 맵 중앙에 위치 (2048x2048 맵)
        self.x = 1024
        self.y = 1024

        # 타겟 플레이어
        self.target_player = player

        # 손 애니메이션 (8프레임)
        self.hand_frame = 0
        self.hand_total_frames = 8
        self.hand_animation_speed = 16  # 초당 16 업데이트

        # 얼굴 상태 및 애니메이션
        self.face_state = 'wait'  # 'wait', 'attack', 'damage'
        self.face_frame = 0

        # 체력 시스템
        self.max_hp = 100
        self.hp = 100
        self.is_dead = False

        # 엔딩 시스템
        self.show_ending = False
        self.ending_timer = 0
        self.ending_wait_time = 3.0  # 3초 대기
        self.ending_stage = 0  # 0: 정상, 1: 보스 사망, 2: 엔딩 이미지 표시, 3: 게임 종료

        # 피격 깜빡임
        self.hit_timer = 0
        self.hit_duration = 0.5

        # 공격 시스템
        self.attack_type = 1  # 1=씨앗, 2=뿌리
        self.attack_cooldown = {1: 5.0, 2: 5.0}  # 각 공격 5초 쿨타임
        self.attack_timer = {1: 0, 2: 0}
        self.attack_switch_delay = 3.0  # 공격 전환 시 3초 대기
        self.switch_timer = 0
        self.is_attacking = False

        # 중복 히트 방지
        self.hit_by_hitboxes = set()

    def update(self):
        # 엔딩 처리
        if self.ending_stage > 0:
            self.ending_timer += game_framework.frame_time

            if self.ending_stage == 1:  # 보스 사망 후 대기
                if self.ending_timer >= self.ending_wait_time:
                    self.ending_stage = 2
                    self.ending_timer = 0
                    self.show_ending = True

            elif self.ending_stage == 2:  # 엔딩 이미지 표시 후 대기
                if self.ending_timer >= self.ending_wait_time:
                    self.ending_stage = 3
                    game_framework.quit()  # 게임 종료
            return

        if self.is_dead:
            return

        # 손 애니메이션 업데이트
        self.hand_frame = (self.hand_frame + self.hand_animation_speed * game_framework.frame_time) % self.hand_total_frames

        # 얼굴 애니메이션 업데이트
        if self.face_state == 'wait':
            self.face_frame = (self.face_frame + 8 * game_framework.frame_time) % 4
        elif self.face_state == 'attack':
            self.face_frame = (self.face_frame + 6 * game_framework.frame_time) % 3
        # damage는 애니메이션 없음

        # 피격 타이머 감소
        if self.hit_timer > 0:
            self.hit_timer -= game_framework.frame_time
            if self.hit_timer <= 0:
                self.face_state = 'wait'

        # 공격 쿨타임 감소
        for attack in [1, 2]:
            if self.attack_timer[attack] > 0:
                self.attack_timer[attack] -= game_framework.frame_time

        # 공격 전환 타이머 감소
        if self.switch_timer > 0:
            self.switch_timer -= game_framework.frame_time

        # 공격 로직
        self.update_attack()

    def update_attack(self):
        """공격 패턴 업데이트"""
        if self.switch_timer > 0:
            return  # 공격 전환 중

        # 현재 공격 가능한지 확인
        if self.attack_timer[self.attack_type] <= 0:
            # 공격 실행
            if self.attack_type == 1:
                self.seed_attack()
            elif self.attack_type == 2:
                self.root_attack()

            # 쿨타임 시작
            self.attack_timer[self.attack_type] = self.attack_cooldown[self.attack_type]

            # 다음 공격으로 전환
            self.attack_type = 2 if self.attack_type == 1 else 1
            self.switch_timer = self.attack_switch_delay

    def seed_attack(self):
        """씨앗 던지기 공격"""
        from boss_seed import BossSeed

        self.face_state = 'attack'
        self.face_frame = 0

        if self.target_player:
            # 플레이어 방향을 중심으로 원뿔 형태로 발사
            dx = self.target_player.x - self.x
            dy = self.target_player.y - self.y
            center_angle = math.atan2(dy, dx)  # 플레이어 방향
            spread_angle = math.pi / 3  # 60도 (라디안)

            for i in range(12):
                # -30도 ~ +30도 범위로 균등 분포
                angle = center_angle + (spread_angle * (i - 5.5) / 11)
                seed = BossSeed(self.x, self.y, angle)
                game_world.add_object(seed, 1)

                # 씨앗-플레이어 충돌 등록
                game_world.add_collision_pair('boss_attack:player', seed, self.target_player)

    def root_attack(self):
        """뿌리 공격"""
        from boss_root import BossRoot

        self.face_state = 'attack'
        self.face_frame = 0

        if self.target_player:
            # 플레이어 현재 위치보다 10 아래에 뿌리 생성
            root = BossRoot(self.target_player.x, self.target_player.y - 10)
            game_world.add_object(root, 1)

            # 뿌리-플레이어 충돌 등록
            game_world.add_collision_pair('boss_attack:player', root, self.target_player)

    def draw(self, camera=None):
        # 엔딩 화면 표시
        if self.show_ending and self.ending_stage == 2:
            # 화면 전체에 엔딩 이미지 표시
            from pico2d import get_canvas_width, get_canvas_height
            canvas_width = get_canvas_width()
            canvas_height = get_canvas_height()
            self.ending_image.draw(canvas_width // 2, canvas_height // 2, canvas_width, canvas_height)
            return

        # 보스가 살아있으면 몸체, 손, 얼굴 그리기
        if not self.is_dead or self.ending_stage == 1:
            # 스크롤링 적용
            if hasattr(play_mode, 'background') and play_mode.background:
                screen_x = (self.x - play_mode.background.window_left) * play_mode.background.zoom
                screen_y = (self.y - play_mode.background.window_bottom) * play_mode.background.zoom
                zoom = play_mode.background.zoom
            else:
                screen_x = self.x
                screen_y = self.y
                zoom = 1.0

            # 깜빡임 처리
            show_sprite = True
            if self.hit_timer > 0 and int(self.hit_timer * 10) % 2 == 1:
                show_sprite = False

            if show_sprite and not self.is_dead:
                # 1. 몸체 그리기 (forest_boss.png)
                # 원본 이미지 크기 그대로 출력 (좌우 비율 수정)
                body_width = int(500 * zoom)  # 폭 증가 (400 -> 500)
                body_height = int(600 * zoom)
                self.body_image.draw(screen_x, screen_y, body_width, body_height)

                # 2. 손 그리기 (양쪽)
                hand_width = int(160 * zoom)
                hand_height = int(80 * zoom)
                hand_frame = int(self.hand_frame)
                hand_offset_x = int(200 * zoom)  # 몸체로부터의 거리
                hand_offset_y = int(-150 * zoom)  # 200 아래로 이동 (50 - 200 = -150)

                # 왼손 (원본 그대로)
                self.hand_image.clip_draw(
                    hand_frame * 160, 0, 160, 80,
                    screen_x - hand_offset_x, screen_y + hand_offset_y,
                    hand_width, hand_height
                )

                # 오른손 (좌우 반전)
                self.hand_image.clip_composite_draw(
                    hand_frame * 160, 0, 160, 80,
                    0, 'h',
                    screen_x + hand_offset_x, screen_y + hand_offset_y,
                    hand_width, hand_height
                )

            # 3. 얼굴 그리기 (보스가 살아있을 때만)
            if show_sprite and not self.is_dead:
                face_width = int(96 * zoom)
                face_height = int(96 * zoom)
                face_offset_y = int(-60 * zoom)  # 60 더 아래로 이동 (0 - 60 = -60)
                face_frame = int(self.face_frame)

                if self.face_state == 'wait':
                    self.face_wait_image.clip_draw(
                        face_frame * 96, 0, 96, 96,
                        screen_x, screen_y + face_offset_y,
                        face_width, face_height
                    )
                elif self.face_state == 'attack':
                    self.face_attack_image.clip_draw(
                        face_frame * 96, 0, 96, 96,
                        screen_x, screen_y + face_offset_y,
                        face_width, face_height
                    )
                elif self.face_state == 'damage':
                    self.face_damage_image.draw(
                        screen_x, screen_y + face_offset_y,
                        face_width, face_height
                    )

            # 바운딩 박스 그리기 (300x300, 뿌리 부분) - 살아있을 때만
            # if not self.is_dead:
            #     bb_half_size = int(150 * zoom)
            #     bb_offset_y = int(-150 * zoom)  # 아래쪽으로 이동
            #     draw_rectangle(
            #         screen_x - bb_half_size, screen_y + bb_offset_y - bb_half_size,
            #         screen_x + bb_half_size, screen_y + bb_offset_y + bb_half_size
            #     )

        # 체력바 그리기 (화면 하단에 고정)
        from pico2d import get_canvas_width, get_canvas_height, load_font
        canvas_width = get_canvas_width()
        canvas_height = get_canvas_height()

        # 체력바 위치 및 크기
        bar_width = 600  # 체력바 전체 폭
        bar_height = 60  # 체력바 높이
        bar_x = canvas_width // 2
        bar_y = 60  # 화면 하단에서 60픽셀 위

        # 현재 체력에 따른 체력바 길이 계산
        health_ratio = max(0, self.hp / self.max_hp)
        current_bar_width = int(bar_width * health_ratio)

        # 체력바 (현재 체력만큼만 그리기)
        if health_ratio > 0:
            # 원본 이미지에서 체력 비율만큼 clip하여 그리기
            clip_width = int(self.health_bar_image.w * health_ratio)
            self.health_bar_image.clip_draw(
                0, 0, clip_width, self.health_bar_image.h,
                bar_x - bar_width // 2 + current_bar_width // 2, bar_y,
                current_bar_width, bar_height
            )

        # 체력 텍스트 표시 (기본 폰트 사용)
        try:
            font = load_font(None, 24)  # 기본 폰트 사용
            font.draw(bar_x - 50, bar_y - 8, f"BOSS HP: {int(self.hp)}/{self.max_hp}", (255, 255, 255))
        except:
            pass  # 폰트 로드 실패시 텍스트 표시 안함

    def get_bb(self):
        """바운딩 박스 (뿌리 부분, 300x300)"""
        # 중심에서 아래쪽으로 150 이동
        bb_center_y = self.y - 150
        return self.x - 150, bb_center_y - 150, self.x + 150, bb_center_y + 150

    def handle_collision(self, group, other):
        if self.is_dead or self.ending_stage > 0:
            return

        if group == 'player_attack:monster':
            # 중복 히트 방지
            if other in self.hit_by_hitboxes:
                return
            self.hit_by_hitboxes.add(other)

            self.hp -= 5  # 1 -> 5로 변경 (20번 공격으로 체력 100 소진)
            self.hit_timer = self.hit_duration
            self.face_state = 'damage'
            print(f"Boss hit! HP: {self.hp}/{self.max_hp}")

            if self.hp <= 0:
                self.hp = 0
                self.is_dead = True
                self.ending_stage = 1  # 엔딩 시퀀스 시작
                self.ending_timer = 0
                print("Boss defeated! Ending sequence started.")

        elif group == 'arrow:monster':
            self.hp -= 5  # 1 -> 5로 변경
            self.hit_timer = self.hit_duration
            self.face_state = 'damage'
            print(f"Boss hit by arrow! HP: {self.hp}/{self.max_hp}")

            if self.hp <= 0:
                self.hp = 0
                self.is_dead = True
                self.ending_stage = 1  # 엔딩 시퀀스 시작
                self.ending_timer = 0
                print("Boss defeated! Ending sequence started.")
