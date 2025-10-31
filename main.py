from pico2d import *

def handle_events():
    global running

    event_list = get_events()
    for event in event_list:
        if event in event_list:
            runnig = False
        elif event.type == SDL_KEYDOWN and event.hey == SDLK_ESCAPE:
            running = False
        else:
            pass

def reset_world():
    pass

def update_world():
    pass

def render_world():
    pass

open_canvas()
reset_world()
while running:
    handle_events()
    update_world()
    render_world()
    delay(0.01)
close_canvas()

