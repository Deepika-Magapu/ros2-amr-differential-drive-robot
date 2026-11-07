# Design and Simulation of a Differential Drive Autonomous Mobile Robot using ROS 2

## 1. Project Overview

This project focuses on the mechanical design, robot modelling and simulation of a Differential Drive Autonomous Mobile Robot (AMR) using SolidWorks and ROS 2.

The mechanical structure of the robot was designed using SolidWorks, including the chassis, drive wheels, caster wheel and sensor mounting components. The mechanical design was then used as a reference for developing the robot description using URDF and integrating it into the ROS 2 simulation environment.

The project explores the integration of mechanical design, robot modelling, differential-drive motion, LiDAR-based perception, environment mapping and autonomous navigation.

## 2. Project Objectives

- Design a differential-drive mobile robot using SolidWorks.
- Develop a 3D mechanical model and assembly.
- Create a robot description using URDF.
- Simulate robot movement using Gazebo Fortress.
- Integrate LiDAR for environmental perception.
- Visualize the robot and sensor data using RViz2.
- Implement environment mapping using SLAM Toolbox.
- Explore autonomous navigation using Nav2.

## 3. Mechanical Design using SolidWorks

The mechanical design of the AMR was developed using SolidWorks.

The design consists of the main robot chassis, differential-drive wheels, caster wheel and sensor mounting components.

### Design Activities

- 3D modelling of the robot chassis.
- Design of differential-drive wheels.
- Modelling of the caster wheel.
- Design of sensor mounting components.
- Assembly of individual mechanical components.
- Export of the complete assembly into STEP format.

### CAD Files Included

The `solidworks_design` directory contains:

| File | Description |
|---|---|
| OMRON.SLDASM | Complete SolidWorks assembly |
| CHASSIS.SLDPRT | Robot chassis |
| WHEEL.SLDPRT | Drive wheel |
| CASTER WHEEL.SLDPRT | Caster wheel |
| LIDAR.SLDPRT | LiDAR component |
| LOW LASER.SLDPRT | Low laser component |
| OMRON.STEP | Complete assembly exported in STEP format |

The native SolidWorks files are provided for accessing the original mechanical design, while the STEP file supports interoperability with other CAD applications.

## 4. ROS 2 Robot Modelling and Simulation

The robot description is developed using URDF and integrated into ROS 2.

Gazebo Fortress is used as the simulation environment, while RViz2 provides visualization of the robot model, coordinate frames and sensor data.

### Main Components

- **URDF:** Defines the robot structure, links and joints.
- **Gazebo Fortress:** Provides the robot simulation environment.
- **Differential Drive:** Enables forward, turning and rotational motion.
- **LiDAR:** Provides environmental distance measurements.
- **RViz2:** Visualizes the robot and sensor information.
- **SLAM Toolbox:** Supports environment mapping.
- **Nav2:** Provides the framework for autonomous navigation.

## 5. Technologies and Tools Used

| Technology | Purpose |
|---|---|
| SolidWorks | Mechanical design and 3D modelling |
| Ubuntu 22.04 | Operating system |
| ROS 2 Humble | Robot software framework |
| Gazebo Fortress | Robot simulation |
| RViz2 | Robot and sensor visualization |
| URDF | Robot description |
| SLAM Toolbox | Environment mapping |
| Nav2 | Autonomous navigation |
| Python / C++ | ROS 2 development |

## 6. Repository Structure

```text
ros2-amr-differential-drive-robot/
│
├── amr_description/
│   ├── config/
│   ├── include/
│   ├── launch/
│   ├── meshes/
│   ├── rviz/
│   ├── scripts/
│   ├── src/
│   ├── urdf/
│   ├── worlds/
│   ├── CMakeLists.txt
│   └── package.xml
│
├── m-explore-ros2/
│   ├── explore/
│   ├── explore_lite_msgs/
│   └── map_merge/
│
├── maps/
│
├── rviz/
│
├── solidworks_design/
│   ├── native_files/
│   │   ├── OMRON.SLDASM
│   │   ├── CHASSIS.SLDPRT
│   │   ├── WHEEL.SLDPRT
│   │   ├── CASTER WHEEL.SLDPRT
│   │   ├── LIDAR.SLDPRT
│   │   └── LOW LASER.SLDPRT
│   │
│   └── exports/
│       └── OMRON.STEP
│
├── README.md
└── .gitignore
```

## 7. Software Requirements

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Fortress
- RViz2
- SLAM Toolbox
- Navigation2
- Colcon build tools

Additional ROS 2 dependencies may be required depending on the selected launch configurations.

## 8. Building the ROS 2 Workspace

### Step 1: Create a ROS 2 workspace

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
```

### Step 2: Clone the repository

```bash
git clone https://github.com/Deepika-Magapu/ros2-amr-differential-drive-robot.git
```

### Step 3: Install dependencies

```bash
cd ~/ros2_ws

source /opt/ros/humble/setup.bash

rosdep install --from-paths src --ignore-src -r -y
```

### Step 4: Build the workspace

```bash
colcon build --symlink-install
```

### Step 5: Source the workspace

```bash
source install/setup.bash
```

The ROS 2 workspace is now ready to use.

## 9. Simulation and Autonomous Navigation

The repository includes the robot description files, launch configurations, Gazebo simulation resources, RViz configurations, saved maps and navigation-related packages required to simulate and test the Autonomous Mobile Robot (AMR).

The project supports the following functionalities:

1. **Robot Model Visualization:** Visualizing the differential-drive AMR model in Gazebo and RViz.
2. **Differential-Drive Motion:** Simulating forward, reverse, turning and rotational movements.
3. **Sensor Integration:** Integrating and visualizing sensor data, including LiDAR scans.
4. **Environment Mapping:** Generating environment maps using SLAM Toolbox.
5. **Saved-Map Navigation:** Loading previously generated maps for autonomous navigation.
6. **Autonomous Navigation:** Using the ROS 2 Navigation Stack (Nav2) for goal-directed robot movement and obstacle avoidance.

### Launching the Simulation

Open three separate terminals and execute the following commands in the same order.

**Terminal 1: Launch Gazebo Simulation**

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_LOCALHOST_ONLY=1

ros2 launch amr_description gazebo.launch.py
```

**Terminal 2: Launch Saved-Map Navigation Stack**

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_LOCALHOST_ONLY=1

ros2 launch amr_description saved_map_nav_stack.launch.py
```

**Terminal 3: Launch RViz Navigation Interface**

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_LOCALHOST_ONLY=1

ros2 launch amr_description rviz_navigation.launch.py
```

Once all three components are running, the robot can be observed in the Gazebo environment and its navigation information can be monitored through RViz.

**Note:** The above launch sequence uses the saved-map navigation configuration. The repository also contains separate launch files for mapping and other simulation configurations. Refer to the `amr_description/launch` directory for the available launch files.

## 10. Future Improvements

- Improve mechanical design and simulation accuracy.
- Enhance autonomous navigation performance.
- Improve obstacle detection and avoidance.
- Integrate additional sensors.
- Expand testing across different environments.
- Further integrate mechanical design with simulation.

## 11. Project Information

**Project Domain:** Robotics and Automation  
**Robot Type:** Differential Drive Autonomous Mobile Robot  
**Mechanical Design:** SolidWorks  
**Operating System:** Ubuntu 22.04  
**Robotics Framework:** ROS 2 Humble  
**Simulation Environment:** Gazebo Fortress  

---

Developed as part of a Robotics and Automation engineering project.
