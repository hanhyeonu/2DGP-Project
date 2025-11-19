from pico2d import load_image


class Background:
    def __init__(self):
        self.kyoten_image = load_image('kyoten.png')
        self.grass_tile = load_image('base_grass_cc.png')
        self.canvas_width = 2048
        self.canvas_height = 2048
        self.tile_size = 32

        self.grass_height = int(self.canvas_height * 0.7)

    def update(self):
        pass

    def draw(self, camera=None):
        tiles_x = self.canvas_width // self.tile_size + 1
        tiles_y = self.grass_height // self.tile_size + 1

        if camera:
            # 카메라 적용: 타일 그리기
            for y in range(tiles_y):
                for x in range(tiles_x):
                    world_x = x * self.tile_size + self.tile_size // 2
                    world_y = y * self.tile_size + self.tile_size // 2
                    draw_x, draw_y = camera.apply(world_x, world_y)

                    self.grass_tile.draw(
                        draw_x, draw_y,
                        self.tile_size, self.tile_size
                    )

            # 교토 이미지
            center_x, center_y = camera.apply(self.canvas_width // 2, self.canvas_height // 2)
            self.kyoten_image.draw(center_x, center_y, self.canvas_width, self.canvas_height)
        else:
            # 카메라 없으면 기존 방식
            for y in range(tiles_y):
                for x in range(tiles_x):
                    self.grass_tile.draw(
                        x * self.tile_size + self.tile_size // 2,
                        y * self.tile_size + self.tile_size // 2,
                        self.tile_size,
                        self.tile_size
                    )

            self.kyoten_image.draw(self.canvas_width // 2, self.canvas_height // 2, self.canvas_width, self.canvas_height)