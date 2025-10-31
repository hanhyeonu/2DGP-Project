from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDLK_RIGHT, SDLK_LEFT, SDLK_UP, SDLK_DOWN, SDL_KEYUP

import game_world


class Idle:
    pass


class Player:
    def __init__(self):
        self.x, self.y = 400, 400
        self.frame = 0
        self.face_dir = 1
        self.image = load_image('player.png')
        
        self.IDLE = Idle(self)

    def update(self):
        pass

    def draw(self):
        pass

    def handle_event(self):
        pass