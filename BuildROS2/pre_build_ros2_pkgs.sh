#!/bin/bash

## Get ROS2 code
ROS2_WS=$(pwd)/ros2_ws
cd $ROS2_WS
vcs import src < ../ros2_additional_pkgs.repos
