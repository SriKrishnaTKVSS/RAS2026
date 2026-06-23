# Nao Humanoid Simulation — Step-by-Step Guide

**Works with:** ROS 2 Humble + Gazebo Harmonic AND ROS 2 Jazzy + Gazebo Harmonic  
**Goal:** Build a `nao_control` ROS 2 package with 6 Python nodes to command joints, walk, look around, and monitor the simulated Nao robot.

**Audience:** You know nothing about ROS 2 or Gazebo. Every command is here — copy, paste, run.

---

## What You Are Building

This guide creates a ROS 2 workspace with one package (`nao_control`) containing:

| Node | What it does |
|------|-------------|
| `trajectory_bridge` | Bridge between ROS JointTrajectory commands and Gazebo's per-joint topics (required for all other nodes) |
| `joint_commander` | Sits down, stands up, waves (one-shot demo) |
| `walk_controller` | Bipedal walking gait using sine waves |
| `head_controller` | Looks around (continuous sinusoidal motion) |
| `sensor_monitor` | Prints simulation clock time every 5 seconds |
| `demo_sequence` | Choreographed sequence: look → wave → sit → stand |

The Nao model comes from **Gazebo Fuel** (built into Gazebo Sim) — no manual model files needed.

---

## 0. Prerequisites

You need **ROS 2**, **Gazebo Harmonic**, and **ros_gz_bridge** installed.

```bash
# Check ROS 2
source /opt/ros/humble/setup.bash   # or /opt/ros/jazzy/setup.bash
ros2 --version

# Check Gazebo
gz sim --version

# Check ros_gz_bridge
ros2 pkg list | grep ros_gz_bridge
```

If any of these fail, install the environment first:

| Your OS | ROS 2 | Gazebo | Setup guide |
|---------|-------|--------|-------------|
| Ubuntu 22.04 | Humble | Harmonic | `instructions/humble_harmonic_setup.md` |
| Ubuntu 24.04 | Jazzy | Harmonic | `instructions/jazzy_harmonic_setup.md` |

Also install these required system packages:

```bash
sudo apt update
sudo apt install -y python3-colcon-common-extensions python3-gz-transport13 python3-gz-msgs10
```

---

## 1. Clone This Repository

```bash
cd ~
git clone <REPO_URL>    # ← ask your instructor for the URL
cd RAS2026
```

The Python scripts we need are in `instructions/nao_simulation/scripts/`.

---

## 2. Create the ROS 2 Workspace & Package

```bash
mkdir -p ~/nao_ws/src
cd ~/nao_ws/src

ros2 pkg create nao_control --build-type ament_python \
  --dependencies rclpy geometry_msgs trajectory_msgs sensor_msgs std_msgs

cd nao_control

mkdir config launch
```

This creates the package skeleton:

```
~/nao_ws/src/nao_control/
  ├── config/                 (you just created this)
  ├── launch/                 (you just created this)
  ├── nao_control/
  │   └── __init__.py
  ├── package.xml
  ├── resource/nao_control
  ├── setup.cfg
  ├── setup.py
  └── test/
```

---

## 3. Edit `package.xml`

Open `~/nao_ws/src/nao_control/package.xml` and replace its contents with:

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>nao_control</name>
  <version>0.1.0</version>
  <description>Nao humanoid control nodes for Gazebo simulation</description>
  <maintainer email="student@example.com">NAO Controller</maintainer>
  <license>MIT</license>

  <buildtool_depend>ament_python</buildtool_depend>

  <depend>rclpy</depend>
  <depend>geometry_msgs</depend>
  <depend>trajectory_msgs</depend>
  <depend>sensor_msgs</depend>
  <depend>std_msgs</depend>

  <exec_depend>ros2launch</exec_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

---

## 4. Edit `setup.py`

Open `~/nao_ws/src/nao_control/setup.py` and replace its contents with:

```python
from setuptools import find_packages, setup

package_name = 'nao_control'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', ['config/bridge.yaml']),
        ('share/' + package_name + '/launch', ['launch/simulation.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='NAO Controller',
    maintainer_email='student@example.com',
    description='Nao humanoid control nodes for Gazebo simulation',
    license='MIT',
    entry_points={
        'console_scripts': [
            'joint_commander = nao_control.joint_commander:main',
            'walk_controller = nao_control.walk_controller:main',
            'head_controller = nao_control.head_controller:main',
            'sensor_monitor = nao_control.sensor_monitor:main',
            'demo_sequence = nao_control.demo_sequence:main',
            'trajectory_bridge = nao_control.trajectory_bridge:main',
        ],
    },
)
```

