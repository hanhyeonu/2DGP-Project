class Camera:
    def __init__(self, target=None):
        self.x = 512  # 카메라 중심 x (월드 좌표)
        self.y = 512  # 카메라 중심 y (월드 좌표)
        self.target = target  # 따라갈 대상 (플레이어)

        # 화면 크기
        self.screen_width = 1024
        self.screen_height = 1024

        # 맵 크기
        self.map_width = 2048
        self.map_height = 2048

    def update(self):
        if self.target:
            # 카메라를 타겟 위치로 이동
            self.x = self.target.x
            self.y = self.target.y

            # 맵 경계 처리 (카메라가 맵 밖을 보지 않도록)
            half_width = self.screen_width / 2
            half_height = self.screen_height / 2

            # 카메라 x 제한
            if self.x < half_width:
                self.x = half_width
            elif self.x > self.map_width - half_width:
                self.x = self.map_width - half_width

            # 카메라 y 제한
            if self.y < half_height:
                self.y = half_height
            elif self.y > self.map_height - half_height:
                self.y = self.map_height - half_height

    def apply(self, world_x, world_y):
        """월드 좌표를 화면 좌표로 변환"""
        screen_x = world_x - self.x + self.screen_width / 2
        screen_y = world_y - self.y + self.screen_height / 2
        return screen_x, screen_y
