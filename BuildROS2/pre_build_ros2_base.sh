#!/bin/bash

#########################################################################
# install ros2 $ROS2_DISTRO
# https://docs.ros.org/en/$ROS2_DISTRO/Installation/Ubuntu-Development-Setup.html
#########################################################################

ROS2_WS=$1
ROS2_DISTRO=$2

echo "
########################
Install ROS2 $ROS2_DISTRO
########################
"

# cleanup
# sudo rm /etc/apt/sources.list.d/ros2.list*
# sudo rm /etc/ros/rosdep/sources.list.d/20-default.list
# sudo rm ros2_ws/ros2.repos*

# ## Set locale
# locale  # check for UTF-8

# sudo apt update && sudo apt install locales
# sudo locale-gen en_US en_US.UTF-8
# sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
# export LANG=en_US.UTF-8
# #locale  # verify settings


# ## Add the ROS 2 apt repository
# apt-cache policy | grep universe

# sudo apt install software-properties-common
# sudo add-apt-repository universe

# sudo apt update && sudo apt install curl gnupg2 lsb-release
# sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key  -o /usr/share/keyrings/ros-archive-keyring.gpg

# echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

## Install development tools and ROS tools
# sudo apt update && sudo apt install -y \
#   build-essential \
#   cmake \
#   git \
#   libbullet-dev \
#   python3-colcon-common-extensions \
#   python3-flake8 \
#   python3-pip \
#   python3-pytest-cov \
#   python3-rosdep \
#   python3-setuptools \
#   python3-vcstool \
#   wget
# # install some pip packages needed for testing
# python3 -m pip install -U \
#   argcomplete \
#   flake8-blind-except \
#   flake8-builtins \
#   flake8-class-newline \
#   flake8-comprehensions \
#   flake8-deprecated \
#   flake8-docstrings \
#   flake8-import-order \
#   flake8-quotes \
#   pytest-repeat \
#   pytest-rerunfailures \
#   pytest
# # install Fast-RTPS dependencies
# sudo apt install --no-install-recommends -y \
#   libasio-dev \
#   libtinyxml2-dev
# # install Cyclone DDS dependencies
# sudo apt install --no-install-recommends -y \
#   libcunit1-dev


echo "
#######################
Get ROS2 source 
########################
"
## Get ROS2 code
mkdir -p $ROS2_WS/src
pushd $ROS2_WS
  wget https://raw.githubusercontent.com/ros2/ros2/$ROS2_DISTRO/ros2.repos
  vcs import src < ros2.repos

  echo "
  ##############################################
  Ignore ros1_bridge and example_interfaces. 
  ###############################################
  "
  touch src/ros2/ros1_bridge/COLCON_IGNORE
  touch src/ros2/example_interfaces/COLCON_IGNORE

  # Install dependencies using rosdep
  #sudo apt upgrade
  sudo rosdep init
  rosdep update
  rosdep install --from-paths src --ignore-src -y --skip-keys "fastcdr rti-connext-dds-5.3.1 urdfdom_headers"
popd

#########################################################################
# Reinstall python package due to issues 
# https://github.com/ros-visualization/qt_gui_core/issues/212:
#########################################################################

echo "
#######################
Reinstall python package due to issues 
########################
"

sudo apt remove shiboken2 libshiboken2-dev libshiboken2-py3-5.14 -y
pip3 install shiboken2

echo "
#######################
Clone rclc 
########################
"
git clone --branch $ROS2_DISTRO https://github.com/ros2/rclc.git $ROS2_WS/src/rclc

echo "
#######################
Patch rcpputils 
########################
"
pushd $ROS2_WS/src/ros2/rcpputils
  git apply ../../../../patches/rcpputils.patch
popd

# can't patch here. patch after copied header under UE project.
# cd $ROS2_WS/src/ros2/rcutils
# git apply ../../../../patches/rcutils.patch

echo "
############################################################
[Temp hack]Patch Fast-DDS and asio to avod crash in Editor
#############################################################
"
pushd $ROS2_WS/src/eProsima/Fast-DDS
  git apply ../../../../patches/Fast-DDS.patch
  git submodule init
  git submodule update
  pushd thirdparty/asio
    git apply ../../../../../../patches/asio.patch  
  popd
popd

echo "
#######################
Other dependency to build and copy lib to UE
########################
"

# patchelf
sudo apt install patchelf -y

# iceoryx_hoofs dependency
sudo apt-get install libacl1-dev -y

# clang-13
echo 'deb http://archive.ubuntu.com/ubuntu/ focal-proposed universe' >> /etc/apt/sources.list
sudo apt update
sudo apt install clang-13 -y
