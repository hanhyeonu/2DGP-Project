from pico2d import draw_rectangle


class Wall:
    """벽 타일 충돌 객체"""

    def __init__(self, x, y, size):
        """
        x, y: 월드 좌표 (타일 중심)
        size: 타일 크기 (64x64)
        """
        self.x = x
        self.y = y
        self.size = size
        self.half_size = size // 2

    def update(self):
        pass

    def draw(self, camera=None):
        # 벽은 background에서 이미 그려지므로 여기서는 디버그용으로만 사용
        pass

    def get_bb(self):
        """바운딩 박스 반환 (left, bottom, right, top)"""
        return (
            self.x - self.half_size,
            self.y - self.half_size,
            self.x + self.half_size,
            self.y + self.half_size
        )

    def handle_collision(self, group, other):
        """충돌 처리 - 벽은 아무것도 하지 않음"""
        pass