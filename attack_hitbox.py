class AttackHitbox:
    """공격 판정용 임시 히트박스"""
    def __init__(self, owner, x, y, width, height, duration=0.1):
        self.owner = owner
        # owner의 현재 위치 기준 오프셋 저장
        self.offset_x = x - owner.x
        self.offset_y = y - owner.y
        self.width = width
        self.height = height
        self.half_width = width // 2
        self.half_height = height // 2
        self.duration = duration
        self.elapsed_time = 0
        self.hit_targets = []

    def update(self):
        import game_framework
        import game_world

        # owner가 죽었으면 히트박스 즉시 제거
        if hasattr(self.owner, 'is_dead') and self.owner.is_dead:
            game_world.remove_object(self)
            return

        self.elapsed_time += game_framework.frame_time
        if self.elapsed_time >= self.duration:
            game_world.remove_object(self)

    def draw(self, camera=None):
        import play_mode
        from pico2d import draw_rectangle

        # owner의 현재 위치 + offset
        x = self.owner.x + self.offset_x
        y = self.owner.y + self.offset_y

        if hasattr(play_mode, 'background') and play_mode.background:
            screen_x = (x - play_mode.background.window_left) * play_mode.background.zoom
            screen_y = (y - play_mode.background.window_bottom) * play_mode.background.zoom
            hw = self.half_width * play_mode.background.zoom
            hh = self.half_height * play_mode.background.zoom
        else:
            screen_x, screen_y = x, y
            hw, hh = self.half_width, self.half_height

        draw_rectangle(screen_x - hw, screen_y - hh, screen_x + hw, screen_y + hh)

    def get_bb(self):
        # owner의 현재 위치 + offset
        x = self.owner.x + self.offset_x
        y = self.owner.y + self.offset_y
        return (x - self.half_width, y - self.half_height,
                x + self.half_width, y + self.half_height)

    def handle_collision(self, group, other):
        if other in self.hit_targets:
            return

        self.hit_targets.append(other)

        # 몬스터가 플레이어를 공격한 경우
        if group == 'monster_attack:player':
            if hasattr(other, 'take_damage'):
                other.take_damage(10)

        # 피격 시 깜빡임 효과 활성화
        if hasattr(other, 'hit_duration'):
            other.hit_timer = other.hit_duration
            print(f"Hit effect activated! hit_timer set to {other.hit_timer}")
        elif hasattr(other, 'hit_timer'):
            other.hit_timer = 0.5
            print(f"Hit effect activated! hit_timer set to 0.5")
