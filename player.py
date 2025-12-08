from pico2d import load_image, draw_rectangle, get_canvas_width, get_canvas_height, clamp
from sdl2 import SDL_KEYDOWN, SDLK_RIGHT, SDLK_LEFT, SDLK_UP, SDLK_DOWN, SDL_KEYUP
from sdl2 import SDLK_z, SDLK_x, SDLK_i, SDLK_1, SDLK_2, SDLK_m

import game_world
import game_framework
import common
from state_machine import StateMachine
from skill import BowSkill
import math


def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT


def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT


def up_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_UP


def up_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_UP


def down_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_DOWN


def down_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_DOWN


def z_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_z


def x_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_x


def i_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_i


def key_1_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_1


def key_2_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_2


def m_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_m


def event_stop(e):
    return e[0] == 'STOP'


def event_run(e):
    return e[0] == 'RUN'


# Player Speed
PIXEL_PER_METER = (10.0 / 0.3)
RUN_SPEED_KMPH = 20.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

# Player Action Speed
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 10


class Idle:

    def __init__(self, player):
        self.player = player

    def enter(self, e):
        self.player.dir_x = 0
        self.player.dir_y = 0

    def exit(self, e):
        pass

    def do(self):
        self.player.frame = (self.player.frame + 2 * ACTION_PER_TIME * game_framework.frame_time) % 2

    def draw(self):
        # 깜빡임 처리: 피격 중일 때 0.1초마다 on/off
        if self.player.hit_timer > 0 and int(self.player.hit_timer * 10) % 2 == 1:
            return

        if self.player.background:
            screen_x = (self.player.x - self.player.background.window_left) * self.player.background.zoom
            screen_y = (self.player.y - self.player.background.window_bottom) * self.player.background.zoom
            draw_w = int(28 * self.player.background.zoom)
            draw_h = int(32 * self.player.background.zoom)
        else:
            screen_x = self.player.x
            screen_y = self.player.y
            draw_w = 28
            draw_h = 32

        sprite_w = 28
        sprite_h = 32

        if self.player.face_dir == 1:
            self.player.image.clip_composite_draw(int(self.player.frame) * 28 + 450, 512 - 272, 28, 32, 0, '',
                                                  screen_x, screen_y, draw_w, draw_h)
        elif self.player.face_dir == 2:
            self.player.image.clip_composite_draw(int(self.player.frame) * 28 + 450, 512 - 400, 28, 32, 0, '',
                                                  screen_x, screen_y, draw_w, draw_h)
        elif self.player.face_dir == 3:
            self.player.image.clip_composite_draw(int(self.player.frame) * 28 + 450, 512 - 336, 28, 32, 0, '',
                                                  screen_x, screen_y, draw_w, draw_h)
        elif self.player.face_dir == -1:
            self.player.image.clip_composite_draw(int(self.player.frame) * 28 + 450, 512 - 272, 28, 32, 0, 'h',
                                                  screen_x, screen_y, draw_w, draw_h)
        elif self.player.face_dir == -2:
            self.player.image.clip_composite_draw(int(self.player.frame) * 28 + 450, 512 - 400, 28, 32, 0, 'h',
                                                  screen_x, screen_y, draw_w, draw_h)
        elif self.player.face_dir == -3:
            self.player.image.clip_composite_draw(int(self.player.frame) * 28 + 450, 512 - 336, 28, 32, 0, 'h',
                                                  screen_x, screen_y, draw_w, draw_h)
        elif self.player.face_dir == 0:
            self.player.image.clip_composite_draw(int(self.player.frame) * 28 + 450, 512 - 303, 28, 32, 0, '',
                                                  screen_x, screen_y, draw_w, draw_h)
        elif self.player.face_dir == 4:
            self.player.image.clip_composite_draw(int(self.player.frame) * 28 + 450, 512 - 368, 28, 32, 0, '',
                                                  screen_x, screen_y, draw_w, draw_h)


