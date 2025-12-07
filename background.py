from pico2d import load_image, get_canvas_width, get_canvas_height, clamp
import common


class Background:
    def __init__(self):
        # 화면 크기
        self.cw = get_canvas_width()
        self.ch = get_canvas_height()

        # 카메라 줌 설정
        self.zoom = 2.0  # 2배 확대
        self.camera_width = int(self.cw / self.zoom)  # 실제 보는 월드 영역
        self.camera_height = int(self.ch / self.zoom)

        # 기존 배경 이미지
        self.kyoten_image = load_image('kyoten.png')
        self.grass_tile = load_image('base_grass_cc.png')

        # 타일맵 이미지 로드
        self.tile_images = {
            'ground1': load_image('ground1.png'),
            'ground2': load_image('ground2.png'),
            'ground3': load_image('ground3.png'),
            'wall1': load_image('wall1.png'),
            'wall2': load_image('wall2.png')
        }

        # 월드 크기 설정
        self.world_width = 2048
        self.world_height = 2048
        self.tile_size = 32
        self.grass_height = int(self.world_height * 0.7)

        # 타일맵 설정
        self.TILE_SIZE = 32
        self.TILE_SCALE = 2
        self.SCALED_TILE_SIZE = self.TILE_SIZE * self.TILE_SCALE  # 64x64
        self.TILES_X = self.world_width // self.SCALED_TILE_SIZE  # 32개
        self.TILES_Y = self.world_height // self.SCALED_TILE_SIZE  # 32개

        # 맵 데이터 정의 (32x32 2차원 배열)
        # 0: ground (이동 가능), 1: wall (이동 불가)

        # 맵1: 던전 스타일 (ground1 + wall1)
        # 구조: Z자 모양, 4개 몬스터 방 (좌상단 → 우상단 → 중앙 → 좌하단 → 우하단)
        # 시작: 좌상단, 포탈: 우하단
        self.map1 = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1],
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
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]

        # 맵2: 사막 던전 스타일 (ground2 + wall2)
        # 구조: N자 모양, 4개 몬스터 방 (좌하단 → 좌상단 → 중앙 → 우하단 → 우상단)
        # 시작: 좌하단, 포탈: 우상단
        self.map2 = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]

        # 맵3: 바다 던전 (ground3만 사용)
        # 구조: 전체 ground, 길/방 없음
        self.map3 = [[0] * 32 for _ in range(32)]

        # 현재 맵 설정
        self.current_map = self.map1
        self.current_map_number = 1
        self.use_tilemap = True

        # 벽 충돌 객체 리스트 (사용 안 함 - 타일맵 체크로 대체)
        self.walls = []

    def is_wall_at(self, world_x, world_y):
        """주어진 월드 좌표가 벽인지 체크"""
        # 맵3이나 타일맵 사용 안 할 때는 벽 없음
        if not self.use_tilemap or self.current_map_number == 3:
            return False

        # 월드 좌표 → 타일 좌표
        tile_x = int(world_x // self.SCALED_TILE_SIZE)
        tile_y = int(world_y // self.SCALED_TILE_SIZE)

        # 맵 범위 체크
        if tile_x < 0 or tile_x >= self.TILES_X or tile_y < 0 or tile_y >= self.TILES_Y:
            return True  # 맵 밖은 벽으로 취급

        # Y축 반전 적용
        flipped_y = self.TILES_Y - 1 - tile_y

        # 타일 값 체크 (1 = 벽)
        return self.current_map[flipped_y][tile_x] == 1

    def create_walls(self):
        """벽 생성 - 더 이상 사용 안 함 (타일맵 체크로 대체)"""
        # 기존 벽 제거
        from wall import Wall
        import game_world

        for wall in self.walls:
            game_world.remove_object(wall)
        self.walls.clear()

    def set_map(self, map_number):
        """맵 전환"""
        if map_number == 1:
            self.current_map = self.map1
            self.current_map_number = 1
            self.use_tilemap = True
        elif map_number == 2:
            self.current_map = self.map2
            self.current_map_number = 2
            self.use_tilemap = True
        elif map_number == 3:
            self.current_map = self.map3
            self.current_map_number = 3
            self.use_tilemap = True
        elif map_number == 4:
            self.current_map_number = 4
            self.use_tilemap = False  # 기존 배경 사용

    def update(self):
        pass

    def draw_original_background(self):
        """기존 배경 그리기 (kyoten + grass) - 스크롤링 적용 + 2배 줌"""
        # 플레이어 위치 기준으로 window 계산 (줌 적용)
        window_left = clamp(0, int(common.player.x) - self.camera_width // 2, self.world_width - self.camera_width)
        window_bottom = clamp(0, int(common.player.y) - self.camera_height // 2, self.world_height - self.camera_height)

        # 잔디 타일 그리기
        tiles_x = self.world_width // self.tile_size + 1
        tiles_y = self.grass_height // self.tile_size + 1

        half_tile = self.tile_size // 2

        for y in range(tiles_y):
            for x in range(tiles_x):
                world_x = x * self.tile_size
                world_y = y * self.tile_size

                # camera window 영역 안에 있는지 확인
                if (world_x >= window_left and world_x < window_left + self.camera_width and
                        world_y >= window_bottom and world_y < window_bottom + self.camera_height):
                    # 화면 좌표로 변환 (중심점으로 보정 + 줌 적용)
                    screen_x = (world_x - window_left) * self.zoom + half_tile * self.zoom
                    screen_y = (world_y - window_bottom) * self.zoom + half_tile * self.zoom
                    self.grass_tile.draw(screen_x, screen_y, self.tile_size * self.zoom, self.tile_size * self.zoom)

        # 교토 이미지 그리기 (중앙에 고정 + 줌 적용)
        kyoten_x = (self.world_width // 2 - window_left) * self.zoom
        kyoten_y = (self.world_height // 2 - window_bottom) * self.zoom
        self.kyoten_image.draw(kyoten_x, kyoten_y, self.world_width * self.zoom, self.world_height * self.zoom)

    def draw_tilemap(self):
        """타일맵 그리기 - 스크롤링 적용 + 2배 줌"""
        # 플레이어 위치 기준으로 window 계산 (줌 적용)
        window_left = clamp(0, int(common.player.x) - self.camera_width // 2, self.world_width - self.camera_width)
        window_bottom = clamp(0, int(common.player.y) - self.camera_height // 2, self.world_height - self.camera_height)

        # 보이는 타일만 그리기
        start_tile_x = window_left // self.SCALED_TILE_SIZE
        end_tile_x = min((window_left + self.camera_width) // self.SCALED_TILE_SIZE + 1, self.TILES_X)
        start_tile_y = window_bottom // self.SCALED_TILE_SIZE
        end_tile_y = min((window_bottom + self.camera_height) // self.SCALED_TILE_SIZE + 1, self.TILES_Y)

        # 타일 크기의 절반 (중심점 보정)
        half_tile = self.SCALED_TILE_SIZE // 2

        for y in range(start_tile_y, end_tile_y):
            for x in range(start_tile_x, end_tile_x):
                # Y축 반전: 배열의 위쪽이 화면 위쪽에 오도록
                flipped_y = self.TILES_Y - 1 - y
                tile_value = self.current_map[flipped_y][x]

                # 월드 좌표 (타일의 왼쪽 아래 모서리)
                world_x = x * self.SCALED_TILE_SIZE
                world_y = y * self.SCALED_TILE_SIZE

                # 화면 좌표로 변환 (중심점으로 보정 + 줌 적용)
                screen_x = (world_x - window_left) * self.zoom + half_tile * self.zoom
                screen_y = (world_y - window_bottom) * self.zoom + half_tile * self.zoom

                # 타일 크기도 줌 적용
                tile_draw_size = self.SCALED_TILE_SIZE * self.zoom

                # 타일 그리기
                if self.current_map_number == 1:
                    if tile_value == 0:
                        self.tile_images['ground1'].draw(screen_x, screen_y, tile_draw_size, tile_draw_size)
                    elif tile_value == 1:
                        self.tile_images['wall1'].draw(screen_x, screen_y, tile_draw_size, tile_draw_size)
                elif self.current_map_number == 2:
                    if tile_value == 0:
                        self.tile_images['ground2'].draw(screen_x, screen_y, tile_draw_size, tile_draw_size)
                    elif tile_value == 1:
                        self.tile_images['wall2'].draw(screen_x, screen_y, tile_draw_size, tile_draw_size)
                elif self.current_map_number == 3:
                    self.tile_images['ground3'].draw(screen_x, screen_y, tile_draw_size, tile_draw_size)

    def draw(self):
        """통합 렌더링 - 스크롤링 방식"""
        if self.use_tilemap:
            self.draw_tilemap()
        else:
            self.draw_original_background()