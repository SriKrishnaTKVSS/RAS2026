# ROS 2 Jazzy + Gazebo Harmonic — Simulation Setup

**Target:** Ubuntu 24.04  
**Status:** ✅ Recommended (official pairing)

---

## 1. Install ROS 2 Jazzy

[Official install guide](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html)

```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository universe
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
  http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
sudo apt update
sudo apt install -y ros-jazzy-desktop python3-colcon-common-extensions
```

---

## 2. Install Gazebo Harmonic + ros_gz Bridge

Starting with Jazzy, Gazebo is available via ROS vendor packages — one command installs everything:

```bash
sudo apt install -y ros-jazzy-ros-gz
```

This metapackage provides:

| Package | Link |
|---------|------|
| [`ros_gz_bridge`](https://github.com/gazebosim/ros_gz/tree/jazzy/ros_gz_bridge) | [README](https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_bridge/README.md) |
| [`ros_gz_sim`](https://github.com/gazebosim/ros_gz/tree/jazzy/ros_gz_sim) | Spawn robots, launch Gazebo with ROS |
| [`ros_gz_image`](https://github.com/gazebosim/ros_gz/tree/jazzy/ros_gz_image) | Camera image bridge |
| [`ros_gz_point_cloud`](https://github.com/gazebosim/ros_gz/tree/jazzy/ros_gz_point_cloud) | LiDAR point cloud bridge |

---

## 3. Install Additional ROS 2 Packages

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

---

## 4. Source & Verify

```bash
source /opt/ros/jazzy/setup.bash

ros2 pkg list | grep ros_gz
# ros_gz_bridge, ros_gz_sim, ros_gz_image, ros_gz_sim_demos, ...

# Test bridge — clock sync
ros2 run ros_gz_bridge parameter_bridge /clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock

# Launch Gazebo
gz sim
```

---

## 5. ros_gz Bridge — Usage

### Manual per-topic
```bash
ros2 run ros_gz_bridge parameter_bridge \
  /TOPIC@ROS_MSG_TYPE@gz.msgs.GZ_MSG_TYPE
```
Direction: `@` bidirectional, `[` Gazebo→ROS, `]` ROS→Gazebo

Examples:
```bash
# Clock sync
ros2 run ros_gz_bridge parameter_bridge \
  /clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock

# Joint states
ros2 run ros_gz_bridge parameter_bridge \
  /joint_states@sensor_msgs/msg/JointState@gz.msgs.Model

# Joint commands
ros2 run ros_gz_bridge parameter_bridge \
  /joint_trajectory@trajectory_msgs/msg/JointTrajectory@gz.msgs.JointTrajectory \
  --ros-args -p direction:=ROS_TO_GZ
```

### Via YAML config
`config/bridge.yaml`:
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
```bash
ros2 launch ros_gz_bridge ros_gz_bridge.launch.py \
  config_file:=src/nao_control/config/bridge.yaml
```

### Nao-relevant message mappings

| Purpose | ROS Type | Gazebo Type |
|---------|----------|-------------|
| Joint commands | `trajectory_msgs/msg/JointTrajectory` | `gz.msgs.JointTrajectory` |
| Joint states | `sensor_msgs/msg/JointState` | `gz.msgs.Model` |
| Odometry / poses | `geometry_msgs/msg/PoseStamped` | `gz.msgs.Pose` |
| Clock sync | `rosgraph_msgs/msg/Clock` | `gz.msgs.Clock` |
| Twist velocity | `geometry_msgs/msg/Twist` | `gz.msgs.Twist` |
| Camera image | `sensor_msgs/msg/Image` | `gz.msgs.Image` |
| Laser scan | `sensor_msgs/msg/LaserScan` | `gz.msgs.LaserScan` |
| IMU data | `sensor_msgs/msg/Imu` | `gz.msgs.IMU` |

Full table: [ros_gz_bridge README](https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_bridge/README.md#message-types-supported-by-the-bridge)

---

## 6. Build a ROS 2 Package for Nao Control

```bash
mkdir -p ~/nao_ws/src && cd ~/nao_ws/src
ros2 pkg create nao_control --build-type ament_python \
  --dependencies rclpy geometry_msgs trajectory_msgs sensor_msgs
cd ~/nao_ws
colcon build
source install/setup.bash
```

### Node design

| Node | Function |
|------|----------|
| `walk_controller` | Publish `JointTrajectory` for walking gait |
| `head_controller` | Head pitch/yaw targets (look around) |
| `joint_activator` | Individual joint position/effort commands |
| `command_server` | ROS 2 action/service server for high-level commands |

### Example: JointTrajectory publisher

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
        point.time_from_start = Duration(
            sec=int(time_from_start),
            nanosec=int((time_from_start % 1) * 1e9))
        msg.points = [point]
        self.pub.publish(msg)
```

---

## 7. Nao Robot in Gazebo

Nao has 25+ DOF. Model sources:
- [`nao_v5_description`](https://github.com/ros-naoqi/nao_robot)
- [Pal Robotics fork](https://github.com/pal-robotics/nao_robot)

Spawn in Gazebo:
```bash
ros2 run ros_gz_sim create -file ~/nao_ws/src/nao_description/urdf/nao.urdf
```

Bridge joint commands from your `nao_control` nodes.

---

## 8. Quick Start Workflow

```bash
# Terminal 1: Gazebo
source /opt/ros/jazzy/setup.bash
gz sim

# Terminal 2: Clock bridge
source /opt/ros/jazzy/setup.bash
ros2 run ros_gz_bridge parameter_bridge /clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock

# Terminal 3: Spawn Nao
source ~/nao_ws/install/setup.bash
ros2 run ros_gz_sim create -file src/nao_description/nao.sdf

# Terminal 4: Control node
source ~/nao_ws/install/setup.bash
ros2 run nao_control walk_controller
```

---

## Key Links

- [ROS 2 Jazzy install](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html)
- [Gazebo Harmonic install](https://gazebosim.org/docs/harmonic/install_ubuntu)
- [Installing Gazebo with ROS](https://gazebosim.org/docs/harmonic/ros_installation)
- [ROS 2 ↔ Gazebo integration](https://gazebosim.org/docs/harmonic/ros2_integration)
- [`ros_gz` jazzy branch](https://github.com/gazebosim/ros_gz/tree/jazzy)
- [`ros_gz_bridge` README](https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_bridge/README.md)
- [`gz_ros2_control`](https://github.com/gazebosim/gz_ros2_control)
- [ros2_control docs](https://control.ros.org/jazzy/)
- [Nao ROS packages](https://github.com/ros-naoqi/nao_robot)
