import game_world
import game_framework
from arrow import Arrow
import math


class Skill:
    def __init__(self, player):
        self.player = player
        self.skill_timer = 0
        self.arrow_count = 0
        self.arrow_delay = 0.05
        self.total_arrows = 5
        self.angles = []

    def activate(self):
        pass

    def update(self):
        pass


class BowSkill(Skill):
    def __init__(self, player):
        super().__init__(player)

    def activate(self):
        self.skill_timer = 0
        self.arrow_count = 0

        base_angle = self.get_base_angle()
        spread_range = math.radians(60)

        self.angles = []
        for i in range(self.total_arrows):
            angle = base_angle + (spread_range / (self.total_arrows - 1)) * i - spread_range / 2
            self.angles.append(angle)

    def get_base_angle(self):
        face_dir = self.player.face_dir

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

        return angle_map.get(face_dir, 0)

    def update(self):
        if self.arrow_count >= self.total_arrows or not self.angles:
            return

        self.skill_timer += game_framework.frame_time

        if self.skill_timer >= self.arrow_delay:
            self.skill_timer = 0
            self.fire_arrow(self.angles[self.arrow_count])
            self.arrow_count += 1

    def fire_arrow(self, angle):
        offset_distance = 20
        offset_x = offset_distance * math.cos(angle)
        offset_y = offset_distance * math.sin(angle)

        arrow = Arrow(self.player.x + offset_x, self.player.y + offset_y, self.player.face_dir, angle)
        game_world.add_object(arrow, 1)

    def is_active(self):
        return self.angles and self.arrow_count < self.total_arrows