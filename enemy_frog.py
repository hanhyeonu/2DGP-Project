from pico2d import load_image, draw_rectangle
import game_framework
from state_machine import StateMachine
import math
import random

PIXEL_PER_METER = (10.0 / 0.3)
RUN_SPEED_KMPH = 10.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION


def time_out(e):
    return e[0] == 'TIME_OUT'


def attack_range_in(e):
    return e[0] == 'ATTACK_RANGE_IN'


def attack_finished(e):
    return e[0] == 'ATTACK_FINISHED'


class Idle:
    # 40x40 그리드 기반 스프라이트 좌표
    SPRITE_COORDS = {
        1: {'y': 240, 'frames': 3},   # 오른쪽/왼쪽
        0: {'y': 200, 'frames': 3},   # 아래
        4: {'y': 160, 'frames': 3}    # 위
    }

    def __init__(self, frog):
        self.frog = frog

    def enter(self, e):
        self.frog.dir_x = 0
        self.frog.dir_y = 0
        self.frog.idle_timer = 1.0  # 1초 후 Move로 전환
        self.frog.frame = 0

    def exit(self, e):
        pass

    def do(self):
        # 3프레임 애니메이션
        self.frog.frame = (self.frog.frame + 6 * game_framework.frame_time) % 3

        # 타이머 업데이트
        self.frog.idle_timer -= game_framework.frame_time
        if self.frog.idle_timer <= 0:
            self.frog.state_machine.handle_state_event(('TIME_OUT', 0))

    def draw(self):
        # face_dir에 따른 스프라이트 선택 및 flip 처리
        dir_key = abs(self.frog.face_dir) if abs(self.frog.face_dir) == 1 else self.frog.face_dir

        if dir_key in self.SPRITE_COORDS:
            coords = self.SPRITE_COORDS[dir_key]
            frame = int(self.frog.frame) % coords['frames']
            flip = 'h' if self.frog.face_dir == -1 else ''

            self.frog.image.clip_composite_draw(
                frame * 40, coords['y'], 40, 40,
                0, flip,
                self.frog.x, self.frog.y, 40, 40
            )


class Move:
    # 40x40 그리드 기반 스프라이트 좌표
    SPRITE_COORDS = {
        1: {'y': 120, 'frames': 5},   # 오른쪽/왼쪽
        0: {'y': 80, 'frames': 5},    # 아래
        4: {'y': 40, 'frames': 5}     # 위
    }

    def __init__(self, frog):
        self.frog = frog

    def enter(self, e):
        self.frog.frame = 0

    def exit(self, e):
        pass

    def do(self):
        # 5프레임 애니메이션
        self.frog.frame = (self.frog.frame + 10 * game_framework.frame_time) % 5

        if self.frog.target_player:
            # 플레이어와의 거리 계산
            dx = self.frog.target_player.x - self.frog.x
            dy = self.frog.target_player.y - self.frog.y
            distance = math.sqrt(dx**2 + dy**2)

            if distance < self.frog.attack_range:
                # Attack 상태로 전환
                self.frog.state_machine.handle_state_event(('ATTACK_RANGE_IN', 0))
            elif distance > 0:
                # 플레이어 방향으로 이동
                self.frog.dir_x = dx / distance
                self.frog.dir_y = dy / distance

                speed = self.frog.chase_speed * game_framework.frame_time
                self.frog.x += self.frog.dir_x * speed
                self.frog.y += self.frog.dir_y * speed

                # 화면 경계 체크
                self.frog.x = max(0, min(1024, self.frog.x))
                self.frog.y = max(0, min(1024, self.frog.y))

                # face_dir 업데이트 (주 방향만: 1, -1, 0, 4)
                if abs(dx) > abs(dy):
                    self.frog.face_dir = 1 if dx > 0 else -1
                else:
                    self.frog.face_dir = 4 if dy > 0 else 0

    def draw(self):
        # face_dir에 따른 스프라이트 선택 및 flip 처리
        dir_key = abs(self.frog.face_dir) if abs(self.frog.face_dir) == 1 else self.frog.face_dir

        if dir_key in self.SPRITE_COORDS:
            coords = self.SPRITE_COORDS[dir_key]
            frame = int(self.frog.frame) % coords['frames']
            flip = 'h' if self.frog.face_dir == -1 else ''

            self.frog.image.clip_composite_draw(
                frame * 40, coords['y'], 40, 40,
                0, flip,
                self.frog.x, self.frog.y, 40, 40
            )


class Attack:
    # 40x40 그리드 기반 스프라이트 좌표 (행 7, y=0)
    SPRITE_COORDS = {
        1: {'x': 0, 'y': 0},     # 오른쪽/왼쪽
        0: {'x': 40, 'y': 0},    # 아래
        4: {'x': 80, 'y': 0}     # 위
    }

    def __init__(self, frog):
        self.frog = frog
        self.attack_duration = 0.5
        self.attack_timer = 0

    def enter(self, e):
        self.attack_timer = 0

    def exit(self, e):
        pass

    def do(self):
        self.attack_timer += game_framework.frame_time
        if self.attack_timer >= self.attack_duration:
            # Move 상태로 복귀
            self.frog.state_machine.handle_state_event(('ATTACK_FINISHED', 0))

    def draw(self):
        # face_dir에 따른 스프라이트 선택 및 flip 처리
        dir_key = abs(self.frog.face_dir) if abs(self.frog.face_dir) == 1 else self.frog.face_dir

        if dir_key in self.SPRITE_COORDS:
            coords = self.SPRITE_COORDS[dir_key]
            flip = 'h' if self.frog.face_dir == -1 else ''

            self.frog.image.clip_composite_draw(
                coords['x'], coords['y'], 40, 40,
                0, flip,
                self.frog.x, self.frog.y, 40, 40
            )


class EnemyFrog:
    def __init__(self, player=None):
        self.x, self.y = 500, 500
        self.frame = 0
        self.face_dir = 1
        self.dir_x = 0
        self.dir_y = 0
        self.idle_timer = 0
        self.image = load_image('EnemyFrog.png')
        self.target_player = player
        self.attack_range = 80
        self.chase_speed = 100  # 픽셀/초

        # 상태 생성
        self.IDLE = Idle(self)
        self.MOVE = Move(self)
        self.ATTACK = Attack(self)

        # 상태머신 설정
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {time_out: self.MOVE},
                self.MOVE: {attack_range_in: self.ATTACK},
                self.ATTACK: {attack_finished: self.MOVE}
            }
        )

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.x - 15, self.y - 15, self.x + 15, self.y + 15

    def handle_collision(self, group, other):
        pass
