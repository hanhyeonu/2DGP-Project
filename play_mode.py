from pico2d import *
from pico2d import SDLK_F1, SDLK_F2, SDLK_F3, SDLK_F4

import game_framework
import game_world

from player import Player
from background import Background
from enemy_frog import EnemyFrog
from enemy_slime import EnemySlime
from enemy_attacker import EnemyAttacker
from enemy_bommer import EnemyBommer

player = None
background = None
enemy_frog = None
enemy_slime = None
enemy_attacker = None
enemy_bommer = None


def handle_events():
    global enemy_frog, enemy_slime, enemy_attacker, enemy_bommer

    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_F1:
            # F1: 개구리 토글
            if enemy_frog is None:
                enemy_frog = EnemyFrog(player)
                game_world.add_object(enemy_frog, 2)
            else:
                game_world.remove_object(enemy_frog)
                enemy_frog = None
        elif event.type == SDL_KEYDOWN and event.key == SDLK_F2:
            # F2: 슬라임 토글
            if enemy_slime is None:
                enemy_slime = EnemySlime(player)
                game_world.add_object(enemy_slime, 2)
            else:
                game_world.remove_object(enemy_slime)
                enemy_slime = None
        elif event.type == SDL_KEYDOWN and event.key == SDLK_F3:
            # F3: 칼 든 몬스터 토글
            if enemy_attacker is None:
                enemy_attacker = EnemyAttacker(player)
                game_world.add_object(enemy_attacker, 2)
            else:
                game_world.remove_object(enemy_attacker)
                enemy_attacker = None
        elif event.type == SDL_KEYDOWN and event.key == SDLK_F4:
            # F4: 폭탄 몬스터 토글
            if enemy_bommer is None:
                enemy_bommer = EnemyBommer(player)
                game_world.add_object(enemy_bommer, 2)
            else:
                game_world.remove_object(enemy_bommer)
                enemy_bommer = None
        else:
            player.handle_event(event)


def init():
    global player, background, enemy_frog, enemy_slime, enemy_attacker, enemy_bommer

    background = Background()
    game_world.add_object(background, 0)

    player = Player()
    game_world.add_object(player, 2)

    # 몬스터는 키 입력으로 생성하므로 None으로 초기화
    enemy_frog = None
    enemy_slime = None
    enemy_attacker = None
    enemy_bommer = None


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