class Run:
    SPRITE_COORDS = {
        1: {
            'y': 464,
            'height': 48,
            'x': [0, 48, 96, 144, 192, 240, 288, 336, 384, 432],
            'width': [48, 48, 48, 48, 48, 48, 48, 48, 48, 48]
        },
        0: {
            'y': 416,
            'height': 48,
            'x': [0, 48, 96, 144, 192, 240, 288, 336, 384, 432],
            'width': [48, 48, 48, 48, 48, 48, 48, 48, 48, 48]
        },
        3: {
            'y': 368,
            'height': 48,
            'x': [0, 48, 96, 144, 192, 240, 288, 336, 384, 432],
            'width': [48, 48, 48, 48, 48, 48, 48, 48, 48, 48]
        },
        4: {
            'y': 320,
            'height': 48,
            'x': [0, 48, 96, 144, 192, 240, 288, 336, 384, 432],
            'width': [48, 48, 48, 48, 48, 48, 48, 48, 48, 48]
        },
        2: {
            'y': 272,
            'height': 48,
            'x': [0, 48, 96, 144, 192, 240, 288, 336, 384, 432],
            'width': [48, 48, 48, 48, 48, 48, 48, 48, 48, 48]
        }
    }

    def __init__(self, player):
        self.player = player

    def enter(self, e):
        if right_down(e):
            self.player.dir_x += 1
        elif left_down(e):
            self.player.dir_x -= 1
        elif right_up(e):
            self.player.dir_x -= 1
        elif left_up(e):
            self.player.dir_x += 1

        if up_down(e):
            self.player.dir_y += 1
        elif down_down(e):
            self.player.dir_y -= 1
        elif up_up(e):
            self.player.dir_y -= 1
        elif down_up(e):
            self.player.dir_y += 1

        self.update_face_dir()

    def exit(self, e):
        pass

    def update_face_dir(self):
        if self.player.dir_x > 0:
            if self.player.dir_y > 0:
                self.player.face_dir = 2
            elif self.player.dir_y < 0:
                self.player.face_dir = 3
            else:
                self.player.face_dir = 1
        elif self.player.dir_x < 0:
            if self.player.dir_y > 0:
                self.player.face_dir = -2
            elif self.player.dir_y < 0:
                self.player.face_dir = -3
            else:
                self.player.face_dir = -1
        else:
            if self.player.dir_y > 0:
                self.player.face_dir = 4
            elif self.player.dir_y < 0:
                self.player.face_dir = 0

    def do(self):
        self.player.frame = (self.player.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 10

        if not self.player.is_attacking:
            speed = RUN_SPEED_PPS * game_framework.frame_time
            if self.player.dir_x != 0 and self.player.dir_y != 0:
                speed = speed * 0.7071

            self.player.x += self.player.dir_x * speed
            self.player.y += self.player.dir_y * speed

        self.update_face_dir()

    def draw(self):
        # 깜빡임 처리: 피격 중일 때 0.1초마다 on/off
        if self.player.hit_timer > 0 and int(self.player.hit_timer * 10) % 2 == 1:
            return

        if self.player.background:
            screen_x = (self.player.x - self.player.background.window_left) * self.player.background.zoom
            screen_y = (self.player.y - self.player.background.window_bottom) * self.player.background.zoom
        else:
            screen_x = self.player.x
            screen_y = self.player.y

        direction = abs(self.player.face_dir)
        flip = 'h' if self.player.face_dir < 0 else ''

        if direction in self.SPRITE_COORDS:
            coords = self.SPRITE_COORDS[direction]
            frame = int(self.player.frame)

            if frame < len(coords['x']):
                x = coords['x'][frame]
                y = coords['y']
                width = coords['width'][frame]
                height = coords['height']

                if self.player.background:
                    draw_w = int(width * self.player.background.zoom)
                    draw_h = int(height * self.player.background.zoom)
                else:
                    draw_w = width
                    draw_h = height

                self.player.image.clip_composite_draw(
                    x, y,
                    width, height,
                    0, flip,
                    screen_x, screen_y,
                    draw_w, draw_h
                )


class Player:
    def __init__(self, background=None):
        # 월드 좌표 (왼쪽 상단 방에서 시작)
        self.x, self.y = 288, 1824

        # 이전 프레임 위치 (충돌 처리용)
        self.prev_x, self.prev_y = self.x, self.y

        # 화면 표시 좌표 (항상 화면 중앙)
        self.screen_x = get_canvas_width() // 2
        self.screen_y = get_canvas_height() // 2

        self.frame = 0
        self.face_dir = 1
        self.dir_x = 0
        self.dir_y = 0
        self.image = load_image('player.png')
        self.bow_image = load_image('item_bow_C.png')
        self.inventory_image = load_image('inventory.png')
        self.worldmap_image = load_image('worldmap.png')
        self.health_bar_image = load_image('LifeBarU.png')

        self.show_bow = False
        self.bow_timer = 0
        self.show_inventory = False
        self.show_worldmap = False

        self.current_weapon = 'bow'
        self.skill = BowSkill(self)
        self.is_attacking = False

        # 체력 시스템
        self.max_hp = 100
        self.hp = 100

        # 피격 깜빡임 시스템
        self.hit_timer = 0
        self.hit_duration = 0.5

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {
                    right_down: self.RUN, left_down: self.RUN,
                    up_down: self.RUN, down_down: self.RUN
                },
                self.RUN: {
                    right_up: self.IDLE, left_up: self.IDLE,
                    up_up: self.IDLE, down_up: self.IDLE
                }
            }
        )

        # background 참조 (스크롤링용)
        self.background = background

    def update(self):
        # 이동 전 위치 저장 (충돌 시 되돌리기 위함)
        self.prev_x, self.prev_y = self.x, self.y

        self.state_machine.update()

        # 벽 충돌 체크
        if self.background and self.background.is_wall_at(self.x, self.y):
            self.x = self.prev_x
            self.y = self.prev_y

        # 맵 범위 제한
        self.x = max(0, min(self.x, 2048))
        self.y = max(0, min(self.y, 2048))

        if self.show_bow:
            self.bow_timer -= game_framework.frame_time
            if self.bow_timer <= 0:
                self.show_bow = False

        # 피격 깜빡임 타이머 감소
        if self.hit_timer > 0:
            self.hit_timer -= game_framework.frame_time

        if self.skill and self.skill.is_active():
            self.skill.update()

    def handle_event(self, event):
        if self.state_machine.cur_state == self.RUN:
            if right_down(('INPUT', event)):
                self.dir_x = min(self.dir_x + 1, 1)
            elif right_up(('INPUT', event)):
                self.dir_x = max(self.dir_x - 1, -1)
            elif left_down(('INPUT', event)):
                self.dir_x = max(self.dir_x - 1, -1)
            elif left_up(('INPUT', event)):
                self.dir_x = min(self.dir_x + 1, 1)

            if up_down(('INPUT', event)):
                self.dir_y = min(self.dir_y + 1, 1)
            elif up_up(('INPUT', event)):
                self.dir_y = max(self.dir_y - 1, -1)
            elif down_down(('INPUT', event)):
                self.dir_y = max(self.dir_y - 1, -1)
            elif down_up(('INPUT', event)):
                self.dir_y = min(self.dir_y + 1, 1)

        if z_down(('INPUT', event)):
            if self.current_weapon == 'bow':
                self.fire_arrow()
            elif self.current_weapon == 'sword':
                self.sword_attack()

        if x_down(('INPUT', event)):
            self.use_skill()

        if i_down(('INPUT', event)):
            self.toggle_inventory()

        if key_1_down(('INPUT', event)):
            self.current_weapon = 'sword'

        if key_2_down(('INPUT', event)):
            self.current_weapon = 'bow'

        if m_down(('INPUT', event)):
            self.show_worldmap = not self.show_worldmap

        self.state_machine.handle_state_event(('INPUT', event))

    def draw(self, camera=None):
        # 스크롤링: 화면 좌표 계산
        if self.background:
            screen_x = (self.x - self.background.window_left) * self.background.zoom
            screen_y = (self.y - self.background.window_bottom) * self.background.zoom
        else:
            screen_x = self.x
            screen_y = self.y

        self.state_machine.draw()

        if self.show_bow:
            bow_angle = 0
            bow_x_offset = 0
            bow_y_offset = 0

            if self.face_dir == 1:
                bow_angle = math.pi
                bow_x_offset, bow_y_offset = 20, 0
            elif self.face_dir == -1:
                bow_angle = 0
                bow_x_offset, bow_y_offset = -20, 0
            elif self.face_dir == 2:
                bow_angle = math.pi * 5 / 4
                bow_x_offset, bow_y_offset = 15, 15
            elif self.face_dir == -2:
                bow_angle = math.pi * 7 / 4
                bow_x_offset, bow_y_offset = -15, 15
            elif self.face_dir == 3:
                bow_angle = math.pi * 3 / 4
                bow_x_offset, bow_y_offset = 15, -15
            elif self.face_dir == -3:
                bow_angle = math.pi / 4
                bow_x_offset, bow_y_offset = -15, -15
            elif self.face_dir == 4:
                bow_angle = math.pi * 3 / 2
                bow_x_offset, bow_y_offset = 0, 20
            elif self.face_dir == 0:
                bow_angle = math.pi / 2
                bow_x_offset, bow_y_offset = 0, -20

            if self.background:
                bow_offset_x = bow_x_offset * self.background.zoom
                bow_offset_y = bow_y_offset * self.background.zoom
                bow_size = int(30 * self.background.zoom)
            else:
                bow_offset_x = bow_x_offset
                bow_offset_y = bow_y_offset
                bow_size = 30

            self.bow_image.composite_draw(bow_angle, '',
                                          screen_x + bow_offset_x,
                                          screen_y + bow_offset_y,
                                          bow_size, bow_size)

        if self.show_inventory:
            self.inventory_image.draw(512, 512, 512, 512)

        if self.show_worldmap:
            self.worldmap_image.draw(512, 512, 1024, 576)

        # 체력바 그리기 (플레이어 머리 위)
        self.draw_health_bar(screen_x, screen_y)

        # 바운딩 박스 (화면 좌표 기준)
        if self.background:
            bb_half_size = int(12 * self.background.zoom)
        else:
            bb_half_size = 12
        draw_rectangle(
            screen_x - bb_half_size, screen_y - bb_half_size,
            screen_x + bb_half_size, screen_y + bb_half_size
        )

    def get_bb(self):
        return self.x - 12, self.y - 12, self.x + 12, self.y + 12

    def fire_arrow(self):
        from arrow import Arrow

        self.show_bow = True
        self.bow_timer = 0.1

        offset_map = {
            1: (20, 0), 2: (15, 15), 3: (15, -15), 4: (0, 20),
            0: (0, -20), -1: (-20, 0), -2: (-15, 15), -3: (-15, -15)
        }

        offset_x, offset_y = offset_map.get(self.face_dir, (20, 0))
        arrow = Arrow(self.x + offset_x, self.y + offset_y, self.face_dir)
        game_world.add_object(arrow, 1)

        # 화살-몬스터 충돌 쌍 등록
        game_world.add_collision_pair('arrow:monster', arrow, None)

    def use_skill(self):
        if self.skill and not self.skill.is_active():
            self.skill.activate()

    def toggle_inventory(self):
        self.show_inventory = not self.show_inventory

    def sword_attack(self):
        from sword import Sword
        from attack_hitbox import AttackHitbox

        self.is_attacking = True

        sword = Sword(self.x, self.y, self.face_dir, self)
        game_world.add_object(sword, 1)

        # 방향별 오프셋
        offset_x, offset_y = 0, 0
        if self.face_dir == 1:
            offset_x = 40
        elif self.face_dir == -1:
            offset_x = -40
        elif self.face_dir == 4:
            offset_y = 40
        elif self.face_dir == 0:
            offset_y = -40
        elif self.face_dir == 2:
            offset_x, offset_y = 30, 30
        elif self.face_dir == -2:
            offset_x, offset_y = -30, 30
        elif self.face_dir == 3:
            offset_x, offset_y = 30, -30
        elif self.face_dir == -3:
            offset_x, offset_y = -30, -30

        hitbox = AttackHitbox(self, self.x + offset_x, self.y + offset_y,
                             60, 60, 0.2)
        game_world.add_object(hitbox, 3)
        game_world.add_collision_pair('player_attack:monster', hitbox, None)

    def draw_health_bar(self, screen_x, screen_y):
        """체력바 그리기"""
        if self.background:
            bar_y_offset = int(30 * self.background.zoom)
            bar_width = int(28 * self.background.zoom)  # 플레이어 크기와 동일
            bar_height = int(4 * self.background.zoom)
        else:
            bar_y_offset = 30
            bar_width = 28
            bar_height = 4

        # 체력 비율 계산
        hp_ratio = max(0, self.hp / self.max_hp)

        # 체력바 그리기 (플레이어 머리 위)
        bar_x = screen_x
        bar_y = screen_y + bar_y_offset

        # 체력바 이미지를 비율에 맞게 잘라서 그리기
        if hp_ratio > 0:
            # LifeBarU.png의 왼쪽부터 hp_ratio만큼만 그리기
            source_width = int(28 * hp_ratio)
            draw_width = int(bar_width * hp_ratio)

            # clip_draw(sx, sy, width, height, x, y, w, h)
            self.health_bar_image.clip_draw(
                0, 0, source_width, 4,
                bar_x - bar_width // 2 + draw_width // 2, bar_y,
                draw_width, bar_height
            )

    def take_damage(self, damage):
        """데미지 받기"""
        self.hp -= damage
        self.hit_timer = self.hit_duration
        print(f"Player took {damage} damage! HP: {self.hp}/{self.max_hp}")

        # 체력이 0 이하가 되면 게임 종료
        if self.hp <= 0:
            self.hp = 0
            print("Player defeated! Game Over!")
            import game_framework
            game_framework.quit()

    def handle_collision(self, group, other):
        if group == 'monster_attack:player':
            pass  # 넉백은 히트박스에서 처리
        elif group == 'explosion:player':
            pass  # 폭발 데미지는 explosion에서 처리