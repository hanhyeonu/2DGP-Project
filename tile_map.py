from pico2d import load_image

# 타일 크기 설정
TILE_SIZE = 32  # 원본 이미지 크기
TILE_SCALE = 4  # 4배 확대
SCALED_TILE_SIZE = TILE_SIZE * TILE_SCALE  # 128x128

# 맵 크기 설정
MAP_WIDTH = 1024
MAP_HEIGHT = 1024
TILES_X = MAP_WIDTH // SCALED_TILE_SIZE  # 8개
TILES_Y = MAP_HEIGHT // SCALED_TILE_SIZE  # 8개


class TileMap:
    def __init__(self):
        # 타일 이미지 로드
        self.tiles = {
            'ground1': load_image('ground1.png'),
            'ground2': load_image('ground2.png'),
            'ground3': load_image('ground3.png'),
            'wall1': load_image('wall1.png'),
            'wall2': load_image('wall2.png')
        }

        # 맵 데이터 정의 (8x8 2차원 배열)
        # 0: ground, 1: wall

        # 맵1: ground1 + wall1
        self.map1 = [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 1, 0, 0, 1],
            [1, 0, 0, 1, 1, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1]
        ]

        # 맵2: ground2 + wall2
        self.map2 = [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 0, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1]
        ]

        # 맵3: ground3만 (벽 없음)
        self.map3 = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]

        # 현재 맵 설정
        self.current_map = self.map1
        self.current_map_number = 1

    def set_map(self, map_number):
        """맵 전환"""
        if map_number == 1:
            self.current_map = self.map1
            self.current_map_number = 1
        elif map_number == 2:
            self.current_map = self.map2
            self.current_map_number = 2
        elif map_number == 3:
            self.current_map = self.map3
            self.current_map_number = 3

    def update(self):
        pass

    def draw(self, camera=None):
        """맵 렌더링"""
        for y in range(TILES_Y):
            for x in range(TILES_X):
                tile_value = self.current_map[y][x]

                # 월드 좌표 계산 (왼쪽 하단 기준)
                world_x = x * SCALED_TILE_SIZE + SCALED_TILE_SIZE // 2
                world_y = y * SCALED_TILE_SIZE + SCALED_TILE_SIZE // 2

                # 카메라 적용
                if camera:
                    draw_x, draw_y = camera.apply(world_x, world_y)
                else:
                    draw_x, draw_y = world_x, world_y

                # 타일 그리기
                if self.current_map_number == 1:
                    # 맵1: ground1 + wall1
                    if tile_value == 0:
                        self.tiles['ground1'].draw(draw_x, draw_y, SCALED_TILE_SIZE, SCALED_TILE_SIZE)
                    elif tile_value == 1:
                        self.tiles['wall1'].draw(draw_x, draw_y, SCALED_TILE_SIZE, SCALED_TILE_SIZE)

                elif self.current_map_number == 2:
                    # 맵2: ground2 + wall2
                    if tile_value == 0:
                        self.tiles['ground2'].draw(draw_x, draw_y, SCALED_TILE_SIZE, SCALED_TILE_SIZE)
                    elif tile_value == 1:
                        self.tiles['wall2'].draw(draw_x, draw_y, SCALED_TILE_SIZE, SCALED_TILE_SIZE)

                elif self.current_map_number == 3:
                    # 맵3: ground3만
                    self.tiles['ground3'].draw(draw_x, draw_y, SCALED_TILE_SIZE, SCALED_TILE_SIZE)