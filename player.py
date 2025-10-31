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



class Idle:

    def __init__(self,player):
        self.player = player

    def enter(self, e):
        self.player.dir = 0

    def exit(self, e):
        pass

    def do(self):
        self.player.frame = (self.player.frame + 1) % 2

    def draw(self):
        if self.player.face_dir == 1: # 오른쪽
            self.player.image.clip_composite_draw(self.player.frame * 28 + 450, 512-272, 28, 32, 0,'', self.player.x, self.player.y, 56, 64)
        elif self.player.face_dir == 2: # 우상
            self.player.image.clip_composite_draw(self.player.frame * 28 + 450, 512-400, 28, 32, 0,'', self.player.x, self.player.y, 56, 64)
        elif self.player.face_dir == 3: # 우하
            self.player.image.clip_composite_draw(self.player.frame * 28 + 450, 512-336, 28, 32, 0,'', self.player.x, self.player.y, 56, 64)
        elif self.player.face_dir == -1: # 왼쪽
            self.player.image.clip_composite_draw(self.player.frame * 28 + 450, 512-272, 28, 32, 0,'h', self.player.x, self.player.y, 56, 64)
        elif self.player.face_dir == -2: # 좌상
            self.player.image.clip_composite_draw(self.player.frame * 28 + 450, 512-400, 28, 32, 0,'h', self.player.x, self.player.y, 56, 64)
        elif self.player.face_dir == -3: # 좌하
            self.player.image.clip_composite_draw(self.player.frame * 28 + 450, 512-336, 28, 32, 0,'h', self.player.x, self.player.y, 56, 64)
        elif self.player.face_dir == 0: # 아래
            self.player.image.clip_composite_draw(self.player.frame * 28 + 450, 512-303, 28, 32, 0,'', self.player.x, self.player.y, 56, 64)
        elif self.player.face_dir == 4: # 위
            self.player.image.clip_composite_draw(self.player.frame * 28 + 450, 512-368, 28, 32, 0,'', self.player.x, self.player.y, 56, 64)

class Player:
    def __init__(self):
        self.x, self.y = 400, 400
        self.frame = 0
        self.face_dir = 1
        self.dir = 0
        self.image = load_image('player.png')
        
        self.IDLE = Idle(self)
        self.state_machine = StateMachine()

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()

    def handle_event(self,event):
        self.state_machine.handle_state_event(('INPUT', event))