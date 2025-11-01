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
            self.player.image.clip_composite_draw(self.player.frame * 28 + 450, 512 - 336, 28, 32, 0, 'h',
                                                  self.player.x, self.player.y, 56, 64)
        elif self.player.face_dir == 0:  # 아래
            self.player.image.clip_composite_draw(self.player.frame * 28 + 450, 512 - 303, 28, 32, 0, '', self.player.x,
                                                  self.player.y, 56, 64)
        elif self.player.face_dir == 4:  # 위
            self.player.image.clip_composite_draw(self.player.frame * 28 + 450, 512 - 368, 28, 32, 0, '', self.player.x,
                                                  self.player.y, 56, 64)


class Run:
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

    def exit(self, e):
        pass

    def do(self):
        self.player.frame = (self.player.frame + 1) % 10  # 각 줄마다 10개의 스프라이트
        self.player.x += self.player.dir_x * 3  # 이동 속도
        self.player.y += self.player.dir_y * 3

    def draw(self):
        # 각 방향별로 스프라이트 좌표 설정
        # player.png는 512x512 크기, 각 스프라이트는 28x32
        # 맨 위 5줄: 오른쪽(1줄), 아래(2줄), 우하(3줄), 위(4줄), 우상(5줄)

        if self.player.face_dir == 1:  # 오른쪽 - 1번째 줄
            self.player.image.clip_composite_draw(
                self.player.frame * 28 + 30, 512 - 48,  # x, y (맨 위 첫줄)
                28, 32,  # width, height
                0, '',  # 회전, 반전 없음
                self.player.x, self.player.y, 56, 64  # 화면 위치와 크기
            )
        elif self.player.face_dir == 0:  # 아래 - 2번째 줄
            self.player.image.clip_composite_draw(
                self.player.frame * 28 + 30, 512 - 80,
                28, 32,
                0, '',
                self.player.x, self.player.y, 56, 64
            )
        elif self.player.face_dir == 3:  # 우하 - 3번째 줄
            self.player.image.clip_composite_draw(
                self.player.frame * 28 + 30, 512 - 112,
                28, 32,
                0, '',
                self.player.x, self.player.y, 56, 64
            )
        elif self.player.face_dir == 4:  # 위 - 4번째 줄
            self.player.image.clip_composite_draw(
                self.player.frame * 28 + 30, 512 - 144,
                28, 32,
                0, '',
                self.player.x, self.player.y, 56, 64
            )
        elif self.player.face_dir == 2:  # 우상 - 5번째 줄
            self.player.image.clip_composite_draw(
                self.player.frame * 28 + 30, 512 - 176,
                28, 32,
                0, '',
                self.player.x, self.player.y, 56, 64
            )
        elif self.player.face_dir == -1:  # 왼쪽 - 1번째 줄 반전
            self.player.image.clip_composite_draw(
                self.player.frame * 28 + 30, 512 - 48,
                28, 32,
                0, 'h',  # 좌우 반전
                self.player.x, self.player.y, 56, 64
            )
        elif self.player.face_dir == -3:  # 좌하 - 3번째 줄 반전
            self.player.image.clip_composite_draw(
                self.player.frame * 28 + 30, 512 - 112,
                28, 32,
                0, 'h',  # 좌우 반전
                self.player.x, self.player.y, 56, 64
            )
        elif self.player.face_dir == -2:  # 좌상 - 5번째 줄 반전
            self.player.image.clip_composite_draw(
                self.player.frame * 28 + 30, 512 - 176,
                28, 32,
                0, 'h',  # 좌우 반전
                self.player.x, self.player.y, 56, 64
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
        self.state_machine.handle_state_event(('INPUT', event))