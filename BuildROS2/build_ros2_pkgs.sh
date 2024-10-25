#!/bin/bash

ROS2_WS=$1
ROS_DISTRO=$2
PKGS=$3

# cleanup
for d in $2 ; 
do
    rm -r  $1/build/$d
    rm -r  $1/install/$d
done

export LANG=en_US.UTF-8

# export ROS_DOMAIN_ID=10
# pay attention it can be 'rmw_fastrtps_dynamic_cpp' too
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp

# use locally installed clang
CLANG_VER=13
if [ $ROS_DISTRO == "jazzy" ]; then
  CLANG_VER=18
fi

export CC="/usr/bin/clang-$CLANG_VER"
export CXX="/usr/bin/clang++-$CLANG_VER"


# -latomic issue - see more here https://github.com/ros2/ros2/issues/418
export MY_LINKER_FLAGS="-latomic "\
"-Wl,-rpath=\${ORIGIN} "\
"-Wl,-rpath-link=/usr/lib/x86_64-linux-gnu "\
"-Wl,-rpath-link=/usr/lib "

echo build $PKGS

pushd $ROS2_WS
    source install/setup.bash
    colcon build \
        --packages-skip-build-finished \
        --packages-up-to $PKGS \
        --cmake-args \
            "-DCMAKE_SHARED_LINKER_FLAGS='$MY_LINKER_FLAGS'" \
            "-DCMAKE_EXE_LINKER_FLAGS='$MY_LINKER_FLAGS'" \
            -DBUILD_TESTING=OFF --no-warn-unused-cli
popd