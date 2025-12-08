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

    def __init__(self, player=None):
        # 이미지 로드
        if ForestBoss.body_image is None:
            ForestBoss.body_image = load_image('2DGP_resource/forestboss/forest_boss.png')
            ForestBoss.hand_image = load_image('2DGP_resource/forestboss/forest_boss_hand.png')
            ForestBoss.face_wait_image = load_image('2DGP_resource/forestboss/forest_boss_face_wait.png')
            ForestBoss.face_attack_image = load_image('2DGP_resource/forestboss/forest_boss_face_attack.png')
            ForestBoss.face_damage_image = load_image('2DGP_resource/forestboss/forest_boss_face_damage.png')

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

        # 12개의 씨앗을 원뿔 형태로 발사
        # 아래쪽 방향 (270도 = -π/2)을 중심으로 좌우 60도 범위
        center_angle = -math.pi / 2  # 아래쪽
        spread_angle = math.pi / 3  # 60도 (라디안)

        for i in range(12):
            # -30도 ~ +30도 범위로 균등 분포
            angle = center_angle + (spread_angle * (i - 5.5) / 11)
            seed = BossSeed(self.x, self.y, angle)
            game_world.add_object(seed, 1)

            # 씨앗-플레이어 충돌 등록
            if self.target_player:
                game_world.add_collision_pair('boss_attack:player', seed, self.target_player)

    def root_attack(self):
        """뿌리 공격"""
        from boss_root import BossRoot

        self.face_state = 'attack'
        self.face_frame = 0

        if self.target_player:
            # 플레이어 현재 위치에 뿌리 생성
            root = BossRoot(self.target_player.x, self.target_player.y)
            game_world.add_object(root, 1)

            # 뿌리-플레이어 충돌 등록
            game_world.add_collision_pair('boss_attack:player', root, self.target_player)

    def draw(self, camera=None):
        if self.is_dead:
            return

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

        if show_sprite:
            # 1. 몸체 그리기 (forest_boss.png)
            # 추정 크기: 약 400x600
            body_width = int(400 * zoom)
            body_height = int(600 * zoom)
            self.body_image.draw(screen_x, screen_y, body_width, body_height)

            # 2. 손 그리기 (양쪽)
            hand_width = int(160 * zoom)
            hand_height = int(80 * zoom)
            hand_frame = int(self.hand_frame)
            hand_offset_x = int(200 * zoom)  # 몸체로부터의 거리
            hand_offset_y = int(50 * zoom)

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

            # 3. 얼굴 그리기
            face_width = int(96 * zoom)
            face_height = int(96 * zoom)
            face_offset_y = int(200 * zoom)  # 몸체 위쪽
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

        # 바운딩 박스 그리기 (300x300, 뿌리 부분)
        bb_half_size = int(150 * zoom)
        bb_offset_y = int(-150 * zoom)  # 아래쪽으로 이동
        draw_rectangle(
            screen_x - bb_half_size, screen_y + bb_offset_y - bb_half_size,
            screen_x + bb_half_size, screen_y + bb_offset_y + bb_half_size
        )

    def get_bb(self):
        """바운딩 박스 (뿌리 부분, 300x300)"""
        # 중심에서 아래쪽으로 150 이동
        bb_center_y = self.y - 150
        return self.x - 150, bb_center_y - 150, self.x + 150, bb_center_y + 150

    def handle_collision(self, group, other):
        if self.is_dead:
            return

        if group == 'player_attack:monster':
            # 중복 히트 방지
            if other in self.hit_by_hitboxes:
                return
            self.hit_by_hitboxes.add(other)

            self.hp -= 1
            self.hit_timer = self.hit_duration
            self.face_state = 'damage'
            print(f"Boss hit! HP: {self.hp}/{self.max_hp}")

            if self.hp <= 0:
                self.is_dead = True
                game_world.remove_object(self)
                print("Boss defeated!")

        elif group == 'arrow:monster':
            self.hp -= 1
            self.hit_timer = self.hit_duration
            self.face_state = 'damage'
            print(f"Boss hit by arrow! HP: {self.hp}/{self.max_hp}")

            if self.hp <= 0:
                self.is_dead = True
                game_world.remove_object(self)
                print("Boss defeated!")