---

## 5. Create the Bridge Config

Create `~/nao_ws/src/nao_control/config/bridge.yaml` with this content:

```yaml
# Bridge configuration for Nao in Gazebo Sim
#
# The Fuel Nao model uses per-joint cmd_pos topics for control.
# Joint commands go through trajectory_bridge.py which converts
# ROS JointTrajectory -> per-joint gz.msgs.Double publications.
#
# NOTE: This model has NO camera/IMU/laser/odometry topics.

# Clock
- ros_topic_name: "clock"
  gz_topic_name: "/clock"
  ros_type_name: "rosgraph_msgs/msg/Clock"
  gz_type_name: "gz.msgs.Clock"
  direction: GZ_TO_ROS
```

> The bridge only syncs the simulation clock. All 24 joint commands are handled by `trajectory_bridge.py` (not by this YAML).

---

## 6. Create the Launch File

Create `~/nao_ws/src/nao_control/launch/simulation.launch.py` with this content:

```python
import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node


def generate_launch_description():
    bridge_config = os.path.join(
        os.path.expanduser('~'), 'nao_ws', 'src', 'nao_control', 'config', 'bridge.yaml'
    )

    return LaunchDescription([
        ExecuteProcess(
            cmd=['gz', 'sim', '-r'],
            output='screen',
        ),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            arguments=['--ros-args', '-p', f'config_file:={bridge_config}'],
            output='screen',
        ),
    ])
```

This launch file starts Gazebo + the ROS-GZ bridge together.

---

## 7. Copy the Python Scripts from the Repo

Now copy all the Python scripts from the cloned repository into the package:

```bash
# From the cloned RAS2026 repo:
cp ~/RAS2026/instructions/nao_simulation/scripts/*.py \
   ~/nao_ws/src/nao_control/nao_control/

# These should already exist, but copy them again to be safe:
cp ~/RAS2026/instructions/nao_simulation/config/bridge.yaml \
   ~/nao_ws/src/nao_control/config/

cp ~/RAS2026/instructions/nao_simulation/simulation.launch.py \
   ~/nao_ws/src/nao_control/launch/
```

Verify the file structure looks like this:

```bash
# Install tree if you don't have it: sudo apt install tree
tree ~/nao_ws/src/nao_control/
```

Expected output:

```
/home/<you>/nao_ws/src/nao_control/
  ├── config/
  │   └── bridge.yaml
  ├── launch/
  │   └── simulation.launch.py
  ├── nao_control/
  │   ├── __init__.py
  │   ├── demo_sequence.py
  │   ├── head_controller.py
  │   ├── joint_commander.py
  │   ├── sensor_monitor.py
  │   ├── trajectory_bridge.py
  │   └── walk_controller.py
  ├── package.xml
  ├── resource/
  │   └── nao_control
  ├── setup.cfg
  ├── setup.py
  └── test/
```

---

## 8. Build the Package

```bash
cd ~/nao_ws
colcon build --packages-select nao_control
source install/setup.bash
```

> **Whenever you open a new terminal** to run a node, you must re-run `source ~/nao_ws/install/setup.bash` (or add it to `~/.bashrc`).

---

## 9. Run the Simulation

### 9a. Terminal 1 — Gazebo Simulator

Open a terminal and run:

```bash
source /opt/ros/humble/setup.bash   # or jazzy
gz sim
```

Once the Gazebo GUI opens:
1. Click the **☰** menu (top-left) → **Insert** → **Fuel** tab
2. In the search bar, type **Nao**
3. Click the result **"NAO with Ignition position controller"** by **OpenRobotics**
4. Click anywhere on the ground plane to place the robot
5. The model name is `Nao` (capital N) — this is used in the topic names

> ⏳ The first insert downloads the model from the cloud — this takes a few seconds.

### 9b. Terminal 2 — Bridge + Trajectory Bridge

Open a second terminal:

```bash
source /opt/ros/humble/setup.bash   # or jazzy
source ~/nao_ws/install/setup.bash

# Start the ROS-GZ clock bridge in the background
ros2 run ros_gz_bridge parameter_bridge \
  --ros-args -p config_file:=$HOME/nao_ws/src/nao_control/config/bridge.yaml &

# Start the trajectory bridge (keeps running)
ros2 run nao_control trajectory_bridge
```

