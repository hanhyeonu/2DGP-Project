from pico2d import load_image, get_canvas_width, get_canvas_height, clamp


class Background:
    def __init__(self, player):
        # 플레이어 참조 (스크롤링용)
        self.player = player

        # 화면 크기
        self.cw = get_canvas_width()
        self.ch = get_canvas_height()

        # 줌 설정 (2배 확대)
        self.zoom = 2.0
        self.camera_width = int(self.cw / self.zoom)  # 512
        self.camera_height = int(self.ch / self.zoom)  # 512

        # 월드 크기 (2048x2048)
        self.world_width = 2048
        self.world_height = 2048

        # 타일맵 설정
        self.TILE_SIZE = 64
        self.TILES_X = self.world_width // self.TILE_SIZE
        self.TILES_Y = self.world_height // self.TILE_SIZE

        # 타일 이미지 로드
        self.tile_images = {
            'ground1': load_image('ground1.png'),
            'ground2': load_image('ground2.png'),
            'ground3': load_image('ground3.png'),
            'wall1': load_image('wall1.png'),
            'wall2': load_image('wall2.png')
        }

        # 맵 데이터 (32x32, 0=ground, 1=wall)
        # 빈 배열로 초기화 - 나중에 맵 데이터 채우기
        self.map_data = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]


        self.current_map_type = 1

    def set_map(self, map_number):
        """맵 타입 전환"""
        if map_number in [1, 2, 3]:
            self.current_map_type = map_number

    def is_wall_at(self, world_x, world_y):
        """벽 충돌 체크"""
        tile_x = int(world_x // self.TILE_SIZE)
        tile_y = int(world_y // self.TILE_SIZE)

        if tile_x < 0 or tile_x >= self.TILES_X or tile_y < 0 or tile_y >= self.TILES_Y:
            return True

        flipped_y = self.TILES_Y - 1 - tile_y
        return self.map_data[flipped_y][tile_x] == 1

    def update(self):
        pass

    def draw(self):
        """Lecture18 스타일 스크롤링 + 2배 줌"""
        # 줌 적용한 window 계산
        self.window_left = clamp(0, int(self.player.x) - self.camera_width // 2, self.world_width - self.camera_width)
        self.window_bottom = clamp(0, int(self.player.y) - self.camera_height // 2, self.world_height - self.camera_height)

        # 타일 그리기도 줌 적용
        start_tile_x = self.window_left // self.TILE_SIZE
        end_tile_x = min((self.window_left + self.camera_width) // self.TILE_SIZE + 1, self.TILES_X)
        start_tile_y = self.window_bottom // self.TILE_SIZE
        end_tile_y = min((self.window_bottom + self.camera_height) // self.TILE_SIZE + 1, self.TILES_Y)

        for y in range(start_tile_y, end_tile_y):
            for x in range(start_tile_x, end_tile_x):
                world_x = x * self.TILE_SIZE
                world_y = y * self.TILE_SIZE

                # 화면 좌표 계산 시 줌 적용
                screen_x = (world_x - self.window_left) * self.zoom + self.TILE_SIZE // 2 * self.zoom
                screen_y = (world_y - self.window_bottom) * self.zoom + self.TILE_SIZE // 2 * self.zoom

                # 타일 크기도 줌 적용
                tile_size = int(self.TILE_SIZE * self.zoom)

                # 맵3일 때는 벽 없이 ground3만
                if self.current_map_type == 3:
                    self.tile_images['ground3'].draw(screen_x, screen_y, tile_size, tile_size)
                else:
                    # 맵1, 맵2일 때는 타일 값에 따라 그리기
                    if len(self.map_data) > 0 and len(self.map_data[0]) > 0:
                        flipped_y = self.TILES_Y - 1 - y
                        if 0 <= flipped_y < len(self.map_data) and 0 <= x < len(self.map_data[0]):
                            tile_value = self.map_data[flipped_y][x]

                            if tile_value == 0:
                                if self.current_map_type == 1:
                                    self.tile_images['ground1'].draw(screen_x, screen_y, tile_size, tile_size)
                                elif self.current_map_type == 2:
                                    self.tile_images['ground2'].draw(screen_x, screen_y, tile_size, tile_size)
                            elif tile_value == 1:
                                if self.current_map_type == 1:
                                    self.tile_images['wall1'].draw(screen_x, screen_y, tile_size, tile_size)
                                else:
                                    self.tile_images['wall2'].draw(screen_x, screen_y, tile_size, tile_size)
