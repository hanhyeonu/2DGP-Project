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
    # 55x55 그리드 기반 스프라이트 좌표
    SPRITE_COORDS = {
        1: {'y': 495, 'frames': 3},  # 오른쪽/왼쪽
        4: {'y': 440, 'frames': 3},  # 위
        0: {'y': 385, 'frames': 3}  # 아래
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
        # 깜빡임 처리
        if self.attacker.hit_timer > 0 and int(self.attacker.hit_timer * 10) % 2 == 1:
            return

        # face_dir에 따른 스프라이트 선택 및 flip 처리
        dir_key = abs(self.attacker.face_dir) if abs(self.attacker.face_dir) == 1 else self.attacker.face_dir

        if dir_key in self.SPRITE_COORDS:
            coords = self.SPRITE_COORDS[dir_key]
            frame = int(self.attacker.frame) % coords['frames']
            flip = 'h' if self.attacker.face_dir == -1 else ''

            if hasattr(self.attacker, 'draw_x'):
                size = int(55 * play_mode.background.zoom) if hasattr(play_mode, 'background') and play_mode.background else 55
            else:
                size = 55

            self.attacker.image.clip_composite_draw(
                frame * 55, coords['y'], 55, 55,
                0, flip,
                self.attacker.draw_x if hasattr(self.attacker, 'draw_x') else self.attacker.x,
                self.attacker.draw_y if hasattr(self.attacker, 'draw_y') else self.attacker.y, size, size
            )


class Move:
    # 55x55 그리드 기반 스프라이트 좌표
    SPRITE_COORDS = {
        1: {'y': 330, 'frames': 3},  # 오른쪽/왼쪽
        4: {'y': 275, 'frames': 3},  # 위
        0: {'y': 220, 'frames': 3}  # 아래
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
            distance = math.sqrt(dx ** 2 + dy ** 2)

            # 추적 거리 밖이면 Idle로 전환
            if distance > self.attacker.chase_range:
                self.attacker.state_machine.cur_state = self.attacker.IDLE
                self.attacker.IDLE.enter(('OUT_OF_RANGE', None))
                return

            # 매우 가까운 거리이고 쿨타임 끝나면 공격
            if distance < self.attacker.attack_range and self.attacker.cooldown_timer <= 0:
                # Attack 상태로 전환
                self.attacker.state_machine.cur_state = self.attacker.ATTACK
                self.attacker.ATTACK.enter(('ATTACK', None))
            elif distance > 0:
                # 플레이어 방향으로 이동
                self.attacker.dir_x = dx / distance
                self.attacker.dir_y = dy / distance

                # 이동 전 위치 저장
                prev_x, prev_y = self.attacker.x, self.attacker.y

                speed = self.attacker.chase_speed * game_framework.frame_time
                self.attacker.x += self.attacker.dir_x * speed
                self.attacker.y += self.attacker.dir_y * speed

                # 벽 충돌 체크
                import play_mode
                if hasattr(play_mode, 'background') and play_mode.background:
                    if play_mode.background.is_wall_at(self.attacker.x, self.attacker.y):
                        self.attacker.x = prev_x
                        self.attacker.y = prev_y

                # 화면 경계 체크
                self.attacker.x = max(0, min(2048, self.attacker.x))
                self.attacker.y = max(0, min(2048, self.attacker.y))

                # face_dir 업데이트 (4방향만: 1, -1, 0, 4)
                if abs(dx) > abs(dy):
                    self.attacker.face_dir = 1 if dx > 0 else -1
                else:
                    self.attacker.face_dir = 4 if dy > 0 else 0

    def draw(self):
        # 깜빡임 처리
        if self.attacker.hit_timer > 0 and int(self.attacker.hit_timer * 10) % 2 == 1:
            return

        # face_dir에 따른 스프라이트 선택 및 flip 처리
        dir_key = abs(self.attacker.face_dir) if abs(self.attacker.face_dir) == 1 else self.attacker.face_dir

        if dir_key in self.SPRITE_COORDS:
            coords = self.SPRITE_COORDS[dir_key]
            frame = int(self.attacker.frame) % coords['frames']
            flip = 'h' if self.attacker.face_dir == -1 else ''

            if hasattr(self.attacker, 'draw_x'):
                size = int(55 * play_mode.background.zoom) if hasattr(play_mode, 'background') and play_mode.background else 55
            else:
                size = 55

            self.attacker.image.clip_composite_draw(
                frame * 55, coords['y'], 55, 55,
                0, flip,
                self.attacker.draw_x if hasattr(self.attacker, 'draw_x') else self.attacker.x,
                self.attacker.draw_y if hasattr(self.attacker, 'draw_y') else self.attacker.y, size, size
            )


class Attack:
    # 55x55 그리드 기반 스프라이트 좌표
    SPRITE_COORDS = {
        1: {'y': 165, 'frames': 5},  # 오른쪽/왼쪽
        4: {'y': 110, 'frames': 5},  # 위
        0: {'y': 55, 'frames': 5}  # 아래
    }

    def __init__(self, attacker):
        self.attacker = attacker
        self.attack_duration = 0.5  # 공격 애니메이션 시간
        self.attack_timer = 0
        self.hitbox_delay = 0.2  # 히트박스 생성 딜레이
        self.hitbox_created = False

    def enter(self, e):
        self.attack_timer = 0
        self.attacker.frame = 0  # 공격 애니메이션 처음부터
        self.hitbox_created = False

    def exit(self, e):
        pass

    def do(self):
        # 공격 애니메이션 프레임 업데이트 (5프레임)
        self.attacker.frame = (self.attacker.frame + 10 * game_framework.frame_time) % 5
        self.attack_timer += game_framework.frame_time

        # 딜레이 후 히트박스 생성
        if not self.hitbox_created and self.attack_timer >= self.hitbox_delay:
            from attack_hitbox import AttackHitbox

            # 기본 바운딩박스 크기: 44x44 (half_size = 22)
            # 좌우 공격: 가로 11 (44/4), 세로 44
            # 상하 공격: 가로 44, 세로 11 (44/4)
            # 오프셋: 바운딩박스 경계 + 히트박스 반지름 = 22 + 5.5 ≈ 28

            offset_x, offset_y = 0, 0
            width, height = 0, 0

            if self.attacker.face_dir == 1:  # 오른쪽
                offset_x = 28
                width, height = 11, 44
            elif self.attacker.face_dir == -1:  # 왼쪽
                offset_x = -28
                width, height = 11, 44
            elif self.attacker.face_dir == 4:  # 위
                offset_y = 28
                width, height = 44, 11
            elif self.attacker.face_dir == 0:  # 아래
                offset_y = -28
                width, height = 44, 11

            hitbox = AttackHitbox(self.attacker,
                                 self.attacker.x + offset_x,
                                 self.attacker.y + offset_y,
                                 width, height, 0.3)
            game_world.add_object(hitbox, 3)
            game_world.add_collision_pair('monster_attack:player', hitbox, None)
            self.hitbox_created = True
            print(f"Attacker hitbox created at {self.attack_timer:.2f}s")

        # 제자리에서 공격 - 이동 코드 없음!
        # self.attacker.x, self.attacker.y 변경하지 않음

        # 충돌 검사
        if self.attacker.target_player and game_world.collide(self.attacker, self.attacker.target_player):
            # 플레이어와 접촉 중
            pass

        # 공격 시간 종료
        if self.attack_timer >= self.attack_duration:
            self.attacker.cooldown_timer = self.attacker.attack_cooldown

            # 여전히 범위 안이면 Idle, 아니면 Move
            if self.attacker.target_player:
                dx = self.attacker.target_player.x - self.attacker.x
                dy = self.attacker.target_player.y - self.attacker.y
                distance = math.sqrt(dx ** 2 + dy ** 2)

                if distance < self.attacker.attack_range * 1.5:
                    self.attacker.state_machine.cur_state = self.attacker.IDLE
                    self.attacker.IDLE.enter(('ATTACK_END', None))
                else:
                    self.attacker.state_machine.cur_state = self.attacker.MOVE
                    self.attacker.MOVE.enter(('ATTACK_END', None))

    def draw(self):
        # 깜빡임 처리
        if self.attacker.hit_timer > 0 and int(self.attacker.hit_timer * 10) % 2 == 1:
            return

        # face_dir에 따른 스프라이트 선택 및 flip 처리
        dir_key = abs(self.attacker.face_dir) if abs(self.attacker.face_dir) == 1 else self.attacker.face_dir

        if dir_key in self.SPRITE_COORDS:
            coords = self.SPRITE_COORDS[dir_key]
            frame = int(self.attacker.frame) % coords['frames']
            flip = 'h' if self.attacker.face_dir == -1 else ''

            if hasattr(self.attacker, 'draw_x'):
                size = int(55 * play_mode.background.zoom) if hasattr(play_mode, 'background') and play_mode.background else 55
            else:
                size = 55

            self.attacker.image.clip_composite_draw(
                frame * 55, coords['y'], 55, 55,
                0, flip,
                self.attacker.draw_x if hasattr(self.attacker, 'draw_x') else self.attacker.x,
                self.attacker.draw_y if hasattr(self.attacker, 'draw_y') else self.attacker.y, size, size
            )


class EnemyAttacker:
    def __init__(self, player=None):
        # 월드 좌표로 초기화
        self.x, self.y = 600, 1500  # 다른 몬스터와 겹치지 않는 위치
        self.frame = 0
        self.face_dir = 1
        self.dir_x = 0
        self.dir_y = 0
        self.image = load_image('EnemyAttaker.png')  # 철자 주의: Attaker (t 하나)
        self.target_player = player
        self.attack_range = 60  # 매우 가까운 거리에서만 공격
        self.chase_speed = 70  # 중간 속도
        self.attack_cooldown = 3.0  # 쿨타임 3.0초
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
        # 스크롤링: 플레이어 기준으로 화면 좌표 계산
        if hasattr(play_mode, 'background') and play_mode.background:
            self.draw_x = (self.x - play_mode.background.window_left) * play_mode.background.zoom
            self.draw_y = (self.y - play_mode.background.window_bottom) * play_mode.background.zoom
            bb_half_size = int(20 * play_mode.background.zoom)
        else:
            window_left = clamp(0, int(common.player.x) - get_canvas_width() // 2, 2048 - get_canvas_width())
            window_bottom = clamp(0, int(common.player.y) - get_canvas_height() // 2, 2048 - get_canvas_height())
            self.draw_x = self.x - window_left
            self.draw_y = self.y - window_bottom
            bb_half_size = 20

        self.state_machine.draw()

        # 바운딩 박스도 화면 좌표로
        draw_rectangle(
            self.draw_x - bb_half_size, self.draw_y - bb_half_size,
            self.draw_x + bb_half_size, self.draw_y + bb_half_size
        )

    def get_bb(self):
        return self.x - 22, self.y - 22, self.x + 22, self.y + 22

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
            print(f"Attacker hit! HP: {self.hp}")

            if self.hp <= 0:
                self.is_dead = True
                import game_world
                game_world.remove_object(self)
                print("Attacker defeated!")

        elif group == 'arrow:monster':
            # 화살은 별도 처리 (화살 자체가 한 번만 맞음)
            self.hp -= 1
            print(f"Attacker hit by arrow! HP: {self.hp}")

            if self.hp <= 0:
                self.is_dead = True
                import game_world
                game_world.remove_object(self)
                print("Attacker defeated!")