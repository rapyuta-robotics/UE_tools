#!/bin/bash

ROSDISTRO=$1
UE5_DIR=${2:-$UE5_DIR} # to mount the clang

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

OTHER_ARG=${3:-''}
docker buildx build -t yuokamoto1988/ue_ros2_base:$ROSDISTRO . -f Dockerfile.$ROSDISTRO --build-context ue5_extras=$UE5_DIR/Engine/Extras --progress=plain --no-cache