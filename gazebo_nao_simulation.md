# Gazebo + ROS 2 Simulation Setup for Nao Humanoid Robot

Two supported ROS 2 + Gazebo combinations for simulating the Nao humanoid robot, building a custom ROS 2 package to control walking, head movement, joint activation, and command execution.

---

## Compatibility Overview

| ROS 2 Distro | Gazebo Version | Ubuntu  | Status         |
|--------------|----------------|---------|----------------|
| Humble       | Harmonic       | 22.04   | ⚡ Possible    |
| **Jazzy**    | **Harmonic**   | **24.04**| ✅ Recommended |

Per the [official compatibility table](https://gazebosim.org/docs/harmonic/ros_installation/#summary-of-compatible-ros-and-gazebo-combinations):
- **Jazzy + Harmonic** is the recommended pairing.
- **Humble + Harmonic** works but requires extra setup (Humble's default Gazebo is Fortress).

---

## Option A: ROS 2 Humble + Gazebo Harmonic (Ubuntu 22.04)

### 1. Install ROS 2 Humble
- [Official install guide](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html)

### 2. Install Gazebo Harmonic
```bash
sudo apt update
sudo apt install -y curl lsb-release gnupg
sudo curl -sSL https://packages.osrfoundation.org/gazebo.gpg \
  -o /usr/share/keyrings/gazebo-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/gazebo-archive-keyring.gpg] \
  https://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
sudo apt update
sudo apt install -y gz-harmonic
```
Verify: `gz sim` should launch the GUI.

### 3. Install ros_gz Bridge & Simulation Packages (Humble + Harmonic)

Humble officially pairs with Fortress, so Harmonic needs the community bridge from `packages.osrfoundation.org`:
```bash
sudo apt install -y ros-humble-ros-gzharmonic
```
This metapackage provides:
- [`ros-gz-bridge`](https://github.com/gazebosim/ros_gz/tree/humble/ros_gz_bridge) — bidirectional ROS 2 ↔ Gazebo Transport bridge
- [`ros-gz-sim`](https://github.com/gazebosim/ros_gz/tree/humble/ros_gz_sim) — launch files & tools to run Gazebo with ROS
- [`ros-gz-image`](https://github.com/gazebosim/ros_gz/tree/humble/ros_gz_image) — image bridge (camera → ROS)
- [`ros-gz-point-cloud`](https://github.com/gazebosim/ros_gz/tree/humble/ros_gz_point_cloud) — LiDAR point cloud bridge

Alternatively, build `ros_gz` from source against Harmonic:
```bash
# https://github.com/gazebosim/ros_gz/tree/humble
export GZ_VERSION=harmonic
# then colcon build in a workspace
```

### 4. Additional ROS 2 Packages for Simulation

```bash
sudo apt install -y \
  ros-humble-rviz2 \
  ros-humble-joint-state-publisher \
  ros-humble-joint-state-publisher-gui \
  ros-humble-robot-state-publisher \
  ros-humble-xacro \
  ros-humble-teleop-twist-keyboard \
  ros-humble-teleop-twist-joy
```

### 5. Source the environment & verify bridge
```bash
source /opt/ros/humble/setup.bash
ros2 pkg list | grep ros_gz
# Expected: ros_gz_bridge, ros_gz_sim, ros_gz_image, ros_gz_point_cloud

# Quick bridge test (clock sync)
ros2 run ros_gz_bridge parameter_bridge /clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock
```

---

## Option B: ROS 2 Jazzy + Gazebo Harmonic (Ubuntu 24.04) — Recommended

### 1. Install ROS 2 Jazzy
- [Official install guide](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html)

### 2. Install Gazebo Harmonic + ros_gz Bridge (single command)

Starting with Jazzy, Gazebo is available via ROS vendor packages:
```bash
sudo apt install -y ros-jazzy-ros-gz
```
This metapackage pulls in Gazebo Harmonic libraries and the full `ros_gz` stack:

| Package | Description | Link |
|---------|-------------|------|
| [`ros-gz-bridge`](https://github.com/gazebosim/ros_gz/tree/jazzy/ros_gz_bridge) | Bidirectional ROS 2 ↔ Gazebo Transport bridge | [README](https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_bridge/README.md) |
| [`ros-gz-sim`](https://github.com/gazebosim/ros_gz/tree/jazzy/ros_gz_sim) | Launch files & tools to run Gazebo with ROS | — |
| [`ros-gz-image`](https://github.com/gazebosim/ros_gz/tree/jazzy/ros_gz_image) | Image bridge (camera → ROS via image_transport) | — |
| [`ros-gz-point-cloud`](https://github.com/gazebosim/ros_gz/tree/jazzy/ros_gz_point_cloud) | LiDAR point cloud bridge | — |

### 3. Additional ROS 2 Packages for Simulation

```bash
sudo apt install -y \
  ros-jazzy-gz-ros-pkgs \
  ros-jazzy-gz-ros2-control \
  ros-jazzy-rviz2 \
  ros-jazzy-joint-state-publisher \
  ros-jazzy-joint-state-publisher-gui \
  ros-jazzy-robot-state-publisher \
  ros-jazzy-xacro \
  ros-jazzy-teleop-twist-keyboard \
  ros-jazzy-teleop-twist-joy
```

| Package | Purpose |
|---------|---------|
| [`gz-ros-pkgs`](https://github.com/gazebosim/gz_ros_pkgs) | ROS 2 integration extras for Gazebo |
| [`gz-ros2-control`](https://github.com/gazebosim/gz_ros2_control) | `ros2_control` hardware interface for Gazebo |
| [`rviz2`](https://github.com/ros2/rviz) | 3D visualization |
| [`joint-state-publisher`](https://github.com/ros/joint_state_publisher) | Publish joint states from GUI sliders |
| [`robot-state-publisher`](https://github.com/ros/robot_state_publisher) | Publish TF from URDF joint states |
| [`xacro`](https://github.com/ros/xacro) | Macro language for URDF |
| [`teleop-twist-keyboard`](https://github.com/ros2/teleop_twist_keyboard) | Keyboard teleop for cmd_vel |
| [`teleop-twist-joy`](https://github.com/ros2/teleop_twist_joy) | Joystick teleop for cmd_vel |

### 4. Verify Installation
```bash
source /opt/ros/jazzy/setup.bash

# Check all ros_gz packages are present
ros2 pkg list | grep ros_gz
# ros_gz_bridge, ros_gz_sim, ros_gz_image, ros_gz_sim_demos, ...

# Quick bridge test — clock sync
ros2 run ros_gz_bridge parameter_bridge /clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock

# Launch Gazebo
gz sim
```

---

## ros_gz Bridge: How to Use

The bridge translates between Gazebo Transport topics and ROS 2 topics.

Official docs:
- [`ros_gz_bridge` README](https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_bridge/README.md)
- [ROS 2 ↔ Gazebo integration tutorial](https://gazebosim.org/docs/harmonic/ros2_integration)
- [Installing Gazebo with ROS](https://gazebosim.org/docs/harmonic/ros_installation)

### Manual bridge (per-topic)
```bash
ros2 run ros_gz_bridge parameter_bridge \
  /TOPIC@ROS_MSG_TYPE@gz.msgs.GZ_MSG_TYPE
```
Direction modifiers:
- `@` — bidirectional
- `[` — Gazebo → ROS only
- `]` — ROS → Gazebo only

Examples:
```bash
# Clock sync (always needed in simulation)
ros2 run ros_gz_bridge parameter_bridge \
  /clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock

# Joint states from Gazebo to ROS
ros2 run ros_gz_bridge parameter_bridge \
  /joint_states@sensor_msgs/msg/JointState@gz.msgs.Model

# Joint trajectory commands from ROS to Gazebo
ros2 run ros_gz_bridge parameter_bridge \
  /joint_trajectory@trajectory_msgs/msg/JointTrajectory@gz.msgs.JointTrajectory \
  --ros-args -p direction:=ROS_TO_GZ
```

### Bridge via YAML config
Create `config/bridge.yaml`:
```yaml
- ros_topic_name: "clock"
  gz_topic_name: "/clock"
  ros_type_name: "rosgraph_msgs/msg/Clock"
  gz_type_name: "gz.msgs.Clock"
  direction: GZ_TO_ROS
- ros_topic_name: "joint_states"
  gz_topic_name: "/joint_states"
  ros_type_name: "sensor_msgs/msg/JointState"
  gz_type_name: "gz.msgs.Model"
  direction: GZ_TO_ROS
- ros_topic_name: "joint_trajectory"
  gz_topic_name: "/joint_trajectory"
  ros_type_name: "trajectory_msgs/msg/JointTrajectory"
  gz_type_name: "gz.msgs.JointTrajectory"
  direction: ROS_TO_GZ
- ros_topic_name: "cmd_vel"
  gz_topic_name: "/cmd_vel"
  ros_type_name: "geometry_msgs/msg/Twist"
  gz_type_name: "gz.msgs.Twist"
  direction: ROS_TO_GZ
```
Launch with:
```bash
ros2 launch ros_gz_bridge ros_gz_bridge.launch.py \
  config_file:=src/nao_control/config/bridge.yaml
```

### Nao-relevant bridged messages
| Purpose              | ROS Type                                | Gazebo Type              |
|----------------------|-----------------------------------------|--------------------------|
| Joint commands       | `trajectory_msgs/msg/JointTrajectory`   | `gz.msgs.JointTrajectory`|
| Joint states         | `sensor_msgs/msg/JointState`            | `gz.msgs.Model`          |
| Odometry / poses     | `geometry_msgs/msg/PoseStamped`         | `gz.msgs.Pose`           |
| Clock sync           | `rosgraph_msgs/msg/Clock`              | `gz.msgs.Clock`          |
| Twist velocity       | `geometry_msgs/msg/Twist`              | `gz.msgs.Twist`          |
| Camera image         | `sensor_msgs/msg/Image`                | `gz.msgs.Image`          |
| Laser scan           | `sensor_msgs/msg/LaserScan`            | `gz.msgs.LaserScan`      |
| IMU data             | `sensor_msgs/msg/Imu`                  | `gz.msgs.IMU`            |

Full message mapping table: [ros_gz_bridge README → Message types](https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_bridge/README.md#message-types-supported-by-the-bridge)

---

## Building a ROS 2 Package for Nao Control

```bash
# Create workspace
mkdir -p ~/nao_ws/src && cd ~/nao_ws/src
ros2 pkg create nao_control --build-type ament_python \
  --dependencies rclpy geometry_msgs trajectory_msgs sensor_msgs

# Build
cd ~/nao_ws
colcon build
source install/setup.bash
```

### Node ideas for `nao_control`

| Node              | Function                                                |
|-------------------|---------------------------------------------------------|
| `trajectory_bridge` | Converts ROS JointTrajectory → per-joint Gazebo commands (required) |
| `walk_controller` | Publishes `JointTrajectory` to actuate leg joints for walking gait |
| `head_controller` | Publishes joint targets for head pitch/yaw (look around) |
| `joint_commander` | Sends individual joint position commands (sit, stand, wave) |
| `sensor_monitor`  | Monitors simulation clock (no dedicated sensor topics on Fuel model) |
| `demo_sequence`   | Choreographed demo: look → wave → sit → stand |

> **For a complete step-by-step guide with all 6 nodes, bridge config, launch file, build, and run instructions, see [`instructions/nao_simulation/setup.md`](instructions/nao_simulation/setup.md).**

### Example: publish a joint trajectory command
```python
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

class JointCommander(Node):
    def __init__(self):
        super().__init__('joint_commander')
        self.pub = self.create_publisher(JointTrajectory, '/joint_trajectory', 10)

    def send_command(self, joint_names, positions, time_from_start=1.0):
        msg = JointTrajectory()
        msg.joint_names = joint_names
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start = Duration(sec=int(time_from_start),
                                         nanosec=int((time_from_start % 1) * 1e9))
        msg.points = [point]
        self.pub.publish(msg)
```

---

## Nao Robot Model in Gazebo

The Nao humanoid (by Aldebaran/SoftBank) has 25+ DOF. The easiest way to use it in Gazebo Harmonic is the **Fuel model** (no manual URDF/SDF files needed):

1. Launch Gazebo: `gz sim`
2. Click **☰ → Insert → Fuel** tab
3. Search for **"NAO with Ignition position controller"** by OpenRobotics
4. Click to place the robot in the world

The model uses **per-joint `cmd_pos` topics** (e.g. `/model/Nao/joint/HeadYaw/0/cmd_pos`) controlled via `gz.msgs.Double`. It has **no dedicated sensor topics** (no camera, IMU, laser, or odometry).

Joint commands are sent by the `trajectory_bridge.py` node, which listens for ROS `JointTrajectory` messages and publishes to each joint's Gazebo topic.

> For the complete setup, see [`instructions/nao_simulation/setup.md`](instructions/nao_simulation/setup.md).

---

## Quick Start Workflow

```bash
# Terminal 1: Gazebo + Insert Nao from Fuel
source /opt/ros/jazzy/setup.bash   # or humble
gz sim
# → GUI: Insert tab → search "Nao" → place in world

# Terminal 2: Bridge clock + trajectory bridge
source /opt/ros/jazzy/setup.bash   # or humble
source ~/nao_ws/install/setup.bash
ros2 run ros_gz_bridge parameter_bridge \
  --ros-args -p config_file:=$HOME/nao_ws/src/nao_control/config/bridge.yaml &
ros2 run nao_control trajectory_bridge

# Terminal 3: Run control node
source ~/nao_ws/install/setup.bash
ros2 run nao_control demo_sequence
```

> **For the full step-by-step guide including workspace creation, all file contents, build instructions, and troubleshooting, see [`instructions/nao_simulation/setup.md`](instructions/nao_simulation/setup.md).**

---

## Key Links

### ROS 2 Installation
- [ROS 2 Humble install (Ubuntu 22.04)](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html)
- [ROS 2 Jazzy install (Ubuntu 24.04)](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html)

### Gazebo Installation & ROS Integration
- [Gazebo Harmonic install](https://gazebosim.org/docs/harmonic/install_ubuntu)
- [Installing Gazebo with ROS (compatibility table)](https://gazebosim.org/docs/harmonic/ros_installation)
- [ROS 2 ↔ Gazebo integration tutorial](https://gazebosim.org/docs/harmonic/ros2_integration)

### ros_gz Bridge & Simulation Packages
- [`ros_gz` repo — all versions/branches](https://github.com/gazebosim/ros_gz)
- [`ros_gz_bridge` README (message mappings)](https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_bridge/README.md)
- [`ros_gz_sim` — spawn & launch tools](https://github.com/gazebosim/ros_gz/tree/jazzy/ros_gz_sim)
- [`ros_gz_image` — camera bridge](https://github.com/gazebosim/ros_gz/tree/jazzy/ros_gz_image)
- [`ros_gz_point_cloud` — LiDAR bridge](https://github.com/gazebosim/ros_gz/tree/jazzy/ros_gz_point_cloud)
- [`ros_gz` Humble branch (build from source)](https://github.com/gazebosim/ros_gz/tree/humble)

### ros2_control with Gazebo
- [`gz_ros2_control` — ros2_control hardware interface](https://github.com/gazebosim/gz_ros2_control)
- [`gz_ros_pkgs` — additional ROS integration](https://github.com/gazebosim/gz_ros_pkgs)
- [ros2_control docs](https://control.ros.org/jazzy/)

### ROS 2 Tools
- [RViz2](https://github.com/ros2/rviz)
- [Joint State Publisher](https://github.com/ros/joint_state_publisher)
- [Robot State Publisher](https://github.com/ros/robot_state_publisher)
- [Xacro](https://github.com/ros/xacro)
- [Teleop Twist Keyboard](https://github.com/ros2/teleop_twist_keyboard)
- [Teleop Twist Joy](https://github.com/ros2/teleop_twist_joy)

### Nao Humanoid Robot
- [ROS packages for Nao](https://github.com/ros-naoqi/nao_robot)
- [Pal Robotics Nao fork](https://github.com/pal-robotics/nao_robot)
- [Nao V5 description (URDF)](https://github.com/ros-naoqi/nao_robot/tree/master/nao_v5_description)
