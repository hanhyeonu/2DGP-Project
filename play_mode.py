from pico2d import *
import game_framework
import game_world
import common

from player import Player
from background import Background
from enemy_frog import EnemyFrog
from enemy_slime import EnemySlime
from enemy_attacker import EnemyAttacker
from enemy_bommer import EnemyBommer


def handle_events():
    global enemy_frog, enemy_slime, enemy_attacker, enemy_bommer

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        # 맵 전환 키 (테스트용)
        elif event.type == SDL_KEYDOWN and event.key == SDLK_7:
            common.background.set_map(1)
            print("맵1로 전환")
        elif event.type == SDL_KEYDOWN and event.key == SDLK_8:
            common.background.set_map(2)
            print("맵2로 전환")
        elif event.type == SDL_KEYDOWN and event.key == SDLK_9:
            common.background.set_map(3)
            print("맵3로 전환")
        elif event.type == SDL_KEYDOWN and event.key == SDLK_0:
            common.background.set_map(4)
            print("맵4(기존 배경)로 전환")
        elif event.type == SDL_KEYDOWN and event.key == SDLK_F1:
            # F1: 개구리 토글
            if enemy_frog is None:
                enemy_frog = EnemyFrog(common.player)
                game_world.add_object(enemy_frog, 2)
                game_world.add_collision_pair('player:enemy', common.player, enemy_frog)
            else:
                game_world.remove_object(enemy_frog)
                enemy_frog = None
        elif event.type == SDL_KEYDOWN and event.key == SDLK_F2:
            # F2: 슬라임 토글
            if enemy_slime is None:
                enemy_slime = EnemySlime(common.player)
                game_world.add_object(enemy_slime, 2)
                game_world.add_collision_pair('player:enemy', common.player, enemy_slime)
            else:
                game_world.remove_object(enemy_slime)
                enemy_slime = None
        elif event.type == SDL_KEYDOWN and event.key == SDLK_F3:
            # F3: 칼 든 몬스터 토글
            if enemy_attacker is None:
                enemy_attacker = EnemyAttacker(common.player)
                game_world.add_object(enemy_attacker, 2)
                game_world.add_collision_pair('player:enemy', common.player, enemy_attacker)
            else:
                game_world.remove_object(enemy_attacker)
                enemy_attacker = None
        elif event.type == SDL_KEYDOWN and event.key == SDLK_F4:
            # F4: 폭탄 몬스터 토글
            if enemy_bommer is None:
                enemy_bommer = EnemyBommer(common.player)
                game_world.add_object(enemy_bommer, 2)
                game_world.add_collision_pair('player:enemy', common.player, enemy_bommer)
            else:
                game_world.remove_object(enemy_bommer)
                enemy_bommer = None
        else:
            common.player.handle_event(event)


def init():
    global enemy_frog, enemy_slime, enemy_attacker, enemy_bommer

    # 통합 배경 생성 (common에 저장)
    common.background = Background()
    game_world.add_object(common.background, 0)

    # 플레이어 생성 (common에 저장)
    common.player = Player()
    game_world.add_object(common.player, 2)

    # 몬스터는 None으로 초기화
    enemy_frog = None
    enemy_slime = None
    enemy_attacker = None
    enemy_bommer = None


def finish():
    game_world.clear()
    pass


def update():
    game_world.update()
    game_world.handle_collisions()


def draw():
    clear_canvas()
    game_world.render()  # camera 인자 제거
    update_canvas()


def pause():
    pass


def resume():
    pass