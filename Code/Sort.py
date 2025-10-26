import random
import sys
from typing import Dict, Generator, List, Optional, Tuple

import pygame
import colorsys


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 640
BACKGROUND_COLOR = (30, 30, 32)
TEXT_COLOR = (235, 235, 235)
NUM_ITEMS = 1000


class SortStats:
    def __init__(self) -> None:
        self.comparisons: int = 0
        self.array_accesses: int = 0


def hsv_color(h: float, s: float = 1.0, v: float = 1.0) -> Tuple[int, int, int]:
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return int(r * 255), int(g * 255), int(b * 255)


def generate_random_array(n: int) -> List[int]:
    values = list(range(1, n + 1))
    random.shuffle(values)
    return values


def draw_array(
    surface: pygame.Surface,
    values: List[int],
    stats: SortStats,
    highlight: Optional[Dict[str, int]] = None,
    title: str = "Quick Sort",
) -> None:
    surface.fill(BACKGROUND_COLOR)

    n = len(values)
    plot_margin = 8
    usable_width = WINDOW_WIDTH - plot_margin * 2
    usable_height = WINDOW_HEIGHT - plot_margin * 2
    bar_width = max(1, usable_width // n)

    # Base gradient color by value so最終的に滑らかな坂とグラデーションになる
    for i, v in enumerate(values):
        x = plot_margin + i * bar_width
        bar_h = int((v / n) * (usable_height - 40))  # 40 はヘッダ余白
        y = WINDOW_HEIGHT - plot_margin - bar_h

        hue = v / n
        color = hsv_color(hue, 1.0, 1.0)

        # ハイライト上書き
        if highlight:
            if i == highlight.get("pivot", -1):
                color = (255, 80, 80)  # pivot: red
            elif i == highlight.get("i", -1):
                color = (80, 220, 120)  # i: green
            elif i == highlight.get("j", -1):
                color = (255, 220, 100)  # j: yellow
            elif i in (
                highlight.get("swap_a", -2),
                highlight.get("swap_b", -3),
            ):
                color = (150, 200, 255)  # swapping: light blue

        pygame.draw.rect(surface, color, (x, y, bar_width, bar_h))

    # タイトル・統計の描画
    font = pygame.font.SysFont("consolas,monospace", 18)
    title_surf = font.render(title, True, TEXT_COLOR)
    stats_surf = font.render(
        f"Comparisons: {stats.comparisons:,}  Array Accesses: {stats.array_accesses:,}",
        True,
        TEXT_COLOR,
    )
    surface.blit(title_surf, (10, 8))
    surface.blit(stats_surf, (10, 28))


def quick_sort_steps(values: List[int], stats: SortStats) -> Generator[Dict[str, int], None, None]:
    # 非再帰（スタック）実装で可視化用に頻繁に yield
    stack: List[Tuple[int, int]] = [(0, len(values) - 1)]

    def partition(low: int, high: int) -> Generator[Tuple[int, Dict[str, int]], None, None]:
        pivot_index = high
        pivot_value = values[pivot_index]
        stats.array_accesses += 1  # pivot 読み
        i = low - 1
        highlight = {"pivot": pivot_index}
        yield -1, highlight  # 初期ピボット表示

        for j in range(low, high):
            highlight = {"pivot": pivot_index, "j": j, "i": i}
            stats.comparisons += 1
            stats.array_accesses += 1  # values[j] 読み
            yield -1, highlight
            if values[j] <= pivot_value:
                i += 1
                if i != j:
                    values[i], values[j] = values[j], values[i]
                    stats.array_accesses += 4  # 2 読み 2 書き（概算）
                    yield -1, {
                        "pivot": pivot_index,
                        "swap_a": i,
                        "swap_b": j,
                        "i": i,
                        "j": j,
                    }
        # pivot を正しい位置へ
        if i + 1 != pivot_index:
            values[i + 1], values[pivot_index] = values[pivot_index], values[i + 1]
            stats.array_accesses += 4
            yield -1, {"swap_a": i + 1, "swap_b": pivot_index, "pivot": pivot_index}
        yield i + 1, {"pivot": i + 1}

    while stack:
        low, high = stack.pop()
        if low >= high:
            continue
        # partition をステップ実行
        part_gen = partition(low, high)
        pivot_final = None
        for pivot_final, hl in part_gen:
            yield hl
        assert pivot_final is not None

        p = pivot_final
        # 右側を先、左側を後に積むと見た目が安定
        if p + 1 < high:
            stack.append((p + 1, high))
        if low < p - 1:
            stack.append((low, p - 1))


def bubble_sort_steps(values: List[int], stats: SortStats) -> Generator[Dict[str, int], None, None]:
    n = len(values)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            stats.comparisons += 1
            stats.array_accesses += 2
            yield {"i": j, "j": j + 1}
            if values[j] > values[j + 1]:
                values[j], values[j + 1] = values[j + 1], values[j]
                stats.array_accesses += 4
                swapped = True
                yield {"swap_a": j, "swap_b": j + 1}
        if not swapped:
            break


def insertion_sort_steps(values: List[int], stats: SortStats) -> Generator[Dict[str, int], None, None]:
    n = len(values)
    for i in range(1, n):
        key = values[i]
        stats.array_accesses += 1
        j = i - 1
        yield {"i": i}
        while j >= 0:
            stats.comparisons += 1
            stats.array_accesses += 1
            yield {"i": i, "j": j}
            if values[j] > key:
                values[j + 1] = values[j]
                stats.array_accesses += 2
                yield {"swap_a": j, "swap_b": j + 1}
                j -= 1
            else:
                break
        values[j + 1] = key
        stats.array_accesses += 1
        yield {"i": j + 1}


def selection_sort_steps(values: List[int], stats: SortStats) -> Generator[Dict[str, int], None, None]:
    n = len(values)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            stats.comparisons += 1
            stats.array_accesses += 2
            yield {"i": min_idx, "j": j}
            if values[j] < values[min_idx]:
                min_idx = j
                yield {"i": min_idx}
        if min_idx != i:
            values[i], values[min_idx] = values[min_idx], values[i]
            stats.array_accesses += 4
            yield {"swap_a": i, "swap_b": min_idx}


def heap_sort_steps(values: List[int], stats: SortStats) -> Generator[Dict[str, int], None, None]:
    n = len(values)

    def heapify(end: int, i: int) -> Generator[None, None, None]:
        while True:
            left = 2 * i + 1
            right = 2 * i + 2
            largest = i
            if left < end:
                stats.comparisons += 1
                stats.array_accesses += 2
                yield {"i": i, "j": left}
                if values[left] > values[largest]:
                    largest = left
            if right < end:
                stats.comparisons += 1
                stats.array_accesses += 2
                yield {"i": largest, "j": right}
                if values[right] > values[largest]:
                    largest = right
            if largest != i:
                values[i], values[largest] = values[largest], values[i]
                stats.array_accesses += 4
                yield {"swap_a": i, "swap_b": largest}
                i = largest
            else:
                return

    # build max heap
    for i in range(n // 2 - 1, -1, -1):
        for _ in heapify(n, i):
            yield {}

    # extract elements
    for end in range(n - 1, 0, -1):
        values[0], values[end] = values[end], values[0]
        stats.array_accesses += 4
        yield {"swap_a": 0, "swap_b": end}
        for _ in heapify(end, 0):
            yield {}


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Sorting Visualizer")
    surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    values = generate_random_array(NUM_ITEMS)
    stats = SortStats()
    steps_per_frame = 50  # 1 フレーム当たりのステップ数（速度）

    AlgorithmFactory = Tuple[str, callable]
    algorithms: List[AlgorithmFactory] = [
        ("Quick Sort", quick_sort_steps),
        ("Heap Sort", heap_sort_steps),
        ("Bubble Sort", bubble_sort_steps),
        ("Insertion Sort", insertion_sort_steps),
        ("Selection Sort", selection_sort_steps),
    ]

    current_algo_idx = 0
    algo_name, algo_fn = algorithms[current_algo_idx]
    sorter = algo_fn(values, stats)
    sorting = True
    highlight: Optional[Dict[str, int]] = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    # 乱数列を再生成して再開
                    values = generate_random_array(NUM_ITEMS)
                    stats = SortStats()
                    algo_name, algo_fn = algorithms[current_algo_idx]
                    sorter = algo_fn(values, stats)
                    sorting = True
                elif event.key == pygame.K_p:
                    # 一時停止/再開
                    sorting = not sorting
                elif event.key == pygame.K_SPACE:
                    # アルゴリズム切替
                    current_algo_idx = (current_algo_idx + 1) % len(algorithms)
                    values = generate_random_array(NUM_ITEMS)
                    stats = SortStats()
                    algo_name, algo_fn = algorithms[current_algo_idx]
                    sorter = algo_fn(values, stats)
                    sorting = True
                elif event.key in (pygame.K_UP, pygame.K_RIGHT):
                    steps_per_frame = min(steps_per_frame + 1, 100)
                elif event.key in (pygame.K_DOWN, pygame.K_LEFT):
                    steps_per_frame = max(1, steps_per_frame - 1)

        if sorting:
            for _ in range(steps_per_frame):
                try:
                    highlight = next(sorter)
                except StopIteration:
                    sorting = False
                    highlight = None
                    break

        draw_array(surface, values, stats, highlight, title=algo_name)
        # 右上に速度表示
        font = pygame.font.SysFont("consolas,monospace", 16)
        speed_text = font.render(
            f"Speed: {steps_per_frame} steps/frame  [Space] Algo  [P] Pause  [R] Reset",
            True,
            TEXT_COLOR,
        )
        surface.blit(speed_text, (WINDOW_WIDTH - speed_text.get_width() - 10, 8))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()


