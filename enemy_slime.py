import common
import play_mode
from pico2d import load_image, draw_rectangle, get_canvas_width, get_canvas_height, clamp
import game_framework
from state_machine import StateMachine
import game_world
import math

PIXEL_PER_METER = (10.0 / 0.3)
RUN_SPEED_KMPH = 10.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION


class Idle:
    def __init__(self, slime):
        self.slime = slime

    def enter(self, e):
        self.slime.frame = 0

    def exit(self, e):
        pass

    def do(self):
        # 프레임 업데이트 (5프레임)
        self.slime.frame = (self.slime.frame + 10 * game_framework.frame_time) % 5

        # 쿨타임 감소
        if self.slime.cooldown_timer > 0:
            self.slime.cooldown_timer -= game_framework.frame_time

        # 충돌 해제되고 쿨타임 끝나면 Move로
        if self.slime.target_player:
            if not game_world.collide(self.slime, self.slime.target_player) and self.slime.cooldown_timer <= 0:
                self.slime.state_machine.cur_state = self.slime.MOVE
                self.slime.MOVE.enter(('START_CHASE', None))

    def draw(self):
        # 깜빡임 처리
        if self.slime.hit_timer > 0 and int(self.slime.hit_timer * 10) % 2 == 1:
            return

        if hasattr(play_mode, 'background') and play_mode.background:
            screen_x = (self.slime.x - play_mode.background.window_left) * play_mode.background.zoom
            screen_y = (self.slime.y - play_mode.background.window_bottom) * play_mode.background.zoom
            size = int(50 * play_mode.background.zoom)
        else:
            screen_x = self.slime.x
            screen_y = self.slime.y
            size = 50

        # 모든 방향 동일 - 행 1 사용
        frame = int(self.slime.frame) % 5
        self.slime.image.clip_composite_draw(
            frame * 50, 200, 50, 50,
            0, '',
            screen_x, screen_y, size, size
        )


class Move:
    def __init__(self, slime):
        self.slime = slime

    def enter(self, e):
        self.slime.frame = 0

    def exit(self, e):
        pass

    def do(self):
        # 프레임 업데이트 (7프레임)
        self.slime.frame = (self.slime.frame + 14 * game_framework.frame_time) % 7

        # 쿨타임 감소
        if self.slime.cooldown_timer > 0:
            self.slime.cooldown_timer -= game_framework.frame_time

        if self.slime.target_player:
            dx = self.slime.target_player.x - self.slime.x
            dy = self.slime.target_player.y - self.slime.y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            # 추적 거리 밖이면 Idle로 전환
            if distance > self.slime.chase_range:
                self.slime.state_machine.cur_state = self.slime.IDLE
                self.slime.IDLE.enter(('OUT_OF_RANGE', None))
                return

            # 공격 범위 안이고 쿨타임 끝나면 공격
            if distance < self.slime.attack_range and self.slime.cooldown_timer <= 0:
                self.slime.state_machine.cur_state = self.slime.ATTACK
                self.slime.ATTACK.enter(('ATTACK', None))
            elif distance > 0:
                # 이동
                self.slime.dir_x = dx / distance
                self.slime.dir_y = dy / distance

                # 이동 전 위치 저장
                prev_x, prev_y = self.slime.x, self.slime.y

                speed = self.slime.chase_speed * game_framework.frame_time
                self.slime.x += self.slime.dir_x * speed
                self.slime.y += self.slime.dir_y * speed

                # 벽 충돌 체크
                import play_mode
                if hasattr(play_mode, 'background') and play_mode.background:
                    if play_mode.background.is_wall_at(self.slime.x, self.slime.y):
                        self.slime.x = prev_x
                        self.slime.y = prev_y

                # 월드 좌표 범위 제한 (0 ~ 2048)
                self.slime.x = max(0, min(2048, self.slime.x))
                self.slime.y = max(0, min(2048, self.slime.y))

                # face_dir 업데이트 (8방향 지원)
                if abs(dx) > abs(dy) * 2:
                    # 좌우가 압도적
                    self.slime.face_dir = 1 if dx > 0 else -1
                elif abs(dy) > abs(dx) * 2:
                    # 상하가 압도적
                    self.slime.face_dir = 4 if dy > 0 else 0
                else:
                    # 대각선
                    if dx > 0 and dy > 0:
                        self.slime.face_dir = 2  # 우상
                    elif dx < 0 and dy > 0:
                        self.slime.face_dir = -2  # 좌상
                    elif dx > 0 and dy < 0:
                        self.slime.face_dir = 3  # 우하
                    else:
                        self.slime.face_dir = -3  # 좌하

    def draw(self):
        # 깜빡임 처리
        if self.slime.hit_timer > 0 and int(self.slime.hit_timer * 10) % 2 == 1:
            return

        if hasattr(play_mode, 'background') and play_mode.background:
            screen_x = (self.slime.x - play_mode.background.window_left) * play_mode.background.zoom
            screen_y = (self.slime.y - play_mode.background.window_bottom) * play_mode.background.zoom
            size = int(50 * play_mode.background.zoom)
        else:
            screen_x = self.slime.x
            screen_y = self.slime.y
            size = 50

        # 모든 방향 동일 - 행 2 사용
        frame = int(self.slime.frame) % 7
        self.slime.image.clip_composite_draw(
            frame * 50, 150, 50, 50,
            0, '',
            screen_x, screen_y, size, size
        )