You should see 24 log lines like:
```
[INFO] Advertised /model/Nao/joint/HeadYaw/0/cmd_pos
[INFO] Advertised /model/Nao/joint/HeadPitch/0/cmd_pos
...
[INFO] Trajectory bridge ready
```

> **Important:** Use `$HOME` instead of `~` in the bridge config path. The tilde `~` does not expand correctly in ROS 2 parameter files.

### 9c. Terminal 3 — Run a Control Node

Open a third terminal and pick one of these:

```bash
source ~/nao_ws/install/setup.bash

# Option 1: Sit → Stand → Wave demo
ros2 run nao_control joint_commander

# Option 2: Walking gait (press Ctrl+C to stop)
ros2 run nao_control walk_controller

# Option 3: Look around (press Ctrl+C to stop)
ros2 run nao_control head_controller

# Option 4: Monitor simulation time
ros2 run nao_control sensor_monitor

# Option 5: Full choreography (look → wave → sit → stand)
ros2 run nao_control demo_sequence
```

---

## 10. Run with the Launch File (Optional)

Instead of manually running Terminal 1 + half of Terminal 2, you can use the launch file:

```bash
source /opt/ros/humble/setup.bash   # or jazzy
source ~/nao_ws/install/setup.bash

ros2 launch nao_control simulation.launch.py
```

This starts Gazebo + the clock bridge together. You still need to:
1. Insert the Nao model from Fuel (manual GUI step)
2. Run `trajectory_bridge` in a separate terminal
3. Run a control node in another terminal

---

## Quick Test Commands

```bash
# List all active ROS 2 topics
ros2 topic list

# Find Gazebo topics for Nao's joints
gz topic -l | grep -i nao

# Manually send a head turn command (trajectory_bridge must be running)
ros2 topic pub /joint_trajectory trajectory_msgs/msg/JointTrajectory \
  "{joint_names: ['HeadYaw'], points: [{positions: [0.5], time_from_start: {sec: 1, nanosec: 0}}]}" \
  --once
```

---

## Node Source Code Reference

The 6 Python files are listed below for reference. You already copied them from the repo in Step 7, so you don't need to type these manually.

### Reference A — `trajectory_bridge.py`

Converts ROS `JointTrajectory` messages into per-joint `gz.msgs.Double` commands for Gazebo. Required for all other nodes to work.

```python
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory
from gz.transport13 import Node as GzNode
from gz.msgs10.double_pb2 import Double


NAO_JOINTS = [
    'HeadYaw', 'HeadPitch',
    'LHipYawPitch', 'LHipRoll', 'LHipPitch', 'LKneePitch', 'LAnklePitch', 'LAnkleRoll',
    'RHipYawPitch', 'RHipRoll', 'RHipPitch', 'RKneePitch', 'RAnklePitch', 'RAnkleRoll',
    'LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 'LElbowRoll', 'LWristYaw',
    'RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll', 'RWristYaw',
]


class TrajectoryBridge(Node):
    def __init__(self):
        super().__init__('trajectory_bridge')
        self.gz_node = GzNode()
        self.gz_pubs = {}
        for joint in NAO_JOINTS:
            topic = f'/model/Nao/joint/{joint}/0/cmd_pos'
            pub = self.gz_node.advertise(topic, Double)
            self.gz_pubs[joint] = (topic, pub)
            self.get_logger().info(f'Advertised {topic}')
        self.sub = self.create_subscription(
            JointTrajectory, '/joint_trajectory', self.trajectory_cb, 10)
        self.get_logger().info('Trajectory bridge ready')

    def trajectory_cb(self, msg):
        names = msg.joint_names
        if msg.points:
            positions = msg.points[0].positions
            for name, pos in zip(names, positions):
                if name in self.gz_pubs:
                    d = Double()
                    d.data = float(pos)
                    self.gz_pubs[name][1].publish(d)
                    self.get_logger().debug(f'{name} -> {pos:.3f}')
                else:
                    self.get_logger().warn(f'Unknown joint: {name}')


def main(args=None):
    rclpy.init(args=args)
    node = TrajectoryBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

---

### Reference B — `joint_commander.py`

Sends a sequence of joint positions to sit down, stand up, and wave the right arm.

```python
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration


class JointCommander(Node):
    def __init__(self):
        super().__init__('joint_commander')
        self.pub = self.create_publisher(
            JointTrajectory, '/joint_trajectory', 10)
        self.get_logger().info('Joint commander ready')

    def send_pose(self, joint_names, positions, duration_sec=1.0):
        msg = JointTrajectory()
        msg.joint_names = joint_names
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start = Duration(
            sec=int(duration_sec),
            nanosec=int((duration_sec % 1) * 1e9))
        msg.points = [point]
        self.pub.publish(msg)
        names = ', '.join(joint_names)
        self.get_logger().info(
            f'Moved joints [{names}] to positions {positions}')


