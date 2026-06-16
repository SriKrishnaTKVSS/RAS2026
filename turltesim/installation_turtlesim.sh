#!/bin/bash

set -e

echo "Updating package list..."
sudo apt update

echo "Installing ROS 2 Humble turtlesim dependencies..."

sudo apt install -y \
    ros-humble-turtlesim \
    ros-humble-geometry-msgs \
    python3-colcon-common-extensions

echo ""
echo "Installation complete."
echo ""
echo "Source ROS 2:"
echo "source /opt/ros/humble/setup.bash"
