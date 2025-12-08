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
from gate import Gate

# 맵별 몬스터 리스트
map1_frogs = []
map1_slimes = []
map2_attackers = []
map2_bommers = []

# 게이트 관리
current_gate = None
last_monster_pos = None  # 마지막으로 죽은 몬스터 위치
gate_created_for_map = -1  # 이미 게이트가 생성된 맵

# 맵1 방 좌표 (player 시작 방 제외)
MAP1_ROOMS = [
    (1696, 1664),   # 우상단 방
    (1024, 960),    # 중앙 방
    (256, 576),     # 좌하단 방
    (1696, 256),    # 우하단 방
]

# 맵2 방 좌표 (맵1과 동일한 위치)
MAP2_ROOMS = [
    (1696, 1664),   # 우상단 방
    (1024, 960),    # 중앙 방
    (256, 576),     # 좌하단 방
    (1696, 256),    # 우하단 방
]


def create_map1_monsters():
    """맵1: frog 6마리, slime 6마리 배치 (1,2,2,1 분포)"""
    global map1_frogs, map1_slimes

    map1_frogs = []
    map1_slimes = []

    # 각 방에 배치할 몬스터 수 (1,2,2,1)
    monsters_per_room = [1, 2, 2, 1]  # 총 6마리

    for room_idx, (rx, ry) in enumerate(MAP1_ROOMS):
        count = monsters_per_room[room_idx]

        for i in range(count):
            # Frog 배치
            frog = EnemyFrog(player)
            frog.x = rx + (i - count//2) * 60  # 방 안에서 분산
            frog.y = ry + 30
            frog.background = background
            game_world.add_object(frog, 2)
            game_world.add_collision_pair('player_attack:monster', None, frog)
            game_world.add_collision_pair('monster_attack:player', None, player)
            game_world.add_collision_pair('arrow:monster', None, frog)
            map1_frogs.append(frog)

            # Slime 배치
            slime = EnemySlime(player)
            slime.x = rx + (i - count//2) * 60
            slime.y = ry - 30
            slime.background = background
            game_world.add_object(slime, 2)
            game_world.add_collision_pair('player_attack:monster', None, slime)
            game_world.add_collision_pair('monster_attack:player', None, player)
            game_world.add_collision_pair('arrow:monster', None, slime)
            map1_slimes.append(slime)


def create_map2_monsters():
    """맵2: attacker 6마리, bommer 6마리 배치 (1,2,2,1 분포)"""
    global map2_attackers, map2_bommers

    map2_attackers = []
    map2_bommers = []

    monsters_per_room = [1, 2, 2, 1]

    for room_idx, (rx, ry) in enumerate(MAP2_ROOMS):
        count = monsters_per_room[room_idx]

        for i in range(count):
            # Attacker 배치
            attacker = EnemyAttacker(player)
            attacker.x = rx + (i - count//2) * 60
            attacker.y = ry + 30
            attacker.background = background
            game_world.add_object(attacker, 2)
            game_world.add_collision_pair('player_attack:monster', None, attacker)
            game_world.add_collision_pair('monster_attack:player', None, player)
            game_world.add_collision_pair('arrow:monster', None, attacker)
            map2_attackers.append(attacker)

            # Bommer 배치
            bommer = EnemyBommer(player)
            bommer.x = rx + (i - count//2) * 60
            bommer.y = ry - 30
            bommer.background = background
            game_world.add_object(bommer, 2)
            game_world.add_collision_pair('player_attack:monster', None, bommer)
            game_world.add_collision_pair('monster_attack:player', None, player)
            game_world.add_collision_pair('arrow:monster', None, bommer)
            map2_bommers.append(bommer)


def clear_all_monsters():
    """모든 몬스터 제거"""
    global map1_frogs, map1_slimes, map2_attackers, map2_bommers

    all_monsters = map1_frogs + map1_slimes + map2_attackers + map2_bommers
    for monster in all_monsters:
        if monster in game_world.objects[2]:
            game_world.remove_object(monster)

    map1_frogs = []
    map1_slimes = []
    map2_attackers = []
    map2_bommers = []


def create_gate(x, y):
    """게이트 생성"""
    global current_gate

    # 기존 게이트가 있으면 제거
    if current_gate:
        if current_gate in game_world.objects[3]:
            game_world.remove_object(current_gate)

    # 새 게이트 생성 (레이어 3 - 타일보다 위에 그려짐)
    current_gate = Gate(x, y)
    game_world.add_object(current_gate, 3)
    game_world.add_collision_pair('player:gate', player, current_gate)
    print(f"Gate created at ({x}, {y})")


def remove_gate():
    """게이트 제거"""
    global current_gate

    if current_gate and current_gate in game_world.objects[3]:
        game_world.remove_object(current_gate)
    current_gate = None


def check_all_monsters_cleared():
    """모든 몬스터가 제거되었는지 확인하고 게이트 생성"""
    global map1_frogs, map1_slimes, map2_attackers, map2_bommers, gate_created_for_map, last_monster_pos

    current_map = common.background.current_map_type

    # 이미 이 맵에서 게이트를 생성했으면 무시
    if gate_created_for_map == current_map:
        return

    # 맵1: frog와 slime이 모두 제거되면
    if current_map == 1:
        all_monsters = map1_frogs + map1_slimes
        alive_monsters = [m for m in all_monsters if not m.is_dead]

        if len(alive_monsters) == 0 and len(all_monsters) > 0:
            # 마지막으로 살아있던 몬스터 위치 찾기
            dead_monsters = [m for m in all_monsters if m.is_dead]
            if dead_monsters:
                last_monster = dead_monsters[-1]
                create_gate(last_monster.x, last_monster.y)
                gate_created_for_map = 1

    # 맵2: attacker와 bommer가 모두 제거되면
    elif current_map == 2:
        all_monsters = map2_attackers + map2_bommers
        alive_monsters = [m for m in all_monsters if not m.is_dead]

        if len(alive_monsters) == 0 and len(all_monsters) > 0:
            # 마지막으로 살아있던 몬스터 위치 찾기
            dead_monsters = [m for m in all_monsters if m.is_dead]
            if dead_monsters:
                last_monster = dead_monsters[-1]
                create_gate(last_monster.x, last_monster.y)
                gate_created_for_map = 2


def transition_to_next_map():
    """다음 맵으로 전환"""
    global gate_created_for_map

    current_map = common.background.current_map_type

    if current_map == 0:  # 마을 -> 맵1
        common.background.set_map(1)
        common.player.x = 288
        common.player.y = 1824
        clear_all_monsters()
        remove_gate()
        gate_created_for_map = -1
        create_map1_monsters()
        print("맵1로 전환 - frog 6, slime 6 배치")

    elif current_map == 1:  # 맵1 -> 맵2
        common.background.set_map(2)
        common.player.x = 288
        common.player.y = 1824
        clear_all_monsters()
        remove_gate()
        gate_created_for_map = -1
        create_map2_monsters()
        print("맵2로 전환 - attacker 6, bommer 6 배치")

    elif current_map == 2:  # 맵2 -> 맵3
        common.background.set_map(3)
        common.player.x = 1056
        common.player.y = 992
        clear_all_monsters()
        remove_gate()
        gate_created_for_map = -1
        print("맵3로 전환 - 보스맵")


def handle_events():
    global gate_created_for_map

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        # 맵 전환 키 (테스트용)
        elif event.type == SDL_KEYDOWN and event.key == SDLK_7:
            transition_to_next_map()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_0:
            # 마을맵으로 (테스트용)
            common.background.set_map(0)
            common.player.x = 1024
            common.player.y = 1024
            clear_all_monsters()
            remove_gate()
            gate_created_for_map = -1
            create_gate(1024, 512)
            print("마을맵으로 전환")
        elif event.type == SDL_KEYDOWN and event.key == SDLK_8:
            # 맵1로 (테스트용)
            common.background.set_map(1)
            common.player.x = 288
            common.player.y = 1824
            clear_all_monsters()
            remove_gate()
            gate_created_for_map = -1
            create_map1_monsters()
            print("맵1로 전환 - frog 6, slime 6 배치")
        elif event.type == SDL_KEYDOWN and event.key == SDLK_9:
            # 맵3로 (테스트용)
            common.background.set_map(3)
            common.player.x = 1056
            common.player.y = 992
            clear_all_monsters()
            remove_gate()
            gate_created_for_map = -1
            print("맵3로 전환 - 보스맵")
        else:
            common.player.handle_event(event)


def init():
    global player, background

    # 먼저 player 생성
    player = Player()
    game_world.add_object(player, 2)

    # background 생성 (player 전달)
    background = Background(player)
    game_world.add_object(background, 0)

    # player에 background 연결
    player.background = background

    # common에도 저장 (기존 코드 호환성)
    common.player = player
    common.background = background

    # 마을맵에서 시작, 게이트 생성
    background.set_map(0)
    player.x = 1024
    player.y = 1024
    create_gate(1024, 512)


def finish():
    game_world.clear()
    pass


def update():
    game_world.update()
    game_world.handle_collisions()

    # 몬스터 제거 확인 및 게이트 생성
    check_all_monsters_cleared()

    # player-gate 충돌 확인
    if current_gate and game_world.collide(player, current_gate):
        transition_to_next_map()


def draw():
    clear_canvas()
    game_world.render()  # camera 인자 제거
    update_canvas()


def pause():
    pass


def resume():
    pass