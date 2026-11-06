#!/usr/bin/env python3
"""Generate the room SDF world, matching 2D occupancy grid, and markers."""

import os
from pathlib import Path


# Room outer dimensions: X in [-6.0, 6.0], Y in [-5.0, 5.0]
RESOLUTION = 0.05
ORIGIN_X = -6.2
ORIGIN_Y = -5.2
WIDTH_M = 12.4
HEIGHT_M = 10.4

WALL_HEIGHT = 1.2
WALL_THICKNESS = 0.15

# Each box obstacle is defined as:
# (name, x_center, y_center, z_center, x_size, y_size, z_size, (r, g, b, a))
OBSTACLES = [
    # --- Outer Boundary Walls ---
    ('wall_north', 0.0, 5.0, WALL_HEIGHT / 2.0, 12.2, WALL_THICKNESS, WALL_HEIGHT, (0.85, 0.85, 0.82, 1.0)),
    ('wall_south', 0.0, -5.0, WALL_HEIGHT / 2.0, 12.2, WALL_THICKNESS, WALL_HEIGHT, (0.85, 0.85, 0.82, 1.0)),
    ('wall_east', 6.0, 0.0, WALL_HEIGHT / 2.0, WALL_THICKNESS, 10.0, WALL_HEIGHT, (0.85, 0.85, 0.82, 1.0)),
    ('wall_west', -6.0, 0.0, WALL_HEIGHT / 2.0, WALL_THICKNESS, 10.0, WALL_HEIGHT, (0.85, 0.85, 0.82, 1.0)),

    # --- Interior Divider Walls ---
    # North-West Office partition (wide 1.7 m doorway at x in [-2.9, -1.2])
    ('office_wall_h', -4.4, 0.8, WALL_HEIGHT / 2.0, 3.0, WALL_THICKNESS, WALL_HEIGHT, (0.8, 0.8, 0.78, 1.0)),
    ('office_wall_v', -1.2, 2.9, WALL_HEIGHT / 2.0, WALL_THICKNESS, 4.0, WALL_HEIGHT, (0.8, 0.8, 0.78, 1.0)),

    # North-East Conference Room partition (wide 1.7 m doorway at x in [1.2, 2.9])
    ('conf_wall_h', 4.4, 0.8, WALL_HEIGHT / 2.0, 3.0, WALL_THICKNESS, WALL_HEIGHT, (0.8, 0.8, 0.78, 1.0)),
    ('conf_wall_v', 1.2, 2.9, WALL_HEIGHT / 2.0, WALL_THICKNESS, 4.0, WALL_HEIGHT, (0.8, 0.8, 0.78, 1.0)),

    # South-East Lounge divider (wide 1.7 m doorway at x in [1.2, 2.9])
    ('lounge_wall_h', 4.4, -0.8, WALL_HEIGHT / 2.0, 3.0, WALL_THICKNESS, WALL_HEIGHT, (0.8, 0.8, 0.78, 1.0)),

    # South-West Storage divider (wide 1.7 m doorway at x in [-2.9, -1.2])
    ('storage_wall_h', -4.4, -0.8, WALL_HEIGHT / 2.0, 3.0, WALL_THICKNESS, WALL_HEIGHT, (0.8, 0.8, 0.78, 1.0)),

    # --- Furniture: Office (North-West) ---
    ('office_desk', -3.8, 3.2, 0.38, 1.6, 0.8, 0.76, (0.58, 0.40, 0.25, 1.0)),
    ('office_chair', -3.8, 4.1, 0.42, 0.6, 0.55, 0.84, (0.22, 0.22, 0.24, 1.0)),
    ('bookshelf_west', -5.55, 2.8, 0.75, 0.5, 1.8, 1.5, (0.45, 0.28, 0.18, 1.0)),
    ('file_cabinet', -1.9, 4.2, 0.5, 0.6, 0.6, 1.0, (0.7, 0.72, 0.75, 1.0)),

    # --- Furniture: Conference Room (North-East) ---
    ('conference_table', 3.6, 2.8, 0.38, 2.2, 1.1, 0.76, (0.50, 0.32, 0.20, 1.0)),
    ('chair_north', 3.6, 3.75, 0.42, 0.5, 0.5, 0.84, (0.22, 0.22, 0.24, 1.0)),
    ('chair_south', 3.6, 1.85, 0.42, 0.5, 0.5, 0.84, (0.22, 0.22, 0.24, 1.0)),
    ('chair_west', 2.1, 2.8, 0.42, 0.5, 0.5, 0.84, (0.22, 0.22, 0.24, 1.0)),
    ('chair_east', 5.1, 2.8, 0.42, 0.5, 0.5, 0.84, (0.22, 0.22, 0.24, 1.0)),
    ('credenza_east', 5.6, 2.8, 0.45, 0.4, 1.6, 0.9, (0.35, 0.22, 0.15, 1.0)),

    # --- Furniture: Lounge Area (South-East) ---
    ('couch_main', 3.6, -4.1, 0.42, 2.2, 0.85, 0.84, (0.18, 0.28, 0.52, 1.0)),
    ('armchair_left', 2.0, -2.8, 0.42, 0.8, 0.8, 0.84, (0.18, 0.28, 0.52, 1.0)),
    ('armchair_right', 5.1, -2.8, 0.42, 0.8, 0.8, 0.84, (0.18, 0.28, 0.52, 1.0)),
    ('coffee_table', 3.6, -2.8, 0.22, 1.2, 0.7, 0.44, (0.25, 0.25, 0.28, 1.0)),

    # --- Furniture: Storage & Workshop (South-West) ---
    ('storage_rack_west', -5.4, -3.0, 0.8, 0.6, 2.2, 1.6, (0.25, 0.28, 0.32, 1.0)),
    ('storage_rack_south', -3.4, -4.3, 0.8, 1.8, 0.6, 1.6, (0.25, 0.28, 0.32, 1.0)),
    ('workbench', -3.2, -2.4, 0.45, 1.5, 0.8, 0.9, (0.42, 0.44, 0.48, 1.0)),
]


