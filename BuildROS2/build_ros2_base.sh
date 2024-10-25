#!/bin/bash

ROS2_WS=$1
ROS_DISTRO=$2

cleanup() {
    sudo rm -r -f $1/build $1/install $1/log
    sudo rm -r -f $1/build_renamed $1/install_renamed
}

cleanup $ROS2_WS

export LANG=en_US.UTF-8

# export ROS_DOMAIN_ID=10
# pay attention it can be 'rmw_fastrtps_dynamic_cpp' too
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp

# Building ros by exact UE clang toolchain
# not work. temporary commented out
# UE4
# export MY_SYS_ROOT_PATH=$UE_PATH"/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v19_clang-11.0.1-centos7/x86_64-unknown-linux-gnu"
# UE5
# export MY_SYS_ROOT_PATH=$UE_PATH"/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v20_clang-13.0.1-centos7/x86_64-unknown-linux-gnu"
# export CC=$MY_SYS_ROOT_PATH"/bin/clang"
# export CXX=$MY_SYS_ROOT_PATH"/bin/clang++"

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

# options when you build with UE's build tool chaain
# "-Wl,-rpath-link="$MY_SYS_ROOT_PATH" "\
# "-Wl,-rpath-link="$MY_SYS_ROOT_PATH"/usr/lib "\
# "-Wl,-rpath-link="$MY_SYS_ROOT_PATH"/usr/lib64 "\
# "-Wl,-rpath-link="$MY_SYS_ROOT_PATH"/lib "\
# "-Wl,-rpath-link="$MY_SYS_ROOT_PATH"/lib64 "\


pushd $ROS2_WS
colcon build \
    --cmake-clean-cache \
    --cmake-force-configure \
    --continue-on-error \
    --cmake-args \
        "-DCMAKE_SHARED_LINKER_FLAGS='$MY_LINKER_FLAGS'"\
        "-DCMAKE_EXE_LINKER_FLAGS='$MY_LINKER_FLAGS'"\
        "-DCMAKE_CXX_FLAGS='-stdlib=libstdc++'"\
        "-DCMAKE_CXX_FLAGS='-fpermissive'"\
        -DBUILD_TESTING=OFF \
    --no-warn-unused-cli \
   --packages-up-to rclc rcl_action
popd