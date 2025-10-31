from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDLK_RIGHT, SDLK_LEFT, SDLK_UP, SDLK_DOWN, SDL_KEYUP

import game_world
from state_machine import StateMachine


class Idle:

    def __init__(self,player):
        self.player = player

    def enter(self, e):
        self.player.dir = 0

    def exit(self, e):
        pass

    def do(self):
        pass

    def draw(self):
        pass


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
        pass

    def draw(self):
        pass

    def handle_event(self):
        pass