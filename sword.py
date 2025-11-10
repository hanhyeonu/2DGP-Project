from pico2d import load_image
import game_world
import game_framework
import math

SLASH_SPEED = 5.0

class Sword:
    sword_image = None
    slash_image = None

    def __init__(self, x, y, face_dir, player=None):
        if Sword.sword_image == None:
            Sword.sword_image = load_image('sword.png')
        if Sword.slash_image == None:
            Sword.slash_image = load_image('Slash00.png')

        self.player_x = x
        self.player_y = y
        self.face_dir = face_dir
        self.player = player

        self.base_angle = self.get_base_angle()
        self.current_angle = self.base_angle + math.radians(30)
        self.target_angle = self.base_angle - math.radians(30)

        self.slash_frame = 0
        self.frame_time = 0
        self.frame_speed = 15

        self.sword_distance = 25
        self.finished = False

    def get_base_angle(self):
        angle_map = {
            1: 0,
            -1: math.pi,
            2: math.pi / 4,
            -2: math.pi * 3 / 4,
            3: -math.pi / 4,
            -3: -math.pi * 3 / 4,
            4: math.pi / 2,
            0: -math.pi / 2
        }
        return angle_map.get(self.face_dir, 0)

    def update(self):
        if self.finished:
            return

        self.current_angle -= SLASH_SPEED * game_framework.frame_time

        if self.current_angle <= self.target_angle:
            self.finished = True
            if self.player:
                self.player.is_attacking = False
            game_world.remove_object(self)
            return

        self.frame_time += game_framework.frame_time
        if self.frame_time >= 1.0 / self.frame_speed:
            self.frame_time = 0
            self.slash_frame = (self.slash_frame + 1) % 8

    def draw(self):
        sword_x = self.player_x + self.sword_distance * math.cos(self.current_angle)
        sword_y = self.player_y + self.sword_distance * math.sin(self.current_angle)

        self.sword_image.composite_draw(
            self.current_angle - math.pi / 2, '',
            sword_x, sword_y,
            22, 70
        )

        slash_distance = self.sword_distance + 35
        slash_x = self.player_x + slash_distance * math.cos(self.current_angle)
        slash_y = self.player_y + slash_distance * math.sin(self.current_angle)

        frame_x = self.slash_frame * 32
        self.slash_image.clip_composite_draw(
            frame_x, 0,
            32, 96,
            self.current_angle - math.pi / 2 + math.pi / 2, '',
            slash_x, slash_y,
            32, 96
        )