from pico2d import open_canvas, close_canvas
import game_framework
import play_mode as start_mode

open_canvas(1200, 900)
game_framework.run(start_mode)
close_canvas()

# 시간에 맞게 수정 완.