def main(args=None):
    rclpy.init(args=args)
    node = JointCommander()

    joint_names = [
        'LHipPitch', 'RHipPitch',
        'LKneePitch', 'RKneePitch',
        'LAnklePitch', 'RAnklePitch']

    node.get_logger().info('--- Sit down ---')
    node.send_pose(joint_names, [0.5, 0.5, 1.0, 1.0, 0.3, 0.3], 2.0)
    rclpy.spin_once(node, timeout_sec=2.5)

    node.get_logger().info('--- Stand up ---')
    node.send_pose(joint_names, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 2.0)
    rclpy.spin_once(node, timeout_sec=2.5)

    node.get_logger().info('--- Wave right arm ---')
    arm_joints = ['RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll']
    arm_pose = [-0.5, -0.3, 0.0, 0.5]
    node.send_pose(arm_joints, arm_pose, 1.5)
    rclpy.spin_once(node, timeout_sec=2.0)

    node.send_pose(arm_joints, [0.0, 0.0, 0.0, 0.0], 1.0)
    rclpy.spin_once(node, timeout_sec=1.5)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

---

### Reference C — `walk_controller.py`

Generates a periodic walking gait using sine waves for hip and knee motion on alternating legs.

```python
import math
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration


class WalkController(Node):
    LEG_JOINTS = [
        'LHipYawPitch', 'LHipRoll', 'LHipPitch', 'LKneePitch',
        'LAnklePitch', 'LAnkleRoll',
        'RHipYawPitch', 'RHipRoll', 'RHipPitch', 'RKneePitch',
        'RAnklePitch', 'RAnkleRoll']

    def __init__(self):
        super().__init__('walk_controller')
        self.pub = self.create_publisher(
            JointTrajectory, '/joint_trajectory', 10)
        self.timer = self.create_timer(0.05, self.walk_step)
        self.step_time = 0.0
        self.amplitude = 0.3
        self.forward_swing = 0.4
        self.lateral_tilt = 0.05
        self.walking = False
        self.get_logger().info('Walk controller ready')

    def start(self):
        self.walking = True
        self.step_time = 0.0
        self.get_logger().info('Started walking')

    def stop(self):
        self.walking = False
        self.get_logger().info('Stopped walking')

    def walk_step(self):
        if not self.walking:
            return

        dt = 0.05
        self.step_time += dt
        t = self.step_time

        left_swing = math.sin(t * 3.0)
        right_swing = math.sin(t * 3.0 + math.pi)

        l_hip_pitch = self.forward_swing * max(0, left_swing)
        r_hip_pitch = self.forward_swing * max(0, right_swing)

        l_knee_pitch = self.amplitude * max(0, left_swing)
        r_knee_pitch = self.amplitude * max(0, right_swing)

        l_ankle_pitch = -l_knee_pitch * 0.5
        r_ankle_pitch = -r_knee_pitch * 0.5

        l_hip_roll = self.lateral_tilt * math.sin(t * 3.0)
        r_hip_roll = -l_hip_roll

        positions = [
            0.0,
            l_hip_roll,
            l_hip_pitch,
            l_knee_pitch,
            l_ankle_pitch,
            0.0,
            0.0,
            r_hip_roll,
            r_hip_pitch,
            r_knee_pitch,
            r_ankle_pitch,
            0.0,
        ]

        msg = JointTrajectory()
        msg.joint_names = self.LEG_JOINTS
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start = Duration(sec=0, nanosec=50000000)
        msg.points = [point]
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = WalkController()

    node.start()
    for _ in range(100):
        rclpy.spin_once(node, timeout_sec=0.05)
    node.stop()

    for _ in range(20):
        rclpy.spin_once(node, timeout_sec=0.05)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

---

### Reference D — `head_controller.py`

Moves Nao's head yaw and pitch in a smooth sinusoidal pattern.

```python
import math
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration


