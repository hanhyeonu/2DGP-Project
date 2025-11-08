from pico2d import load_image


class Background:
    def __init__(self):
        self.image = load_image('kyoten.png')
        self.canvas_width = 1024
        self.canvas_height = 1024

    def update(self):
        pass

    def draw(self):
        self.image.draw(self.canvas_width // 2, self.canvas_height // 2, self.canvas_width, self.canvas_height)