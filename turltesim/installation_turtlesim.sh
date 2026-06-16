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
echo "Installing Gazebo Harmonic..."
sudo apt install -y lsb-release wget gnupg
sudo mkdir -p /usr/share/keyrings
sudo wget https://packages.osrfoundation.org/gazebo.gpg \
    -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" \
    | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
sudo apt update
sudo apt install -y gz-harmonic

echo ""
echo "Installing ros_gz_bridge..."
sudo apt install -y ros-humble-ros-gz-bridge

echo ""
echo "Installation complete."
echo ""
echo "Source ROS 2:"
echo "source /opt/ros/humble/setup.bash"
