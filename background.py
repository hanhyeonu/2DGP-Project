from pico2d import load_image


class Background:
    def __init__(self):
        self.kyoten_image = load_image('kyoten.png')
        self.grass_tile = load_image('base_grass_cc.png')
        self.canvas_width = 1024
        self.canvas_height = 1024
        self.tile_size = 32

        self.grass_height = int(self.canvas_height * 0.7)

    def update(self):
        pass

    def draw(self):
        tiles_x = self.canvas_width // self.tile_size + 1
        tiles_y = self.grass_height // self.tile_size + 1

        for y in range(tiles_y):
            for x in range(tiles_x):
                self.grass_tile.draw(
                    x * self.tile_size + self.tile_size // 2,
                    y * self.tile_size + self.tile_size // 2,
                    self.tile_size,
                    self.tile_size
                )

        self.kyoten_image.draw(self.canvas_width // 2, self.canvas_height // 2, self.canvas_width, self.canvas_height)