class Attack:
    def __init__(self, slime):
        self.slime = slime
        self.attack_duration = 0.6
        self.attack_timer = 0
        self.dash_speed = 125  # 250 -> 125로 감소
        self.target_x = 0
        self.target_y = 0
        self.dash_dir_x = 0
        self.dash_dir_y = 0

    def enter(self, e):
        self.attack_timer = 0
        self.slime.frame = 0
        self.hitbox_created = False

        if self.slime.target_player:
            self.target_x = self.slime.target_player.x
            self.target_y = self.slime.target_player.y

            dx = self.target_x - self.slime.x
            dy = self.target_y - self.slime.y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            if distance > 0:
                self.dash_dir_x = dx / distance
                self.dash_dir_y = dy / distance
            else:
                self.dash_dir_x = 0
                self.dash_dir_y = 0

    def exit(self, e):
        pass

    def do(self):
        # 히트박스는 돌진 시작 시 한 번만 생성
        if not self.hitbox_created:
            from attack_hitbox import AttackHitbox

            hitbox = AttackHitbox(self.slime, self.slime.x, self.slime.y,
                                 50, 50, 0.6)
            game_world.add_object(hitbox, 3)
            game_world.add_collision_pair('monster_attack:player', hitbox, None)
            self.hitbox_created = True

        self.attack_timer += game_framework.frame_time

        # 프레임 업데이트 (5프레임)
        self.slime.frame = (self.slime.frame + 10 * game_framework.frame_time) % 5

        # 충돌 검사
        if self.slime.target_player and game_world.collide(self.slime, self.slime.target_player):
            self.slime.cooldown_timer = self.slime.attack_cooldown
            self.slime.state_machine.cur_state = self.slime.IDLE
            self.slime.IDLE.enter(('COLLISION', None))
            return

        # 돌진
        if self.attack_timer < self.attack_duration:
            # 이동 전 위치 저장
            prev_x, prev_y = self.slime.x, self.slime.y

            dash_distance = self.dash_speed * game_framework.frame_time
            self.slime.x += self.dash_dir_x * dash_distance
            self.slime.y += self.dash_dir_y * dash_distance

            # 벽 충돌 체크
            import play_mode
            if hasattr(play_mode, 'background') and play_mode.background:
                if play_mode.background.is_wall_at(self.slime.x, self.slime.y):
                    self.slime.x = prev_x
                    self.slime.y = prev_y

            # 월드 좌표 범위 제한 (0 ~ 2048)
            self.slime.x = max(0, min(2048, self.slime.x))
            self.slime.y = max(0, min(2048, self.slime.y))
        else:
            self.slime.cooldown_timer = self.slime.attack_cooldown
            self.slime.state_machine.cur_state = self.slime.MOVE
            self.slime.MOVE.enter(('TIME_OUT', None))

    def draw(self):
        # 깜빡임 처리
        if self.slime.hit_timer > 0 and int(self.slime.hit_timer * 10) % 2 == 1:
            return

        if hasattr(play_mode, 'background') and play_mode.background:
            screen_x = (self.slime.x - play_mode.background.window_left) * play_mode.background.zoom
            screen_y = (self.slime.y - play_mode.background.window_bottom) * play_mode.background.zoom
            size = int(50 * play_mode.background.zoom)
        else:
            screen_x = self.slime.x
            screen_y = self.slime.y
            size = 50

        frame = int(self.slime.frame) % 5

        # face_dir에 따라 다른 행 사용
        if self.slime.face_dir in [1, 2, 3]:  # 오른쪽, 우상, 우하
            y = 100  # 행 3
            flip = ''
        elif self.slime.face_dir in [-1, -2, -3]:  # 왼쪽, 좌상, 좌하
            y = 100  # 행 3
            flip = 'h'
        elif self.slime.face_dir == 4:  # 위
            y = 50  # 행 4
            flip = ''
        else:  # face_dir == 0, 아래
            y = 0  # 행 5
            flip = ''

        self.slime.image.clip_composite_draw(
            frame * 50, y, 50, 50,
            0, flip,
            screen_x, screen_y, size, size
        )