def generate_sdf_world(dest_path: Path):
    """Generate Gazebo Fortress SDF world."""
    models_xml = []
    for name, xc, yc, zc, sx, sy, sz, (r, g, b, a) in OBSTACLES:
        models_xml.append(f"""    <model name="{name}">
      <static>true</static>
      <pose>{xc:.3f} {yc:.3f} {zc:.3f} 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry><box><size>{sx:.3f} {sy:.3f} {sz:.3f}</size></box></geometry>
        </collision>
        <visual name="visual">
          <geometry><box><size>{sx:.3f} {sy:.3f} {sz:.3f}</size></box></geometry>
          <material>
            <ambient>{r:.2f} {g:.2f} {b:.2f} {a:.2f}</ambient>
            <diffuse>{r:.2f} {g:.2f} {b:.2f} {a:.2f}</diffuse>
            <specular>0.1 0.1 0.1 1.0</specular>
          </material>
        </visual>
      </link>
    </model>""")

    # Destination Marker model (visual-only, can be moved/translated in Gazebo)
    marker_xml = """    <!-- Interactive Destination Marker (visual target beacon) -->
    <model name="destination_marker">
      <static>true</static>
      <pose>0.0 2.5 0.01 0 0 0</pose>
      <link name="marker_link">
        <visual name="ground_ring">
          <pose>0 0 0.005 0 0 0</pose>
          <geometry><cylinder><radius>0.4</radius><length>0.01</length></cylinder></geometry>
          <material>
            <ambient>0.0 0.9 0.4 0.6</ambient>
            <diffuse>0.0 0.9 0.4 0.6</diffuse>
            <emissive>0.0 0.5 0.2 0.5</emissive>
          </material>
        </visual>
        <visual name="inner_disk">
          <pose>0 0 0.01 0 0 0</pose>
          <geometry><cylinder><radius>0.2</radius><length>0.015</length></cylinder></geometry>
          <material>
            <ambient>0.1 1.0 0.5 0.8</ambient>
            <diffuse>0.1 1.0 0.5 0.8</diffuse>
            <emissive>0.1 0.8 0.4 0.8</emissive>
          </material>
        </visual>
        <visual name="flagpole">
          <pose>0 0 0.6 0 0 0</pose>
          <geometry><cylinder><radius>0.015</radius><length>1.2</length></cylinder></geometry>
          <material>
            <ambient>0.9 0.9 0.9 1.0</ambient>
            <diffuse>0.9 0.9 0.9 1.0</diffuse>
          </material>
        </visual>
        <visual name="top_sphere">
          <pose>0 0 1.2 0 0 0</pose>
          <geometry><sphere><radius>0.1</radius></sphere></geometry>
          <material>
            <ambient>0.0 1.0 0.4 1.0</ambient>
            <diffuse>0.0 1.0 0.4 1.0</diffuse>
            <emissive>0.0 0.8 0.3 1.0</emissive>
          </material>
        </visual>
      </link>
    </model>"""

    sdf_content = f"""<?xml version="1.0" ?>
<sdf version="1.8">
  <world name="nav_world">
    <physics name="1ms" type="ignored">
      <max_step_size>0.002</max_step_size>
      <real_time_factor>1.0</real_time_factor>
    </physics>

    <!-- Plugins -->
    <plugin filename="ignition-gazebo-physics-system" name="ignition::gazebo::systems::Physics"/>
    <plugin filename="ignition-gazebo-user-commands-system" name="ignition::gazebo::systems::UserCommands"/>
    <plugin filename="ignition-gazebo-scene-broadcaster-system" name="ignition::gazebo::systems::SceneBroadcaster"/>
    <plugin filename="ignition-gazebo-sensors-system" name="ignition::gazebo::systems::Sensors">
      <render_engine>ogre2</render_engine>
    </plugin>

    <!-- Lighting -->
    <light type="directional" name="sun">
      <cast_shadows>true</cast_shadows>
      <pose>0 0 10 0 0 0</pose>
      <diffuse>0.85 0.85 0.85 1</diffuse>
      <specular>0.3 0.3 0.3 1</specular>
      <direction>-0.5 0.2 -0.9</direction>
    </light>
    <light type="point" name="room_light_nw">
      <pose>-3.0 2.5 3.0 0 0 0</pose>
      <diffuse>0.5 0.5 0.5 1</diffuse>
      <attenuation><range>15</range><constant>0.5</constant><linear>0.05</linear></attenuation>
    </light>
    <light type="point" name="room_light_ne">
      <pose>3.0 2.5 3.0 0 0 0</pose>
      <diffuse>0.5 0.5 0.5 1</diffuse>
      <attenuation><range>15</range><constant>0.5</constant><linear>0.05</linear></attenuation>
    </light>
    <light type="point" name="room_light_s">
      <pose>0.0 -2.5 3.0 0 0 0</pose>
      <diffuse>0.5 0.5 0.5 1</diffuse>
      <attenuation><range>15</range><constant>0.5</constant><linear>0.05</linear></attenuation>
    </light>

    <!-- Floor Plane with warm wood/tile look -->
    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry><plane><normal>0 0 1</normal><size>100 100</size></plane></geometry>
        </collision>
        <visual name="visual">
          <geometry><plane><normal>0 0 1</normal><size>100 100</size></plane></geometry>
          <material>
            <ambient>0.75 0.73 0.70 1.0</ambient>
            <diffuse>0.75 0.73 0.70 1.0</diffuse>
          </material>
        </visual>
      </link>
    </model>

{chr(10).join(models_xml)}

{marker_xml}
  </world>
</sdf>
"""
    dest_path.write_text(sdf_content)
    print(f"Generated Gazebo world: {dest_path}")