class HeadController(Node):
    HEAD_JOINTS = ['HeadYaw', 'HeadPitch']

    def __init__(self):
        super().__init__('head_controller')
        self.pub = self.create_publisher(
            JointTrajectory, '/joint_trajectory', 10)
        self.timer = self.create_timer(0.1, self.look_around)
        self.t = 0.0
        self.get_logger().info('Head controller active')

    def look_around(self):
        self.t += 0.1
        yaw = 0.8 * math.sin(self.t * 0.5)
        pitch = 0.3 * math.sin(self.t * 0.3 + 1.0)

        msg = JointTrajectory()
        msg.joint_names = self.HEAD_JOINTS
        point = JointTrajectoryPoint()
        point.positions = [yaw, pitch]
        point.time_from_start = Duration(sec=0, nanosec=100000000)
        msg.points = [point]
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = HeadController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

---

### Reference E — `sensor_monitor.py`

Monitors the `/clock` topic and reports simulation time every 5 seconds.

```python
import rclpy
from rclpy.node import Node
from rosgraph_msgs.msg import Clock


class SensorMonitor(Node):
    def __init__(self):
        super().__init__('sensor_monitor')
        self.clock_sub = self.create_subscription(
            Clock, '/clock', self.clock_cb, 10)
        self.clock_msg = None
        self.timer = self.create_timer(5.0, self.report)
        self.get_logger().info(
            'Sensor monitor active — reporting every 5s\n'
            'NOTE: The Fuel Nao model has no camera/IMU/laser/odometry topics.\n'
            'Joint states are embedded in /world/nao_world/state (not bridged).\n'
            'Use: gz topic -e -t /world/nao_world/state | grep -A2 "name:.*joint"')

    def clock_cb(self, msg):
        self.clock_msg = msg

    def report(self):
        if self.clock_msg:
            t = self.clock_msg.clock
            self.get_logger().info(
                f'Sim running — sim time: {t.sec:>6}s.{t.nanosec:09d}')
        else:
            self.get_logger().info('Waiting for /clock...')


def main(args=None):
    rclpy.init(args=args)
    node = SensorMonitor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

---

### Reference F — `demo_sequence.py`

Runs a choreographed sequence: look around → wave → sit → stand.

```python
import time
import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
from std_msgs.msg import String


class DemoSequence(Node):
    HEAD_JOINTS = ['HeadYaw', 'HeadPitch']
    ARM_JOINTS = ['RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll']
    LEG_JOINTS = [
        'LHipPitch', 'RHipPitch',
        'LKneePitch', 'RKneePitch',
        'LAnklePitch', 'RAnklePitch']

    def __init__(self):
        super().__init__('demo_sequence')
        self.traj_pub = self.create_publisher(
            JointTrajectory, '/joint_trajectory', 10)
        self.verbose_pub = self.create_publisher(String, '/demo/status', 10)
        self.get_logger().info('Demo sequence ready')

    def announce(self, text):
        self.get_logger().info(f'[DEMO] {text}')
        self.verbose_pub.publish(String(data=text))

    def send_pose(self, joint_names, positions, duration_sec=1.0):
        msg = JointTrajectory()
        msg.joint_names = joint_names
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start = Duration(
            sec=int(duration_sec),
            nanosec=int((duration_sec % 1) * 1e9))
        msg.points = [point]
        self.traj_pub.publish(msg)

    def wait(self, seconds):
        self.get_logger().info(f'Waiting {seconds}s...')
        time.sleep(seconds)

    def run(self):
        self.announce('Starting demo sequence')

        self.announce('Step 1/5 — Looking around')
        self.send_pose(self.HEAD_JOINTS, [0.5, 0.0], 1.0)
        self.wait(1.5)
        self.send_pose(self.HEAD_JOINTS, [-0.5, 0.2], 1.0)
        self.wait(1.5)
        self.send_pose(self.HEAD_JOINTS, [0.0, -0.3], 1.0)
        self.wait(1.5)
        self.send_pose(self.HEAD_JOINTS, [0.0, 0.0], 0.5)
        self.wait(1.0)

        self.announce('Step 2/5 — Waving')
        self.send_pose(self.ARM_JOINTS, [-0.8, -0.2, 0.0, 0.8], 1.0)
        self.wait(1.5)
        for _ in range(3):
            self.send_pose(
                self.ARM_JOINTS, [-0.8, -0.2, 0.0, 0.8], 0.3)
            self.wait(0.4)
            self.send_pose(
                self.ARM_JOINTS, [-0.8, 0.0, 0.0, 0.5], 0.3)
            self.wait(0.4)
        self.send_pose(self.ARM_JOINTS, [0.0, 0.0, 0.0, 0.0], 1.0)
        self.wait(1.5)

        self.announce('Step 3/5 — Sitting down')
        sit_pose = [0.5, 0.5, 1.2, 1.2, 0.3, 0.3]
        self.send_pose(self.LEG_JOINTS, sit_pose, 2.0)
        self.wait(2.5)

        self.announce('Step 4/5 — Standing up')
        stand_pose = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.send_pose(self.LEG_JOINTS, stand_pose, 2.0)
        self.wait(2.5)

        self.announce('Step 5/5 — Demo complete!')
        self.announce('All steps finished successfully.')