class EnemySlime:
    def __init__(self, player=None):
        # 월드 좌표로 초기화
        self.x, self.y = 700, 1600  # 개구리와 다른 위치
        self.frame = 0
        self.face_dir = 1
        self.dir_x = 0
        self.dir_y = 0
        self.image = load_image('EnemySlime.png')
        self.target_player = player
        self.attack_range = 120  # 개구리보다 조금 더 먼 거리에서 공격
        self.chase_speed = 50  # 개구리보다 느림
        self.attack_cooldown = 4.0  # 쿨타임 4.0초
        self.cooldown_timer = 0
        self.chase_range = 300  # 300픽셀 이내만 추적
        self.background = None  # 벽 충돌용

        # 체력 시스템
        self.hp = 2
        self.is_dead = False

        # 피격 깜빡임 시스템
        self.hit_timer = 0
        self.hit_duration = 0.5

        # 중복 히트 방지 (이미 맞은 히트박스 추적)
        self.hit_by_hitboxes = set()

        # 상태 생성
        self.IDLE = Idle(self)
        self.MOVE = Move(self)
        self.ATTACK = Attack(self)

        # 상태머신 설정
        self.state_machine = StateMachine(self.IDLE, {})

    def update(self):
        self.state_machine.update()

        # 피격 깜빡임 타이머 감소
        if self.hit_timer > 0:
            self.hit_timer -= game_framework.frame_time

    def draw(self, camera=None):
        if hasattr(play_mode, 'background') and play_mode.background:
            screen_x = (self.x - play_mode.background.window_left) * play_mode.background.zoom
            screen_y = (self.y - play_mode.background.window_bottom) * play_mode.background.zoom
            bb_half_size = int(25 * play_mode.background.zoom)
        else:
            screen_x = self.x
            screen_y = self.y
            bb_half_size = 25

        self.state_machine.draw()

        # 바운딩 박스
        draw_rectangle(
            screen_x - bb_half_size, screen_y - bb_half_size,
            screen_x + bb_half_size, screen_y + bb_half_size
        )

    def get_bb(self):
        """바운딩 박스 (50x50)"""
        return self.x - 25, self.y - 25, self.x + 25, self.y + 25

    def handle_collision(self, group, other):
        # 이미 죽었으면 무시
        if self.is_dead:
            return

        if group == 'player_attack:monster':
            # 같은 히트박스로부터는 한 번만 데미지 받기
            if other in self.hit_by_hitboxes:
                return
            self.hit_by_hitboxes.add(other)

            self.hp -= 1
            print(f"Slime hit! HP: {self.hp}")

            if self.hp <= 0:
                self.is_dead = True
                import game_world
                game_world.remove_object(self)
                print("Slime defeated!")

        elif group == 'arrow:monster':
            # 화살은 별도 처리 (화살 자체가 한 번만 맞음)
            self.hp -= 1
            print(f"Slime hit by arrow! HP: {self.hp}")

            if self.hp <= 0:
                self.is_dead = True
                import game_world
                game_world.remove_object(self)
                print("Slime defeated!")