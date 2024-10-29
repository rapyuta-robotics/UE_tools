#!/usr/bin/env bash

ROS2_WS=$1
ROS_DISTRO=$2
PKGS=$3

# build ros2
./build_ros2_pkgs.sh $ROS2_WS $ROS_DISTRO "$PKGS"
