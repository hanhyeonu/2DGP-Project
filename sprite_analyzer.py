"""
스프라이트 시트 분석 도구 (개선 버전)
- PNG 파일에서 개별 스프라이트의 경계를 자동으로 찾아냅니다
- 투명도(alpha channel)를 기반으로 스프라이트를 구분합니다
"""

from PIL import Image
import sys


def analyze_sprite_sheet(image_path, threshold=10, row_gap=2, frame_gap=2):
    """
    스프라이트 시트를 분석하여 각 스프라이트의 좌표를 찾습니다.

    Args:
        image_path: PNG 파일 경로
        threshold: 투명도 임계값 (0-255)
        row_gap: 행을 구분하는 최소 간격 (픽셀)
        frame_gap: 프레임을 구분하는 최소 간격 (픽셀)
    """
    try:
        img = Image.open(image_path)
        img = img.convert('RGBA')
        width, height = img.size
        pixels = img.load()

        print("=" * 80)
        print("스프라이트 시트 분석 결과 (개선 버전)")
        print("=" * 80)
        print(f"이미지 크기: {width}x{height}")
        print(f"이미지 경로: {image_path}")
        print("=" * 80)
        print()

        # 각 y 좌표에 투명하지 않은 픽셀이 있는지 체크
        rows_with_content = {}
        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]
                if a > threshold:
                    if y not in rows_with_content:
                        rows_with_content[y] = []
                    rows_with_content[y].append(x)

        if not rows_with_content:
            print("투명하지 않은 픽셀을 찾을 수 없습니다.")
            return []

        # y 좌표를 그룹화하여 행(row) 생성
        row_groups = []
        current_row = []
        prev_y = -1000

        for y in sorted(rows_with_content.keys()):
            if y - prev_y > row_gap:  # 새로운 행 시작
                if current_row:
                    row_groups.append(current_row)
                current_row = [y]
            else:
                current_row.append(y)
            prev_y = y

        if current_row:
            row_groups.append(current_row)

        # 각 행 분석
        analyzed_rows = []
        for row_idx, row_ys in enumerate(row_groups):
            row_min_y = min(row_ys)
            row_max_y = max(row_ys)
            row_height = row_max_y - row_min_y + 1

            # 이 행의 모든 x 좌표 수집
            row_x_coords = []
            for y in row_ys:
                row_x_coords.extend(rows_with_content[y])
            row_x_coords = sorted(set(row_x_coords))

            # x 좌표를 그룹화하여 프레임 생성
            frame_groups = []
            current_frame = []
            prev_x = -1000

            for x in row_x_coords:
                if x - prev_x > frame_gap:  # 새로운 프레임 시작
                    if current_frame:
                        frame_groups.append(current_frame)
                    current_frame = [x]
                else:
                    current_frame.append(x)
                prev_x = x

            if current_frame:
                frame_groups.append(current_frame)

            # 프레임 정보 수집
            frames_info = []
            for frame_xs in frame_groups:
                frame_min_x = min(frame_xs)
                frame_max_x = max(frame_xs)
                frame_width = frame_max_x - frame_min_x + 1
                frames_info.append({'x': frame_min_x, 'width': frame_width})

            # pico2d 좌표계로 변환
            pico_y = height - row_max_y - 1

            analyzed_rows.append({
                'row_idx': row_idx + 1,
                'y': pico_y,
                'height': row_height,
                'frames': frames_info
            })

        # 결과 출력
        print_analysis_results(analyzed_rows)

        return analyzed_rows

    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {image_path}")
        return []
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return []


def print_analysis_results(analyzed_rows):
    """분석 결과를 보기 좋게 출력"""

    # 기본 출력
    for row in analyzed_rows:
        print("─" * 80)
        print(f"행 {row['row_idx']}:")
        print(f"  y좌표: {row['y']} (pico2d 좌표계), height: {row['height']}")
        print(f"  프레임 개수: {len(row['frames'])}")
        print(f"  각 프레임:")
        for frame_idx, frame in enumerate(row['frames']):
            print(f"    프레임 {frame_idx}: x={frame['x']}, width={frame['width']}")
        print()

    print("=" * 80)
    print("Python Dict 형태 출력:")
    print("=" * 80)
    print()

    # Python dict 출력
    for row in analyzed_rows:
        print(f"# 행 {row['row_idx']}")
        print(f"ROW_{row['row_idx']}_COORDS = {{")
        print(f"    'y': {row['y']},")
        print(f"    'height': {row['height']},")
        print(f"    'frames': {len(row['frames'])},")

        x_coords = [frame['x'] for frame in row['frames']]
        widths = [frame['width'] for frame in row['frames']]

        print(f"    'x': {x_coords},")
        print(f"    'width': {widths}")
        print("}")
        print()

    print("=" * 80)
    print("사용 예시:")
    print("=" * 80)
    print()
    print("SPRITE_COORDS = {")
    for row in analyzed_rows:
        x_coords = [frame['x'] for frame in row['frames']]
        widths = [frame['width'] for frame in row['frames']]
        print(f"    {row['row_idx']}: {{'y': {row['y']}, 'height': {row['height']}, 'x': {x_coords}, 'width': {widths}}},")
    print("}")
    print()


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

        print("=" * 80)
        print("그리드 패턴 분석 결과")
        print("=" * 80)
        print(f"이미지 크기: {width}x{height}")
        print(f"셀 크기: {cell_width}x{cell_height}")
        print(f"그리드: {width // cell_width} x {height // cell_height}")
        print("=" * 80)
        print()

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
        print("=" * 80)
        print("코드 예시:")
        print("=" * 80)
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
    print("=" * 80)
    print("스프라이트 시트 분석 도구 (개선 버전)")
    print("=" * 80)
    print()

    if len(sys.argv) < 2:
        print("사용법:")
        print("  python sprite_analyzer.py <image_path>")
        print("  python sprite_analyzer.py <image_path> grid <width> <height>")
        print()
        print("예시:")
        print("  python sprite_analyzer.py EnemyFrog.png")
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
