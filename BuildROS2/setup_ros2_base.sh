#!/usr/bin/env bash

UE_PROJ_PATH=${1:-~/UnrealEngine}
CLEANUP=${3:-"true"}
ROS2_WS=$(pwd)/ros2_ws

if ${CLEANUP}; then
    echo 'remove ' $ROS2_WS
    sudo rm -r $ROS2_WS
fi

# install dependency and get ros2 sources
./pre_build_ros2_base.sh

# build ros2
./build_ros2_base.sh $UE_PROJ_PATH $ROS2_WS
