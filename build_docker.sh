#!/bin/bash

ROSDISTRO=$1

if [ $ROSDISTRO = "foxy" ]; then
  UBUNTU_VER=20.04
elif [ $ROSDISTRO = "humble" ]; then
  UBUNTU_VER=22.04
elif [ $ROSDISTRO = "jazzy" ]; then
  UBUNTU_VER=24.04
else
  echo ROSDISRO must be foxy, humble or jazzy
  exit
fi

OTHER_ARG=${2:-''}
echo $ROSDISTRO
docker build -t yuokamoto1988/ue_ros2_base:$ROSDISTRO . -f Dockerfile.$ROSDISTRO