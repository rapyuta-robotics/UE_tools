#!/bin/bash
# Copyright 2020-2022 Rapyuta Robotics Co., Ltd.

Help()
{
    # Display Help
    echo "Syntax: ${BASH_SOURCE[0]} [-h] <UE_PATH> <ROS2_PKGS_WS> <PKGS>"
    echo "options:"
    echo "-h Print this Help."
    echo "arguments:"
    echo "-UE_PATH: Path to the UnrealEngine dir"
    echo "-ROS2_PKGS_WS: Path to target ROS2 pkg workspace"
    echo "-PKGS: Name of the target ROS2 pkgs"
}

while getopts ":h" option; do
    case $option in
        h) # display Help
            Help
            exit;;
        \?) # Invalid option
            echo "Error: Invalid option"
            Help
            exit;;
    esac
done

# Set exit on any non-zero status cmd
set -e

# Verify input dirs
check_empty() {
    if [[ "" == "$1" ]]; then
        printf "[$2] is empty!"
        Help
        exit 1
    fi
}
check_dir_valid() {
    check_empty $1 $2
    if [[ ! -d "$1" ]]; then
        printf "[$2] does not exist!"
        Help
        exit 1
    fi
}

UE_PATH=$1
check_dir_valid $UE_PATH "UE_PATH"
ROS2_PKGS_WS=$2
check_dir_valid $ROS2_PKGS_WS "ROS2_PKGS_WS"
PKGS=$3

clean_ros2_ws() {
    rm -rf $1/build $1/install $1/log
}
clean_ros2_ws $ROS2_PKGS_WS

export LANG=en_US.UTF-8

# Build ROS2 PKGS by UE clang toolchain
# export ROS_DOMAIN_ID=10
# pay attention it can be 'rmw_fastrtps_dynamic_cpp' too
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
# Building ros by exact UE clang toolchain
export UE_SYS_ROOT_PATH=$UE_PATH"/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v19_clang-11.0.1-centos7/x86_64-unknown-linux-gnu"
export CC=$UE_SYS_ROOT_PATH"/bin/clang"
export CXX=$UE_SYS_ROOT_PATH"/bin/clang++"

# -latomic issue - see more here https://github.com/ros2/ros2/issues/418
export LINKER_FLAGS="-latomic "\
"-Wl,-rpath=\${ORIGIN} "\
"-Wl,-rpath-link="$UE_SYS_ROOT_PATH" "\
"-Wl,-rpath-link="$UE_SYS_ROOT_PATH"/usr/lib "\
"-Wl,-rpath-link="$UE_SYS_ROOT_PATH"/usr/lib64 "\
"-Wl,-rpath-link=/usr/lib/x86_64-linux-gnu "\
"-Wl,-rpath-link=/usr/lib "

CMAKE_ARGS="-DCMAKE_SHARED_LINKER_FLAGS=${LINKER_FLAGS} -DCMAKE_EXE_LINKER_FLAGS=${LINKER_FLAGS} -DBUILD_TESTING=OFF --no-warn-unused-cli"

# Build ROS2_PKGS_WS
cd $ROS2_PKGS_WS
if [[ -z "$PKGS" ]]; then
    echo "Build all pkgs in ${ROS2_PKGS_WS}"
    colcon build --cmake-args ${CMAKE_ARGS}
else
    echo "Build pkgs ${PKGS}"
    colcon build --packages-select $PKGS --cmake-args ${CMAKE_ARGS}
fi
