# RAS2026 — ROS 2 Turtlesim Control

Collection of ROS 2 (Humble) Python nodes for differential-drive robot control using the `turtlesim` simulator.

## Prerequisites

- Ubuntu 22.04
- ROS 2 Humble ([install guide](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html))

## Setup

```bash
# Install turtlesim dependencies
sudo apt update
sudo apt install -y ros-humble-turtlesim ros-humble-geometry-msgs python3-colcon-common-extensions

# Source ROS 2
source /opt/ros/humble/setup.bash
```

## Usage

Start the turtlesim simulator in a terminal:

```bash
ros2 run turtlesim turtlesim_node
```

In another terminal, source ROS 2 and run any node (each runs indefinitely; press Ctrl+C to stop):

### 1. Open-Loop Control (`open_loop.py`)

Publishes constant velocity commands — the turtle drives in a circle.

```bash
python3 turltesim/open_loop.py
```

### 2. Point Navigation (`goto_point.py`)

Closed-loop P-controller that drives the turtle to target `(xd, yd) = (8.0, 8.0)`.

```bash
python3 turltesim/goto_point.py
```

### 3. Trajectory Tracking (`multi_traj.py`)

Follows a reference trajectory loaded from `turltesim/config.yaml`. Supports four trajectory types (set via `trajectory.type`):

- `circle` — constant-radius circular path
- `ellipse` — elliptical path with semi-axes `a`, `b`
- `figure8` — figure-8 path
- `spiral` — outward spiral with configurable growth rate

```bash
python3 turltesim/multi_traj.py
```

## Configuration

Edit `turltesim/config.yaml` to tune:

| Section | Parameter | Description |
|---------|-----------|-------------|
| `controller` | `publish_rate` | Control loop frequency (Hz) |
| `gains` | `kv` | Linear velocity gain |
| `gains` | `kw` | Angular velocity gain |
| `trajectory` | `type` | Trajectory shape: `circle`, `ellipse`, `figure8`, `spiral` |

Each trajectory block has its own geometric parameters (center, radii, angular velocity, etc.).
