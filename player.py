from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDLK_RIGHT, SDLK_LEFT, SDLK_UP, SDLK_DOWN, SDL_KEYUP

import game_world
from state_machine import StateMachine


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


def any_key_down(e):
    return right_down(e) or left_down(e) or up_down(e) or down_down(e)


def any_key_up(e):
    return right_up(e) or left_up(e) or up_up(e) or down_up(e)


class Idle:

    def __init__(self, player):
        self.player = player

    def enter(self, e):
        self.player.dir_x = 0
        self.player.dir_y = 0

    def exit(self, e):
        pass

    def do(self):
        self.player.frame = (self.player.frame + 1) % 2

    def draw(self):
        if self.player.face_dir == 1:  # 오른쪽
            self.player.image.clip_composite_draw(self.player.frame * 28 + 450, 512 - 272, 28, 32, 0, '', self.player.x,
                                                  self.player.y, 56, 64)
        elif self.player.face_dir == 2:  # 우상
            self.player.image.clip_composite_draw(self.player.frame * 28 + 450, 512 - 400, 28, 32, 0, '', self.player.x,
                                                  self.player.y, 56, 64)
        elif self.player.face_dir == 3:  # 우하
            self.player.image.clip_composite_draw(self.player.frame * 28 + 450, 512 - 336, 28, 32, 0, '', self.player.x,
                                                  self.player.y, 56, 64)
        elif self.player.face_dir == -1:  # 왼쪽
            self.player.image.clip_composite_draw(self.player.frame * 28 + 450, 512 - 272, 28, 32, 0, 'h',
                                                  self.player.x, self.player.y, 56, 64)
        elif self.player.face_dir == -2:  # 좌상
            self.player.image.clip_composite_draw(self.player.frame * 28 + 450, 512 - 400, 28, 32, 0, 'h',
                                                  self.player.x, self.player.y, 56, 64)
        elif self.player.face_dir == -3:  # 좌하
            self.player.image.clip_composite_draw(self.player.frame * 28 + 450, 512 - 338, 28, 32, 0, 'h',
                                                  self.player.x, self.player.y, 56, 64)
        elif self.player.face_dir == 0:  # 아래
            self.player.image.clip_composite_draw(self.player.frame * 28 + 450, 512 - 303, 28, 32, 0, '', self.player.x,
                                                  self.player.y, 56, 64)
        elif self.player.face_dir == 4:  # 위
            self.player.image.clip_composite_draw(self.player.frame * 28 + 450, 512 - 368, 28, 32, 0, '', self.player.x,
                                                  self.player.y, 56, 64)


class Run:
    # 빨간색 박스로 표시된 정확한 스프라이트 좌표
    # 각 줄마다 48픽셀 높이, 10개의 스프라이트(각 48픽셀 너비)
    SPRITE_COORDS = {
        1: {  # 오른쪽 (1줄)
            'y': 464,
            'height': 48,
            'x': [0, 48, 96, 144, 192, 240, 288, 336, 384, 432],
            'width': [48, 48, 48, 48, 48, 48, 48, 48, 48, 48]
        },
        0: {  # 아래 (2줄)
            'y': 416,
            'height': 48,
            'x': [0, 48, 96, 144, 192, 240, 288, 336, 384, 432],
            'width': [48, 48, 48, 48, 48, 48, 48, 48, 48, 48]
        },
        3: {  # 우하 (3줄)
            'y': 368,
            'height': 48,
            'x': [0, 48, 96, 144, 192, 240, 288, 336, 384, 432],
            'width': [48, 48, 48, 48, 48, 48, 48, 48, 48, 48]
        },
        4: {  # 위 (4줄)
            'y': 320,
            'height': 48,
            'x': [0, 48, 96, 144, 192, 240, 288, 336, 384, 432],
            'width': [48, 48, 48, 48, 48, 48, 48, 48, 48, 48]
        },
        2: {  # 우상 (5줄)
            'y': 272,
            'height': 48,
            'x': [0, 48, 96, 144, 192, 240, 288, 336, 384, 432],
            'width': [48, 48, 48, 48, 48, 48, 48, 48, 48, 48]
        }
    }

    def __init__(self, player):
        self.player = player

    def enter(self, e):
        # 키 입력에 따라 방향 업데이트
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

        # dir_x, dir_y에 따라 face_dir 설정 (8방향)
        self.update_face_dir()

    def exit(self, e):
        pass

    def update_face_dir(self):
        if self.player.dir_x > 0:  # 오른쪽
            if self.player.dir_y > 0:
                self.player.face_dir = 2  # 우상
            elif self.player.dir_y < 0:
                self.player.face_dir = 3  # 우하
            else:
                self.player.face_dir = 1  # 오른쪽
        elif self.player.dir_x < 0:  # 왼쪽
            if self.player.dir_y > 0:
                self.player.face_dir = -2  # 좌상
            elif self.player.dir_y < 0:
                self.player.face_dir = -3  # 좌하
            else:
                self.player.face_dir = -1  # 왼쪽
        else:  # dir_x == 0
            if self.player.dir_y > 0:
                self.player.face_dir = 4  # 위
            elif self.player.dir_y < 0:
                self.player.face_dir = 0  # 아래

    def do(self):
        self.player.frame = (self.player.frame + 1) % 10  # 각 줄마다 10개의 스프라이트

        # 대각선 이동시 속도 조정 (피타고라스)
        speed = 3
        if self.player.dir_x != 0 and self.player.dir_y != 0:
            # 대각선 이동시 sqrt(2)로 나눠서 속도 정규화
            speed = speed * 0.7071  # 1/sqrt(2) ≈ 0.7071

        self.player.x += self.player.dir_x * speed
        self.player.y += self.player.dir_y * speed

        # 방향 업데이트 (키가 변경되었을 수 있음)
        self.update_face_dir()

    def draw(self):
        # face_dir에 따라 적절한 방향 선택
        # 음수는 반전
        direction = abs(self.player.face_dir)
        flip = 'h' if self.player.face_dir < 0 else ''

        # 해당 방향의 좌표 정보 가져오기
        if direction in self.SPRITE_COORDS:
            coords = self.SPRITE_COORDS[direction]
            frame = self.player.frame

            # 프레임이 범위 내에 있는지 확인
            if frame < len(coords['x']):
                x = coords['x'][frame]
                y = coords['y']
                width = coords['width'][frame]
                height = coords['height']

                self.player.image.clip_composite_draw(
                    x, y,  # 소스 이미지의 x, y
                    width, height,  # 소스 이미지의 width, height
                    0, flip,  # 회전, 반전
                    self.player.x, self.player.y,  # 화면 위치
                    width * 2, height * 2  # 화면 크기 (2배)
                )


class Player:
    def __init__(self):
        self.x, self.y = 400, 400
        self.frame = 0
        self.face_dir = 1  # 1:우, 2:우상, 3:우하, -1:좌, -2:좌상, -3:좌하, 0:하, 4:상
        self.dir_x = 0
        self.dir_y = 0
        self.image = load_image('player.png')

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {
                    any_key_down: self.RUN
                },
                self.RUN: {
                    any_key_up: self.IDLE
                }
            }
        )

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()

    def handle_event(self, event):
        # 이벤트 처리 - RUN 상태에서도 키 입력을 받아서 방향을 업데이트
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

        self.state_machine.handle_state_event(('INPUT', event))