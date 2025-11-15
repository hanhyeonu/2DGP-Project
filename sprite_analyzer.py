"""
스프라이트 시트 분석 도구
- PNG 파일에서 개별 스프라이트의 경계를 자동으로 찾아냅니다
- 투명도(alpha channel)를 기반으로 스프라이트를 구분합니다
"""

from PIL import Image
import sys

def analyze_sprite_sheet(image_path, threshold=10):
    """
    스프라이트 시트를 분석하여 각 스프라이트의 좌표를 찾습니다.

    Args:
        image_path: PNG 파일 경로
        threshold: 투명도 임계값 (0-255)
    """
    try:
        img = Image.open(image_path)
        img = img.convert('RGBA')
        width, height = img.size
        pixels = img.load()

        print(f"이미지 크기: {width}x{height}")
        print(f"이미지 경로: {image_path}")
        print("-" * 60)

        # 투명하지 않은 픽셀 찾기
        non_transparent_pixels = []
        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]
                if a > threshold:  # 알파값이 임계값보다 크면 투명하지 않음
                    non_transparent_pixels.append((x, y))

        if not non_transparent_pixels:
            print("투명하지 않은 픽셀을 찾을 수 없습니다.")
            return

        # 전체 스프라이트 영역의 경계 찾기
        min_x = min(p[0] for p in non_transparent_pixels)
        max_x = max(p[0] for p in non_transparent_pixels)
        min_y = min(p[1] for p in non_transparent_pixels)
        max_y = max(p[1] for p in non_transparent_pixels)

        print("전체 스프라이트 영역:")
        print(f"  X: {min_x} ~ {max_x} (width: {max_x - min_x + 1})")
        print(f"  Y: {min_y} ~ {max_y} (height: {max_y - min_y + 1})")
        print()

        # 행 단위로 스프라이트 찾기
        print("행별 스프라이트 분석:")
        rows = {}
        for x, y in non_transparent_pixels:
            if y not in rows:
                rows[y] = []
            rows[y].append(x)

        # 연속된 y 좌표를 그룹화 (같은 행)
        row_groups = []
        current_group = []
        prev_y = -1000

        for y in sorted(rows.keys()):
            if y - prev_y > 1:  # 새로운 행 시작
                if current_group:
                    row_groups.append(current_group)
                current_group = [y]
            else:
                current_group.append(y)
            prev_y = y

        if current_group:
            row_groups.append(current_group)

        print(f"발견된 행 개수: {len(row_groups)}")
        print()

        # 각 행의 스프라이트 분석
        for i, row_ys in enumerate(row_groups):
            row_min_y = min(row_ys)
            row_max_y = max(row_ys)
            row_height = row_max_y - row_min_y + 1

            # 이 행의 모든 x 좌표 수집
            row_x_coords = []
            for y in row_ys:
                row_x_coords.extend(rows[y])

            # x 좌표 기준으로 스프라이트 구분
            row_x_coords = sorted(set(row_x_coords))

            # 연속된 x 좌표를 그룹화 (같은 스프라이트)
            sprite_groups = []
            current_sprite = []
            prev_x = -1000

            for x in row_x_coords:
                if x - prev_x > 1:  # 새로운 스프라이트 시작
                    if current_sprite:
                        sprite_groups.append(current_sprite)
                    current_sprite = [x]
                else:
                    current_sprite.append(x)
                prev_x = x

            if current_sprite:
                sprite_groups.append(current_sprite)

            print(f"행 {i + 1}:")
            print(f"  Y 범위: {row_min_y} ~ {row_max_y} (height: {row_height})")
            print(f"  스프라이트 개수: {len(sprite_groups)}")

            for j, sprite_xs in enumerate(sprite_groups):
                sprite_min_x = min(sprite_xs)
                sprite_max_x = max(sprite_xs)
                sprite_width = sprite_max_x - sprite_min_x + 1

                print(f"    스프라이트 {j + 1}: x={sprite_min_x}, y={row_min_y}, width={sprite_width}, height={row_height}")

                # pico2d clip_composite_draw 좌표계로 변환 (bottom-left origin)
                pico_y = height - row_max_y - 1
                print(f"      pico2d 좌표: x={sprite_min_x}, y={pico_y}, w={sprite_width}, h={row_height}")

            print()

        # 규칙적인 패턴 감지
        print("-" * 60)
        print("규칙적인 패턴 분석:")
        detect_regular_pattern(row_groups, rows, width, height)

    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {image_path}")
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()


