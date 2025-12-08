from pico2d import load_image, draw_rectangle, get_canvas_width, get_canvas_height, clamp
import game_framework
import game_world
import common
import play_mode
from state_machine import StateMachine
import math

# Enemy Speed
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
    SPRITE_COORDS = {
        1: {'y': 240, 'frames': 3},
        0: {'y': 200, 'frames': 3},
        4: {'y': 160, 'frames': 3}
    }

    def __init__(self, frog):
        self.frog = frog

    def enter(self, e):
        self.frog.dir_x = 0
        self.frog.dir_y = 0
        self.frog.idle_timer = 1.0
        self.frog.frame = 0

    def exit(self, e):
        pass

    def do(self):
        self.frog.frame = (self.frog.frame + 6 * game_framework.frame_time) % 3

        if self.frog.cooldown_timer > 0:
            self.frog.cooldown_timer -= game_framework.frame_time

        if self.frog.target_player:
            if not game_world.collide(self.frog, self.frog.target_player) and self.frog.cooldown_timer <= 0:
                self.frog.state_machine.cur_state = self.frog.MOVE
                self.frog.MOVE.enter(('START_CHASE', None))

    def draw(self):
        if hasattr(play_mode, 'background') and play_mode.background:
            screen_x = (self.frog.x - play_mode.background.window_left) * play_mode.background.zoom
            screen_y = (self.frog.y - play_mode.background.window_bottom) * play_mode.background.zoom
            size = int(40 * play_mode.background.zoom)
        else:
            screen_x = self.frog.x
            screen_y = self.frog.y
            size = 40

        dir_key = abs(self.frog.face_dir) if abs(self.frog.face_dir) == 1 else self.frog.face_dir

        if dir_key in self.SPRITE_COORDS:
            coords = self.SPRITE_COORDS[dir_key]
            frame = int(self.frog.frame) % coords['frames']
            flip = 'h' if self.frog.face_dir == -1 else ''

            self.frog.image.clip_composite_draw(
                frame * 40, coords['y'], 40, 40,
                0, flip,
                screen_x, screen_y, size, size
            )


class Move:
    SPRITE_COORDS = {
        1: {'y': 120, 'frames': 5},
        0: {'y': 80, 'frames': 5},
        4: {'y': 40, 'frames': 5}
    }

    def __init__(self, frog):
        self.frog = frog

    def enter(self, e):
        self.frog.frame = 0

    def exit(self, e):
        pass

    def do(self):
        self.frog.frame = (self.frog.frame + 10 * game_framework.frame_time) % 5

        if self.frog.cooldown_timer > 0:
            self.frog.cooldown_timer -= game_framework.frame_time

        if self.frog.target_player:
            dx = self.frog.target_player.x - self.frog.x
            dy = self.frog.target_player.y - self.frog.y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            # 추적 거리 밖이면 Idle로 전환
            if distance > self.frog.chase_range:
                self.frog.state_machine.cur_state = self.frog.IDLE
                self.frog.IDLE.enter(('OUT_OF_RANGE', None))
                return

            if distance < self.frog.attack_range and self.frog.cooldown_timer <= 0:
                self.frog.state_machine.cur_state = self.frog.ATTACK
                self.frog.ATTACK.enter(('ATTACK', None))
            elif distance > 0:
                self.frog.dir_x = dx / distance
                self.frog.dir_y = dy / distance

                # 이동 전 위치 저장
                prev_x, prev_y = self.frog.x, self.frog.y

                speed = self.frog.chase_speed * game_framework.frame_time
                self.frog.x += self.frog.dir_x * speed
                self.frog.y += self.frog.dir_y * speed

                # 벽 충돌 체크
                if hasattr(play_mode, 'background') and play_mode.background:
                    if play_mode.background.is_wall_at(self.frog.x, self.frog.y):
                        self.frog.x = prev_x
                        self.frog.y = prev_y

                # 월드 좌표 범위 제한 (0 ~ 2048)
                self.frog.x = max(0, min(2048, self.frog.x))
                self.frog.y = max(0, min(2048, self.frog.y))

                if abs(dx) > abs(dy):
                    self.frog.face_dir = 1 if dx > 0 else -1
                else:
                    self.frog.face_dir = 4 if dy > 0 else 0

    def draw(self):
        if hasattr(play_mode, 'background') and play_mode.background:
            screen_x = (self.frog.x - play_mode.background.window_left) * play_mode.background.zoom
            screen_y = (self.frog.y - play_mode.background.window_bottom) * play_mode.background.zoom
            size = int(40 * play_mode.background.zoom)
        else:
            screen_x = self.frog.x
            screen_y = self.frog.y
            size = 40

        dir_key = abs(self.frog.face_dir) if abs(self.frog.face_dir) == 1 else self.frog.face_dir

        if dir_key in self.SPRITE_COORDS:
            coords = self.SPRITE_COORDS[dir_key]
            frame = int(self.frog.frame) % coords['frames']
            flip = 'h' if self.frog.face_dir == -1 else ''

            self.frog.image.clip_composite_draw(
                frame * 40, coords['y'], 40, 40,
                0, flip,
                screen_x, screen_y, size, size
            )


