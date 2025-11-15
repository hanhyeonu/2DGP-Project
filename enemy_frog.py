from pico2d import load_image, draw_rectangle
import game_framework
from state_machine import StateMachine

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION


class Idle:
    # sprite_analyzer.py 분석 결과 - Idle 애니메이션 좌표
    SPRITE_COORDS = {
        1: {  # 오른쪽 - 1번째 줄
            'y': 224,
            'height': 16,
            'frames': [
                {'x': 1, 'width': 29},
                {'x': 33, 'width': 29},
                {'x': 65, 'width': 31}
            ]
        },
        0: {  # 아래 - 2번째 줄
            'y': 193,
            'height': 21,
            'frames': [
                {'x': 5, 'width': 22},
                {'x': 37, 'width': 22},
                {'x': 69, 'width': 22}
            ]
        },
        -1: {  # 왼쪽 - 3번째 줄
            'y': 162,
            'height': 27,
            'frames': [
                {'x': 5, 'width': 22},
                {'x': 37, 'width': 22},
                {'x': 69, 'width': 22}
            ]
        },
        4: {  # 위 - 4번째 줄
            'y': 96,
            'height': 57,
            'frames': [
                {'x': 1, 'width': 29},
                {'x': 33, 'width': 29},
                {'x': 69, 'width': 86}
            ]
        }
    }

    def __init__(self, frog):
        self.frog = frog

    def enter(self, e):
        pass

    def exit(self, e):
        pass

    def do(self):
        # 3프레임 애니메이션
        self.frog.frame = (self.frog.frame + 3 * ACTION_PER_TIME * game_framework.frame_time) % 3

    def draw(self):
        if self.frog.face_dir in self.SPRITE_COORDS:
            coords = self.SPRITE_COORDS[self.frog.face_dir]
            frame = int(self.frog.frame)

            if frame < len(coords['frames']):
                frame_data = coords['frames'][frame]
                x = frame_data['x']
                y = coords['y']
                width = frame_data['width']
                height = coords['height']

                self.frog.image.clip_composite_draw(
                    x, y,
                    width, height,
                    0, '',
                    self.frog.x, self.frog.y,
                    width, height
                )


class EnemyFrog:
    def __init__(self):
        self.x, self.y = 500, 500
        self.frame = 0
        self.face_dir = 1
        self.image = load_image('EnemyFrog.png')

        self.IDLE = Idle(self)
        self.state_machine = StateMachine(self.IDLE, {})

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        # 스프라이트 크기의 약 70% 정도로 바운딩 박스 설정
        # 평균 크기를 30x30 정도로 가정
        w, h = 20, 20
        return self.x - w/2, self.y - h/2, self.x + w/2, self.y + h/2

    def handle_collision(self, group, other):
        pass
