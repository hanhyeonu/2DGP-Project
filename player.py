from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDLK_RIGHT, SDLK_LEFT, SDLK_UP, SDLK_DOWN, SDL_KEYUP, SDLK_z, SDLK_x, SDLK_i, SDLK_1, SDLK_2, SDLK_m

import game_world
import game_framework
from state_machine import StateMachine
from arrow import Arrow
from skill import BowSkill
from sword import Sword
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


PIXEL_PER_METER = (10.0 / 0.3)
RUN_SPEED_KMPH = 20.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

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
        if self.player.face_dir == 1:
            self.player.image.clip_composite_draw(int(self.player.frame) * 28 + 450, 512 - 272, 28, 32, 0, '',
                                                  self.player.x, self.player.y, 28, 32)
        elif self.player.face_dir == 2:
            self.player.image.clip_composite_draw(int(self.player.frame) * 28 + 450, 512 - 400, 28, 32, 0, '',
                                                  self.player.x, self.player.y, 28, 32)
        elif self.player.face_dir == 3:
            self.player.image.clip_composite_draw(int(self.player.frame) * 28 + 450, 512 - 336, 28, 32, 0, '',
                                                  self.player.x, self.player.y, 28, 32)
        elif self.player.face_dir == -1:
            self.player.image.clip_composite_draw(int(self.player.frame) * 28 + 450, 512 - 272, 28, 32, 0, 'h',
                                                  self.player.x, self.player.y, 28, 32)
        elif self.player.face_dir == -2:
            self.player.image.clip_composite_draw(int(self.player.frame) * 28 + 450, 512 - 400, 28, 32, 0, 'h',
                                                  self.player.x, self.player.y, 28, 32)
        elif self.player.face_dir == -3:
            self.player.image.clip_composite_draw(int(self.player.frame) * 28 + 450, 512 - 336, 28, 32, 0, 'h',
                                                  self.player.x, self.player.y, 28, 32)
        elif self.player.face_dir == 0:
            self.player.image.clip_composite_draw(int(self.player.frame) * 28 + 450, 512 - 303, 28, 32, 0, '',
                                                  self.player.x, self.player.y, 28, 32)
        elif self.player.face_dir == 4:
            self.player.image.clip_composite_draw(int(self.player.frame) * 28 + 450, 512 - 368, 28, 32, 0, '',
                                                  self.player.x, self.player.y, 28, 32)


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

                self.player.image.clip_composite_draw(
                    x, y,
                    width, height,
                    0, flip,
                    self.player.x, self.player.y,
                    width, height
                )


class Player:
    def __init__(self):
        self.x, self.y = 400, 400
        self.frame = 0
        self.face_dir = 1
        self.dir_x = 0
        self.dir_y = 0
        self.image = load_image('player.png')
        self.bow_image = load_image('item_bow_C.png')
        self.inventory_image = load_image('inventory.png')
        self.show_bow = False
        self.bow_timer = 0
        self.show_inventory = False
        self.worldmap_image = load_image('worldmap.png')
        self.show_worldmap = False

        self.current_weapon = 'bow'
        self.skill = BowSkill(self)
        self.is_attacking = False

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

    def update(self):
        self.state_machine.update()

        if self.show_bow:
            self.bow_timer -= game_framework.frame_time
            if self.bow_timer <= 0:
                self.show_bow = False

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

    def draw(self):
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

            self.bow_image.composite_draw(bow_angle, '',
                                          self.x + bow_x_offset,
                                          self.y + bow_y_offset,
                                          30, 30)

        if self.show_inventory:
            self.inventory_image.draw(512, 512, 512, 512)

        if self.show_worldmap:
            self.worldmap_image.draw(512, 512, 1024, 576)

    def fire_arrow(self):
        self.show_bow = True
        self.bow_timer = 0.1

        offset_map = {
            1: (20, 0),
            2: (15, 15),
            3: (15, -15),
            4: (0, 20),
            0: (0, -20),
            -1: (-20, 0),
            -2: (-15, 15),
            -3: (-15, -15)
        }

        offset_x, offset_y = offset_map.get(self.face_dir, (20, 0))
        arrow = Arrow(self.x + offset_x, self.y + offset_y, self.face_dir)
        game_world.add_object(arrow, 1)

    def use_skill(self):
        if self.skill and not self.skill.is_active():
            self.skill.activate()

    def toggle_inventory(self):
        self.show_inventory = not self.show_inventory

    def sword_attack(self):
        self.is_attacking = True
        sword = Sword(self.x, self.y, self.face_dir, self)
        game_world.add_object(sword, 1)