def main(args=None):
    rclpy.init(args=args)
    node = DemoSequence()
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

---

## Nao Joint Reference

| Joint | Range (rad) | Function |
|-------|-------------|----------|
| HeadYaw | -2.09 to 2.09 | Turn head left/right |
| HeadPitch | -0.67 to 0.51 | Tilt head up/down |
| LShoulderPitch | -2.09 to 2.09 | Left arm forward/back |
| LShoulderRoll | -0.31 to 1.33 | Left arm up/down (side) |
| LElbowYaw | -2.09 to 2.09 | Left forearm twist |
| LElbowRoll | -1.54 to -0.01 | Left forearm bend |
| LWristYaw | -1.82 to 1.82 | Left wrist twist |
| RShoulderPitch | -2.09 to 2.09 | Right arm forward/back |
| RShoulderRoll | -0.31 to 1.33 | Right arm up/down (side) |
| RElbowYaw | -2.09 to 2.09 | Right forearm twist |
| RElbowRoll | -1.54 to -0.01 | Right forearm bend |
| RWristYaw | -1.82 to 1.82 | Right wrist twist |
| LHipYawPitch | -1.15 to 1.15 | Left leg twist |
| LHipRoll | -0.38 to 0.79 | Left leg sideways |
| LHipPitch | -1.77 to 0.48 | Left thigh forward/back |
| LKneePitch | -0.09 to 2.12 | Left knee bend |
| LAnklePitch | -1.19 to 0.92 | Left foot tilt |
| LAnkleRoll | -0.40 to 0.40 | Left foot tilt sideways |
| RHipYawPitch | -1.15 to 1.15 | Right leg twist |
| RHipRoll | -0.38 to 0.79 | Right leg sideways |
| RHipPitch | -1.77 to 0.48 | Right thigh forward/back |
| RKneePitch | -0.09 to 2.12 | Right knee bend |
| RAnklePitch | -1.19 to 0.92 | Right foot tilt |
| RAnkleRoll | -0.40 to 0.40 | Right foot tilt sideways |

---

## Troubleshooting

### "bridge.yaml: No such file or directory"
**Cause:** The `~` tilde character doesn't expand in ROS 2 parameter paths.  
**Fix:** Use `$HOME` instead:
```bash
ros2 run ros_gz_bridge parameter_bridge \
  --ros-args -p config_file:=$HOME/nao_ws/src/nao_control/config/bridge.yaml
```

### "trajectory_bridge: command not found"
**Cause:** You forgot to source the workspace.  
**Fix:**
```bash
source ~/nao_ws/install/setup.bash
```

### Nao doesn't appear in Insert → Fuel
**Causes:**
- No internet connection (Fuel requires internet)
- Firewall blocking `fuel.gazebosim.org`
**Try:**
- Restart `gz sim`
- Check your internet connection
- Search for "Nao" (case-insensitive) in the Fuel tab

### Joints don't move
**Check:**
1. Is `trajectory_bridge` running in Terminal 2? (Look for "Trajectory bridge ready")
2. Is the model name `Nao` (capital N)? The topics use `/model/Nao/joint/...`
3. Is Gazebo paused? Click the **▶** play button in the GUI
4. Are you publishing to `/joint_trajectory`? Use `ros2 topic echo /joint_trajectory` to verify

### "ModuleNotFoundError: No module named 'gz'"
**Fix:** Install the Python bindings:
```bash
sudo apt install -y python3-gz-transport13 python3-gz-msgs10
```

### "ModuleNotFoundError: No module named 'rosgraph_msgs'" or similar
**Fix:** The system packages are not sourced:
```bash
source /opt/ros/humble/setup.bash   # or jazzy
```

---

## Key Links

- [ros_gz_bridge README](https://github.com/gazebosim/ros_gz/blob/jazzy/ros_gz_bridge/README.md)
- [ROS 2 ↔ Gazebo integration](https://gazebosim.org/docs/harmonic/ros2_integration)
- [Gazebo Fuel — Nao model](https://app.gazebosim.org/)
- [Trajectory messages](https://docs.ros2.org/latest/api/trajectory_msgs/)