def detect_regular_pattern(row_groups, rows, img_width, img_height):
    """
    규칙적으로 배치된 스프라이트 패턴을 감지합니다.
    """
    if not row_groups:
        return

    # 첫 번째 행의 스프라이트 분석
    first_row_ys = row_groups[0]
    row_height = max(first_row_ys) - min(first_row_ys) + 1

    row_x_coords = []
    for y in first_row_ys:
        row_x_coords.extend(rows[y])
    row_x_coords = sorted(set(row_x_coords))

    # 연속된 x 좌표를 그룹화
    sprite_groups = []
    current_sprite = []
    prev_x = -1000

    for x in row_x_coords:
        if x - prev_x > 1:
            if current_sprite:
                sprite_groups.append(current_sprite)
            current_sprite = [x]
        else:
            current_sprite.append(x)
        prev_x = x

    if current_sprite:
        sprite_groups.append(current_sprite)

    if len(sprite_groups) > 1:
        # 스프라이트 너비 확인
        widths = [max(g) - min(g) + 1 for g in sprite_groups]
        sprite_width = widths[0]

        # 모든 스프라이트가 같은 너비인지 확인
        if all(w == sprite_width for w in widths):
            # 간격 계산
            starts = [min(g) for g in sprite_groups]
            if len(starts) > 1:
                gap = starts[1] - starts[0]

                print(f"규칙적인 패턴 감지됨!")
                print(f"  스프라이트 크기: {sprite_width}x{row_height}")
                print(f"  스프라이트 간격: {gap} (sprite_width + padding)")
                print(f"  시작 X 좌표: {starts[0]}")
                print(f"  행당 스프라이트 개수: {len(sprite_groups)}")
                print()
                print("코드 예시:")
                print(f"# 규칙적인 패턴의 경우")
                print(f"frame_width = {sprite_width}")
                print(f"frame_height = {row_height}")
                print(f"frames_per_row = {len(sprite_groups)}")
                print(f"frame_x = frame * {gap}")
                print(f"frame_y = row * {row_height}")
                print()
                print("# clip_composite_draw 사용 예시:")
                print(f"image.clip_composite_draw(")
                print(f"    frame * {gap}, # x (left)")
                print(f"    frame_y,       # y (bottom)")
                print(f"    {sprite_width}, # width")
                print(f"    {row_height},  # height")
                print(f"    0, '',         # angle, flip")
                print(f"    screen_x, screen_y, # 화면 좌표")
                print(f"    {sprite_width}, {row_height}  # 출력 크기")
                print(f")")
                return

    print("불규칙한 패턴입니다. 수동으로 좌표를 지정해야 합니다.")


def analyze_grid_pattern(image_path, cell_width, cell_height):
    """
    균일한 그리드 패턴으로 배치된 스프라이트 시트를 분석합니다.

    Args:
        image_path: PNG 파일 경로
        cell_width: 각 셀의 너비
        cell_height: 각 셀의 높이
    """
    try:
        img = Image.open(image_path)
        img = img.convert('RGBA')
        width, height = img.size

        print(f"이미지 크기: {width}x{height}")
        print(f"셀 크기: {cell_width}x{cell_height}")
        print(f"그리드: {width // cell_width} x {height // cell_height}")
        print("-" * 60)

        rows = height // cell_height
        cols = width // cell_width

        print(f"총 {rows * cols}개의 스프라이트 감지됨")
        print()

        for row in range(rows):
            for col in range(cols):
                x = col * cell_width
                y = row * cell_height

                # pico2d 좌표계로 변환
                pico_y = height - y - cell_height

                print(f"[{row},{col}] x={x}, y={pico_y}, w={cell_width}, h={cell_height}")

        print()
        print("코드 예시:")
        print(f"frame_width = {cell_width}")
        print(f"frame_height = {cell_height}")
        print(f"cols = {cols}")
        print(f"# frame 번호로 좌표 계산:")
        print(f"frame_x = (frame % {cols}) * {cell_width}")
        print(f"frame_y = {height} - ((frame // {cols}) * {cell_height}) - {cell_height}")

    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("스프라이트 시트 분석 도구")
    print("=" * 60)
    print()

    if len(sys.argv) < 2:
        print("사용법:")
        print("  python sprite_analyzer.py <image_path>")
        print("  python sprite_analyzer.py <image_path> grid <width> <height>")
        print()
        print("예시:")
        print("  python sprite_analyzer.py player.png")
        print("  python sprite_analyzer.py Slash00.png grid 32 96")
        sys.exit(1)

    image_path = sys.argv[1]

    if len(sys.argv) >= 5 and sys.argv[2] == 'grid':
        # 그리드 모드
        cell_width = int(sys.argv[3])
        cell_height = int(sys.argv[4])
        analyze_grid_pattern(image_path, cell_width, cell_height)
    else:
        # 자동 분석 모드
        analyze_sprite_sheet(image_path)
