import common
from pico2d import load_image, draw_rectangle, get_canvas_width, get_canvas_height, clamp
import game_framework
from state_machine import StateMachine
import game_world
import math
from bomb import Bomb


class Idle:
    # 55x55 그리드 기반 스프라이트 좌표
    SPRITE_COORDS = {
        1: {'y': 385, 'frames': 3},  # 오른쪽/왼쪽
        4: {'y': 330, 'frames': 3},  # 위
        0: {'y': 275, 'frames': 3}  # 아래
    }

    def __init__(self, bommer):
        self.bommer = bommer

    def enter(self, e):
        self.bommer.frame = 0

    def exit(self, e):
        pass

    def do(self):
        # 프레임 업데이트 (3프레임)
        self.bommer.frame = (self.bommer.frame + 6 * game_framework.frame_time) % 3

        # 쿨타임 감소
        if self.bommer.cooldown_timer > 0:
            self.bommer.cooldown_timer -= game_framework.frame_time

        # 충돌 해제되고 쿨타임 끝나면 Move로
        if self.bommer.target_player:
            if not game_world.collide(self.bommer, self.bommer.target_player) and self.bommer.cooldown_timer <= 0:
                self.bommer.state_machine.cur_state = self.bommer.MOVE
                self.bommer.MOVE.enter(('START_CHASE', None))

    def draw(self):
        # 깜빡임 처리
        if self.bommer.hit_timer > 0 and int(self.bommer.hit_timer * 10) % 2 == 1:
            return

        # face_dir에 따른 스프라이트 선택 및 flip 처리
        dir_key = abs(self.bommer.face_dir) if abs(self.bommer.face_dir) == 1 else self.bommer.face_dir

        if dir_key in self.SPRITE_COORDS:
            coords = self.SPRITE_COORDS[dir_key]
            frame = int(self.bommer.frame) % coords['frames']
            flip = 'h' if self.bommer.face_dir == -1 else ''

            import play_mode
            if hasattr(self.bommer, 'draw_x'):
                size = int(55 * play_mode.background.zoom) if hasattr(play_mode, 'background') and play_mode.background else 55
            else:
                size = 55

            self.bommer.image.clip_composite_draw(
                frame * 55, coords['y'], 55, 55,
                0, flip,
                self.bommer.draw_x if hasattr(self.bommer, 'draw_x') else self.bommer.x,
                self.bommer.draw_y if hasattr(self.bommer, 'draw_y') else self.bommer.y, size, size
            )


class Move:
    # 55x55 그리드 기반 스프라이트 좌표
    SPRITE_COORDS = {
        1: {'y': 220, 'frames': 3},  # 오른쪽/왼쪽
        4: {'y': 165, 'frames': 3},  # 위
        0: {'y': 110, 'frames': 3}  # 아래
    }

    def __init__(self, bommer):
        self.bommer = bommer

    def enter(self, e):
        self.bommer.frame = 0

    def exit(self, e):
        pass

    def do(self):
        # 프레임 업데이트 (3프레임)
        self.bommer.frame = (self.bommer.frame + 6 * game_framework.frame_time) % 3

        # 쿨타임 감소
        if self.bommer.cooldown_timer > 0:
            self.bommer.cooldown_timer -= game_framework.frame_time

        if self.bommer.target_player:
            # 플레이어와의 거리 계산
            dx = self.bommer.target_player.x - self.bommer.x
            dy = self.bommer.target_player.y - self.bommer.y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            # 추적 거리 밖이면 Idle로 전환
            if distance > self.bommer.chase_range:
                self.bommer.state_machine.cur_state = self.bommer.IDLE
                self.bommer.IDLE.enter(('OUT_OF_RANGE', None))
                return

            # 적절한 거리(100~200)를 유지하려고 함
            if distance < self.bommer.attack_range and distance > self.bommer.min_attack_range and self.bommer.cooldown_timer <= 0:
                # 공격 범위 안이고 쿨타임 끝나면 공격
                self.bommer.state_machine.cur_state = self.bommer.ATTACK
                self.bommer.ATTACK.enter(('ATTACK', None))
            elif distance < self.bommer.min_attack_range:
                # 너무 가까우면 후퇴
                self.bommer.dir_x = -dx / distance
                self.bommer.dir_y = -dy / distance

                # 이동 전 위치 저장
                prev_x, prev_y = self.bommer.x, self.bommer.y

                speed = self.bommer.chase_speed * game_framework.frame_time
                self.bommer.x += self.bommer.dir_x * speed
                self.bommer.y += self.bommer.dir_y * speed

                # 벽 충돌 체크
                import play_mode
                if hasattr(play_mode, 'background') and play_mode.background:
                    if play_mode.background.is_wall_at(self.bommer.x, self.bommer.y):
                        self.bommer.x = prev_x
                        self.bommer.y = prev_y

                # 화면 경계 체크
                self.bommer.x = max(0, min(2048, self.bommer.x))
                self.bommer.y = max(0, min(2048, self.bommer.y))
            elif distance > self.bommer.attack_range:
                # 너무 멀면 접근
                self.bommer.dir_x = dx / distance
                self.bommer.dir_y = dy / distance

                # 이동 전 위치 저장
                prev_x, prev_y = self.bommer.x, self.bommer.y

                speed = self.bommer.chase_speed * game_framework.frame_time
                self.bommer.x += self.bommer.dir_x * speed
                self.bommer.y += self.bommer.dir_y * speed

                # 벽 충돌 체크
                import play_mode
                if hasattr(play_mode, 'background') and play_mode.background:
                    if play_mode.background.is_wall_at(self.bommer.x, self.bommer.y):
                        self.bommer.x = prev_x
                        self.bommer.y = prev_y

                # 화면 경계 체크
                self.bommer.x = max(0, min(2048, self.bommer.x))
                self.bommer.y = max(0, min(2048, self.bommer.y))

            # face_dir 업데이트 (8방향 지원, 대각선은 좌우만 고려)
            if abs(dx) > abs(dy) * 2:
                self.bommer.face_dir = 1 if dx > 0 else -1
            elif abs(dy) > abs(dx) * 2:
                self.bommer.face_dir = 4 if dy > 0 else 0
            else:
                # 대각선은 좌우만 고려
                self.bommer.face_dir = 1 if dx > 0 else -1

    def draw(self):
        # 깜빡임 처리
        if self.bommer.hit_timer > 0 and int(self.bommer.hit_timer * 10) % 2 == 1:
            return

        # face_dir에 따른 스프라이트 선택 및 flip 처리
        dir_key = abs(self.bommer.face_dir) if abs(self.bommer.face_dir) == 1 else self.bommer.face_dir

        if dir_key in self.SPRITE_COORDS:
            coords = self.SPRITE_COORDS[dir_key]
            frame = int(self.bommer.frame) % coords['frames']
            flip = 'h' if self.bommer.face_dir == -1 else ''

            import play_mode
            if hasattr(self.bommer, 'draw_x'):
                size = int(55 * play_mode.background.zoom) if hasattr(play_mode, 'background') and play_mode.background else 55
            else:
                size = 55

            self.bommer.image.clip_composite_draw(
                frame * 55, coords['y'], 55, 55,
                0, flip,
                self.bommer.draw_x if hasattr(self.bommer, 'draw_x') else self.bommer.x,
                self.bommer.draw_y if hasattr(self.bommer, 'draw_y') else self.bommer.y, size, size
            )