def generate_occupancy_grid(pgm_path: Path, yaml_path: Path):
    """Generate static 2D occupancy grid matching room boundaries and obstacles."""
    width_cells = int(round(WIDTH_M / RESOLUTION))
    height_cells = int(round(HEIGHT_M / RESOLUTION))

    # Pre-fill free space (254 = free)
    grid = bytearray([254] * (width_cells * height_cells))

    # Convert obstacles to bounding boxes
    boxes = []
    for name, xc, yc, zc, sx, sy, sz, _ in OBSTACLES:
        xmin = xc - sx / 2.0
        xmax = xc + sx / 2.0
        ymin = yc - sy / 2.0
        ymax = yc + sy / 2.0
        boxes.append((xmin, xmax, ymin, ymax))

    for cy in range(height_cells):
        y = ORIGIN_Y + (cy + 0.5) * RESOLUTION
        # PGM image row 0 is topmost (maximum y)
        pgm_row = height_cells - 1 - cy
        for cx in range(width_cells):
            x = ORIGIN_X + (cx + 0.5) * RESOLUTION
            for xmin, xmax, ymin, ymax in boxes:
                if xmin <= x <= xmax and ymin <= y <= ymax:
                    grid[pgm_row * width_cells + cx] = 0  # 0 = occupied
                    break

    header = f"P5\n{width_cells} {height_cells}\n255\n".encode('ascii')
    pgm_path.write_bytes(header + grid)

    yaml_content = f"""image: {pgm_path.name}
mode: trinary
resolution: {RESOLUTION}
origin: [{ORIGIN_X:.3f}, {ORIGIN_Y:.3f}, 0.0]
negate: 0
occupied_thresh: 0.65
free_thresh: 0.25
"""
    yaml_path.write_text(yaml_content)
    print(f"Generated occupancy grid: {pgm_path} and {yaml_path} ({width_cells}x{height_cells})")


def main():
    pkg_root = Path(__file__).resolve().parents[1]
    world_path = pkg_root / 'worlds' / 'room_world.sdf'
    maps_dir = pkg_root.parent.parent / 'maps'
    maps_dir.mkdir(parents=True, exist_ok=True)

    pgm_path = maps_dir / 'room_map.pgm'
    yaml_path = maps_dir / 'room_map.yaml'

    generate_sdf_world(world_path)
    generate_occupancy_grid(pgm_path, yaml_path)
    print("Room environment generation complete!")


if __name__ == '__main__':
    main()