class Attack:
    SPRITE_COORDS = {
        1: {'x': 0, 'y': 0},
        0: {'x': 40, 'y': 0},
        4: {'x': 80, 'y': 0}
    }

    def __init__(self, frog):
        self.frog = frog
        self.attack_duration = 0.5
        self.attack_timer = 0
        self.dash_speed = 300
        self.target_x = 0
        self.target_y = 0
        self.dash_dir_x = 0
        self.dash_dir_y = 0

    def enter(self, e):
        self.attack_timer = 0

        if self.frog.target_player:
            self.target_x = self.frog.target_player.x
            self.target_y = self.frog.target_player.y

            dx = self.target_x - self.frog.x
            dy = self.target_y - self.frog.y
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
        self.attack_timer += game_framework.frame_time

        if self.frog.target_player and game_world.collide(self.frog, self.frog.target_player):
            self.frog.cooldown_timer = self.frog.attack_cooldown
            self.frog.state_machine.cur_state = self.frog.IDLE
            self.frog.IDLE.enter(('COLLISION', None))
            return

        if self.attack_timer < self.attack_duration:
            # 이동 전 위치 저장
            prev_x, prev_y = self.frog.x, self.frog.y

            dash_distance = self.dash_speed * game_framework.frame_time
            self.frog.x += self.dash_dir_x * dash_distance
            self.frog.y += self.dash_dir_y * dash_distance

            # 벽 충돌 체크
            if hasattr(play_mode, 'background') and play_mode.background:
                if play_mode.background.is_wall_at(self.frog.x, self.frog.y):
                    self.frog.x = prev_x
                    self.frog.y = prev_y

            # 월드 좌표 범위 제한 (0 ~ 2048)
            self.frog.x = max(0, min(2048, self.frog.x))
            self.frog.y = max(0, min(2048, self.frog.y))
        else:
            self.frog.cooldown_timer = self.frog.attack_cooldown
            self.frog.state_machine.cur_state = self.frog.MOVE
            self.frog.MOVE.enter(('TIME_OUT', None))

    def draw(self):
        if hasattr(play_mode, 'background') and play_mode.background:
            screen_x = (self.frog.x - play_mode.background.window_left) * play_mode.background.zoom
            screen_y = (self.frog.y - play_mode.background.window_bottom) * play_mode.background.zoom
            size = int(40 * play_mode.background.zoom)
        else:
            screen_x = self.frog.x
            screen_y = self.frog.y
            size = 40

        dir_key = abs(self.frog.face_dir) if abs(self.frog.face_dir) == 1 else self.frog.face_dir

        if dir_key in self.SPRITE_COORDS:
            coords = self.SPRITE_COORDS[dir_key]
            flip = 'h' if self.frog.face_dir == -1 else ''

            self.frog.image.clip_composite_draw(
                coords['x'], coords['y'], 40, 40,
                0, flip,
                screen_x, screen_y, size, size
            )


class EnemyFrog:
    def __init__(self, player=None):
        # 월드 좌표로 초기화 (플레이어 근처에 스폰)
        self.x, self.y = 500, 1700
        self.frame = 0
        self.face_dir = 1
        self.dir_x = 0
        self.dir_y = 0
        self.idle_timer = 0
        self.image = load_image('EnemyFrog.png')
        self.target_player = player
        self.attack_range = 100
        self.chase_speed = 60
        self.attack_cooldown = 2.0
        self.cooldown_timer = 0
        self.chase_range = 400  # 400픽셀 이내만 추적
        self.background = None  # 벽 충돌용

        self.IDLE = Idle(self)
        self.MOVE = Move(self)
        self.ATTACK = Attack(self)

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

    def draw(self, camera=None):
        if hasattr(play_mode, 'background') and play_mode.background:
            screen_x = (self.x - play_mode.background.window_left) * play_mode.background.zoom
            screen_y = (self.y - play_mode.background.window_bottom) * play_mode.background.zoom
            bb_half_size = int(15 * play_mode.background.zoom)
        else:
            screen_x = self.x
            screen_y = self.y
            bb_half_size = 15

        self.state_machine.draw()

        # 바운딩 박스
        draw_rectangle(
            screen_x - bb_half_size, screen_y - bb_half_size,
            screen_x + bb_half_size, screen_y + bb_half_size
        )

    def get_bb(self):
        return self.x - 15, self.y - 15, self.x + 15, self.y + 15

    def handle_collision(self, group, other):
        pass