#!/usr/bin/env python3
"""Generate the static occupancy map matching worlds/maze_world.sdf."""

from pathlib import Path


RESOLUTION = 0.05
MIN_COORD = -6.0
MAX_COORD = 6.0
WALLS = [
    # Outer walls: (x_min, x_max, y_min, y_max)
    (-6.1, 6.1, 5.9, 6.1),
    (-6.1, 6.1, -6.1, -5.9),
    (5.9, 6.1, -6.0, 6.0),
    (-6.1, -5.9, -6.0, 6.0),
    # Interior walls have alternating 3.9 m openings at opposite ends.
    (-5.9, 2.0, -2.575, -2.425),
    (-2.0, 5.9, 0.425, 0.575),
    (-5.9, 2.0, 3.425, 3.575),
]


def main():
    output_dir = Path(__file__).resolve().parents[3] / 'maps'
    output_dir.mkdir(parents=True, exist_ok=True)
    width = round((MAX_COORD - MIN_COORD) / RESOLUTION)
    height = width

    # PGM row zero is the top of the image, corresponding to maximum map y.
    pixels = bytearray([254] * (width * height))
    for map_y_index in range(height):
        y = MIN_COORD + (map_y_index + 0.5) * RESOLUTION
        pgm_row = height - 1 - map_y_index
        for x_index in range(width):
            x = MIN_COORD + (x_index + 0.5) * RESOLUTION
            if any(x0 <= x <= x1 and y0 <= y <= y1 for x0, x1, y0, y1 in WALLS):
                pixels[pgm_row * width + x_index] = 0

    (output_dir / 'maze_map.pgm').write_bytes(
        f'P5\n{width} {height}\n255\n'.encode('ascii') + pixels
    )
    (output_dir / 'maze_map.yaml').write_text(
        'image: maze_map.pgm\n'
        f'resolution: {RESOLUTION}\n'
        f'origin: [{MIN_COORD}, {MIN_COORD}, 0.0]\n'
        'negate: 0\n'
        'occupied_thresh: 0.65\n'
        'free_thresh: 0.25\n'
        'mode: trinary\n'
    )
    print(f'Wrote {output_dir / "maze_map.yaml"} ({width}x{height}, {RESOLUTION} m/cell)')


if __name__ == '__main__':
    main()
