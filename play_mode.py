from pico2d import *

import game_framework
import game_world

from player import Player
from background import Background
from enemy_frog import EnemyFrog

player = None
background = None
enemy_frog = None


def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        else:
            player.handle_event(event)


def init():
    global player, background, enemy_frog

    background = Background()
    game_world.add_object(background, 0)

    player = Player()
    game_world.add_object(player, 2)

    enemy_frog = EnemyFrog(player)
    game_world.add_object(enemy_frog, 2)


def update():
    game_world.update()


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()


def finish():
    game_world.clear()


def pause():
    pass


def resume():
    pass