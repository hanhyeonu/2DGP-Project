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
    # 55x55 그리드 기반 스프라이트 좌표
    SPRITE_COORDS = {
        1: {'y': 495, 'frames': 3},   # 오른쪽/왼쪽
        4: {'y': 440, 'frames': 3},   # 위
        0: {'y': 385, 'frames': 3}    # 아래
    }

    def __init__(self, attacker):
        self.attacker = attacker

    def enter(self, e):
        self.attacker.frame = 0

    def exit(self, e):
        pass

    def do(self):
        # 프레임 업데이트 (3프레임)
        self.attacker.frame = (self.attacker.frame + 6 * game_framework.frame_time) % 3

        # 쿨타임 감소
        if self.attacker.cooldown_timer > 0:
            self.attacker.cooldown_timer -= game_framework.frame_time

        # 충돌 해제되고 쿨타임 끝나면 Move로
        if self.attacker.target_player:
            if not game_world.collide(self.attacker, self.attacker.target_player) and self.attacker.cooldown_timer <= 0:
                self.attacker.state_machine.cur_state = self.attacker.MOVE
                self.attacker.MOVE.enter(('START_CHASE', None))

    def draw(self):
        # face_dir에 따른 스프라이트 선택 및 flip 처리
        dir_key = abs(self.attacker.face_dir) if abs(self.attacker.face_dir) == 1 else self.attacker.face_dir

        if dir_key in self.SPRITE_COORDS:
            coords = self.SPRITE_COORDS[dir_key]
            frame = int(self.attacker.frame) % coords['frames']
            flip = 'h' if self.attacker.face_dir == -1 else ''

            self.attacker.image.clip_composite_draw(
                frame * 55, coords['y'], 55, 55,
                0, flip,
                self.attacker.x, self.attacker.y, 55, 55
            )


class Move:
    # 55x55 그리드 기반 스프라이트 좌표
    SPRITE_COORDS = {
        1: {'y': 330, 'frames': 3},   # 오른쪽/왼쪽
        4: {'y': 275, 'frames': 3},   # 위
        0: {'y': 220, 'frames': 3}    # 아래
    }

    def __init__(self, attacker):
        self.attacker = attacker

    def enter(self, e):
        self.attacker.frame = 0

    def exit(self, e):
        pass

    def do(self):
        # 프레임 업데이트 (3프레임)
        self.attacker.frame = (self.attacker.frame + 6 * game_framework.frame_time) % 3

        # 쿨타임 감소
        if self.attacker.cooldown_timer > 0:
            self.attacker.cooldown_timer -= game_framework.frame_time

        if self.attacker.target_player:
            # 플레이어와의 거리 계산
            dx = self.attacker.target_player.x - self.attacker.x
            dy = self.attacker.target_player.y - self.attacker.y
            distance = math.sqrt(dx**2 + dy**2)

            # 공격 범위 안이고 쿨타임이 끝났을 때만 공격
            if distance < self.attacker.attack_range and self.attacker.cooldown_timer <= 0:
                # Attack 상태로 전환
                self.attacker.state_machine.cur_state = self.attacker.ATTACK
                self.attacker.ATTACK.enter(('ATTACK', None))
            elif distance > 0:
                # 플레이어 방향으로 이동
                self.attacker.dir_x = dx / distance
                self.attacker.dir_y = dy / distance

                speed = self.attacker.chase_speed * game_framework.frame_time
                self.attacker.x += self.attacker.dir_x * speed
                self.attacker.y += self.attacker.dir_y * speed

                # 화면 경계 체크
                self.attacker.x = max(0, min(1024, self.attacker.x))
                self.attacker.y = max(0, min(1024, self.attacker.y))

                # face_dir 업데이트 (4방향: 1, -1, 0, 4)
                if abs(dx) > abs(dy):
                    self.attacker.face_dir = 1 if dx > 0 else -1
                else:
                    self.attacker.face_dir = 4 if dy > 0 else 0

    def draw(self):
        # face_dir에 따른 스프라이트 선택 및 flip 처리
        dir_key = abs(self.attacker.face_dir) if abs(self.attacker.face_dir) == 1 else self.attacker.face_dir

        if dir_key in self.SPRITE_COORDS:
            coords = self.SPRITE_COORDS[dir_key]
            frame = int(self.attacker.frame) % coords['frames']
            flip = 'h' if self.attacker.face_dir == -1 else ''

            self.attacker.image.clip_composite_draw(
                frame * 55, coords['y'], 55, 55,
                0, flip,
                self.attacker.x, self.attacker.y, 55, 55
            )


class EnemyAttacker:
    def __init__(self, player=None):
        self.x, self.y = 600, 300
        self.frame = 0
        self.face_dir = 1
        self.dir_x = 0
        self.dir_y = 0
        self.image = load_image('EnemyAttacker.png')
        self.target_player = player
        self.attack_range = 60  # 매우 가까이 접근해야 공격
        self.chase_speed = 70  # 중간 속도
        self.attack_cooldown = 1.5  # 빠른 공격 쿨타임
        self.cooldown_timer = 0

        # 상태 생성
        self.IDLE = Idle(self)
        self.MOVE = Move(self)

        # 상태머신 설정
        self.state_machine = StateMachine(self.IDLE, {})

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.x - 22, self.y - 22, self.x + 22, self.y + 22

    def handle_collision(self, group, other):
        pass