class Attack:
    # 모든 방향 행 7 사용
    SPRITE_COORDS = {
        'y': 55,
        'frames': 5
    }

    def __init__(self, bommer):
        self.bommer = bommer
        self.attack_duration = 0.6  # 공격 애니메이션 시간
        self.attack_timer = 0
        self.bomb_thrown = False  # 폭탄을 이미 던졌는지 체크

    def enter(self, e):
        self.attack_timer = 0
        self.bommer.frame = 0
        self.bomb_thrown = False

    def exit(self, e):
        pass

    def do(self):
        # 공격 애니메이션 프레임 업데이트 (5프레임)
        self.bommer.frame = (self.bommer.frame + 8.33 * game_framework.frame_time) % 5
        self.attack_timer += game_framework.frame_time

        # 애니메이션 중간(0.3초)에 폭탄 생성
        if self.attack_timer >= 0.3 and not self.bomb_thrown:
            self.bomb_thrown = True

            # 공격 시점의 플레이어 위치로 폭탄 생성
            if self.bommer.target_player:
                from bomb import Bomb
                bomb = Bomb(
                    self.bommer.x,
                    self.bommer.y,
                    self.bommer.target_player.x,
                    self.bommer.target_player.y
                )
                game_world.add_object(bomb, 1)

        # 공격 종료
        if self.attack_timer >= self.attack_duration:
            self.bommer.cooldown_timer = self.bommer.attack_cooldown
            self.bommer.state_machine.cur_state = self.bommer.MOVE
            self.bommer.MOVE.enter(('ATTACK_END', None))

    def draw(self):
        # 깜빡임 처리
        if self.bommer.hit_timer > 0 and int(self.bommer.hit_timer * 10) % 2 == 1:
            return

        frame = int(self.bommer.frame) % 5
        # 왼쪽 방향 계열이면 flip
        flip = 'h' if self.bommer.face_dir == -1 or self.bommer.face_dir == -2 or self.bommer.face_dir == -3 else ''

        import play_mode
        if hasattr(self.bommer, 'draw_x'):
            size = int(55 * play_mode.background.zoom) if hasattr(play_mode, 'background') and play_mode.background else 55
        else:
            size = 55

        self.bommer.image.clip_composite_draw(
            frame * 55, self.SPRITE_COORDS['y'], 55, 55,
            0, flip,
            self.bommer.draw_x if hasattr(self.bommer, 'draw_x') else self.bommer.x,
            self.bommer.draw_y if hasattr(self.bommer, 'draw_y') else self.bommer.y, size, size
        )


class EnemyBommer:
    def __init__(self, player=None):
        # 월드 좌표로 초기화
        self.x, self.y = 400, 1900  # 다른 몬스터와 겹치지 않는 위치
        self.frame = 0
        self.face_dir = 1
        self.dir_x = 0
        self.dir_y = 0
        self.image = load_image('EnemyBommer.png')
        self.target_player = player
        self.attack_range = 200  # 원거리 공격 (200픽셀)
        self.min_attack_range = 100  # 너무 가까우면 후퇴
        self.chase_speed = 55  # 느린 속도
        self.attack_cooldown = 5.0  # 긴 쿨타임 (5초)
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
        import play_mode
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
            print(f"Bommer hit! HP: {self.hp}")

            if self.hp <= 0:
                self.is_dead = True
                import game_world
                game_world.remove_object(self)
                print("Bommer defeated!")

        elif group == 'arrow:monster':
            # 화살은 별도 처리 (화살 자체가 한 번만 맞음)
            self.hp -= 1
            print(f"Bommer hit by arrow! HP: {self.hp}")

            if self.hp <= 0:
                self.is_dead = True
                import game_world
                game_world.remove_object(self)
                print("Bommer defeated!")