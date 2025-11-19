from pico2d import load_image, draw_rectangle
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
        # 모든 방향 동일 - 행 1 사용
        frame = int(self.slime.frame) % 5
        self.slime.image.clip_composite_draw(
            frame * 50, 200, 50, 50,
            0, '',
            self.slime.draw_x if hasattr(self.slime, 'draw_x') else self.slime.x, self.slime.draw_y if hasattr(self.slime, 'draw_y') else self.slime.y, 50, 50
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
            distance = math.sqrt(dx**2 + dy**2)

            # 공격 범위 안이고 쿨타임 끝나면 공격
            if distance < self.slime.attack_range and self.slime.cooldown_timer <= 0:
                self.slime.state_machine.cur_state = self.slime.ATTACK
                self.slime.ATTACK.enter(('ATTACK', None))
            elif distance > 0:
                # 이동
                self.slime.dir_x = dx / distance
                self.slime.dir_y = dy / distance

                speed = self.slime.chase_speed * game_framework.frame_time
                self.slime.x += self.slime.dir_x * speed
                self.slime.y += self.slime.dir_y * speed

                # 화면 경계 체크
                self.slime.x = max(0, min(1024, self.slime.x))
                self.slime.y = max(0, min(1024, self.slime.y))

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
                        self.slime.face_dir = 2   # 우상
                    elif dx < 0 and dy > 0:
                        self.slime.face_dir = -2  # 좌상
                    elif dx > 0 and dy < 0:
                        self.slime.face_dir = 3   # 우하
                    else:
                        self.slime.face_dir = -3  # 좌하

    def draw(self):
        # 모든 방향 동일 - 행 2 사용
        frame = int(self.slime.frame) % 7
        self.slime.image.clip_composite_draw(
            frame * 50, 150, 50, 50,
            0, '',
            self.slime.draw_x if hasattr(self.slime, 'draw_x') else self.slime.x, self.slime.draw_y if hasattr(self.slime, 'draw_y') else self.slime.y, 50, 50
        )


class Attack:
    def __init__(self, slime):
        self.slime = slime
        self.attack_duration = 0.6
        self.attack_timer = 0
        self.dash_speed = 250
        self.target_x = 0
        self.target_y = 0
        self.dash_dir_x = 0
        self.dash_dir_y = 0

    def enter(self, e):
        self.attack_timer = 0
        self.slime.frame = 0

        if self.slime.target_player:
            self.target_x = self.slime.target_player.x
            self.target_y = self.slime.target_player.y

            dx = self.target_x - self.slime.x
            dy = self.target_y - self.slime.y
            distance = math.sqrt(dx**2 + dy**2)

            if distance > 0:
                self.dash_dir_x = dx / distance
                self.dash_dir_y = dy / distance
            else:
                self.dash_dir_x = 0
                self.dash_dir_y = 0

    def exit(self, e):
        pass

    def do(self):
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
            dash_distance = self.dash_speed * game_framework.frame_time
            self.slime.x += self.dash_dir_x * dash_distance
            self.slime.y += self.dash_dir_y * dash_distance

            # 화면 경계 체크
            self.slime.x = max(0, min(1024, self.slime.x))
            self.slime.y = max(0, min(1024, self.slime.y))
        else:
            self.slime.cooldown_timer = self.slime.attack_cooldown
            self.slime.state_machine.cur_state = self.slime.MOVE
            self.slime.MOVE.enter(('TIME_OUT', None))

    def draw(self):
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
            self.slime.draw_x if hasattr(self.slime, 'draw_x') else self.slime.x, self.slime.draw_y if hasattr(self.slime, 'draw_y') else self.slime.y, 50, 50
        )


class EnemySlime:
    def __init__(self, player=None):
        self.x, self.y = 700, 500  # 개구리와 다른 위치
        self.frame = 0
        self.face_dir = 1
        self.dir_x = 0
        self.dir_y = 0
        self.image = load_image('EnemySlime.png')
        self.target_player = player
        self.attack_range = 120  # 개구리보다 조금 더 먼 거리에서 공격
        self.chase_speed = 50  # 개구리보다 느림
        self.attack_cooldown = 2.5  # 쿨타임 2.5초
        self.cooldown_timer = 0

        # 상태 생성
        self.IDLE = Idle(self)
        self.MOVE = Move(self)
        self.ATTACK = Attack(self)

        # 상태머신 설정
        self.state_machine = StateMachine(self.IDLE, {})

    def update(self):
        self.state_machine.update()

    def draw(self, camera=None):
        if camera:
            self.draw_x, self.draw_y = camera.apply(self.x, self.y)
        else:
            self.draw_x, self.draw_y = self.x, self.y

        self.state_machine.draw()

        if camera:
            bb = self.get_bb()
            offset_x = self.draw_x - self.x
            offset_y = self.draw_y - self.y
            draw_rectangle(
                bb[0] + offset_x, bb[1] + offset_y,
                bb[2] + offset_x, bb[3] + offset_y
            )
        else:
            draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.x - 20, self.y - 20, self.x + 20, self.y + 20

    def handle_collision(self, group, other):
        pass
