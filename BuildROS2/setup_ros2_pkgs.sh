#!/usr/bin/env bash

UE_PROJ_PATH=${1:-~/UnrealEngine}
ROS2_WS=$(pwd)/ros2_ws
PKGS=$2

# install dependency and get ros2 sources
./pre_build_ros2_pkgs.sh

# build ros2
./build_ros2_pkgs.sh $UE_PROJ_PATH $ROS2_WS "$PKGS"
