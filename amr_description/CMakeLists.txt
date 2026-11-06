cmake_minimum_required(VERSION 3.8)
project(amr_description)

# C++ Standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)

find_package(ament_cmake REQUIRED)

find_package(ignition-gui6 REQUIRED)
find_package(ignition-transport11 REQUIRED)
find_package(ignition-msgs8 REQUIRED)
find_package(ignition-plugin1 REQUIRED COMPONENTS register loader)
find_package(Qt5 REQUIRED COMPONENTS Core Quick QuickControls2 Widgets)

# Gazebo GUI Click plugin
qt5_add_resources(RESOURCES src/GazeboGoalClick.qrc)
add_library(GazeboGoalClick SHARED
  src/gazebo_goal_click_plugin.cpp
  ${RESOURCES}
)

target_include_directories(GazeboGoalClick PUBLIC
  include
  ${IGNITION-GUI_INCLUDE_DIRS}
  ${IGNITION-TRANSPORT_INCLUDE_DIRS}
  ${IGNITION-MSGS_INCLUDE_DIRS}
)

target_link_libraries(GazeboGoalClick
  ignition-gui6::ignition-gui6
  ignition-transport11::ignition-transport11
  ignition-msgs8::ignition-msgs8
  ignition-plugin1::ignition-plugin1
  Qt5::Core
  Qt5::Quick
  Qt5::QuickControls2
  Qt5::Widgets
)

install(
  TARGETS GazeboGoalClick
  LIBRARY DESTINATION lib/${PROJECT_NAME}
  ARCHIVE DESTINATION lib/${PROJECT_NAME}
  RUNTIME DESTINATION bin
)

install(
  DIRECTORY urdf meshes launch worlds config
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS
    scripts/odom_tf_broadcaster.py
    scripts/generate_maze_map.py
    scripts/maze_map_markers.py
    scripts/generate_room_environment.py
    scripts/room_markers.py
    scripts/gazebo_goal_manager.py
    scripts/send_goal.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
