from pico2d import load_image, get_canvas_width, get_canvas_height, clamp


class Background:
    def __init__(self, player):
        # 플레이어 참조 (스크롤링용)
        self.player = player

        # 화면 크기
        self.cw = get_canvas_width()
        self.ch = get_canvas_height()

        # 줌 설정 (맵에 따라 다름)
        self.zoom = 1.0  # 기본값
        self.camera_width = int(self.cw / self.zoom)
        self.camera_height = int(self.ch / self.zoom)

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
            'wall2': load_image('wall2.png'),
            'base_grass': load_image('base_grass_cc.png'),
            'kyoten': load_image('kyoten.png')
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


        # 현재 맵 타입: 0=마을, 1=던전1, 2=던전2, 3=보스맵
        self.current_map_type = 0

    def set_map(self, map_number):
        """맵 타입 전환"""
        if map_number in [0, 1, 2, 3]:
            self.current_map_type = map_number

            # 맵에 따라 줌 설정
            if map_number == 0 or map_number == 3:
                # 마을맵과 보스맵: 1배 줌 (넓은 영역)
                self.zoom = 1.0
            else:
                # 던전맵 1, 2: 2배 줌 (좁은 영역)
                self.zoom = 2.0

            # 카메라 크기 재계산
            self.camera_width = int(self.cw / self.zoom)
            self.camera_height = int(self.ch / self.zoom)

    def is_wall_at(self, world_x, world_y):
        """벽 충돌 체크"""
        # 마을맵(0)과 보스맵(3)은 충돌 없음
        if self.current_map_type == 0 or self.current_map_type == 3:
            return False

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

        # 타일 그리기
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

                # 마을맵 (map_type 0) - base_grass_cc.png + kyoten.png 타일로 전체 덮기
                if self.current_map_type == 0:
                    # 먼저 base_grass_cc.png로 배경 그리기
                    self.tile_images['base_grass'].draw(screen_x, screen_y, tile_size, tile_size)
                    # 그 위에 kyoten.png로 덮기
                    self.tile_images['kyoten'].draw(screen_x, screen_y, tile_size, tile_size)

                # 보스맵 (map_type 3) - ground3.png 타일로 전체 덮기
                elif self.current_map_type == 3:
                    self.tile_images['ground3'].draw(screen_x, screen_y, tile_size, tile_size)

                # 던전맵 (map_type 1, 2) - 타일 데이터에 따라 그리기
                else:
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
