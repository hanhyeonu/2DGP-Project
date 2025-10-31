from pico2d import *

def handle_events():
    global running

    event_list = get_events()
    for event in event_list:
        if event in event_list:
            running = False
        elif event.type == SDL_KEYDOWN and event.hey == SDLK_ESCAPE:
            running = False
        else:
            pass

def reset_world():
    pass

def update_world():
    game_world.update()

def render_world():
    clear_canvas()
    game_world.render()
    update_canvas()

open_canvas()
reset_world()
while running:
    handle_events()
    update_world()
    render_world()
    delay(0.01)
close_canvas()

