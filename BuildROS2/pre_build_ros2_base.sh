#!/bin/bash

#########################################################################
# install ros2 foxy
# https://docs.ros.org/en/foxy/Installation/Ubuntu-Development-Setup.html
#########################################################################

echo "
########################
Install ROS2 Foxy
########################
"

# cleanup
sudo rm /etc/apt/sources.list.d/ros2.list*
sudo rm /etc/ros/rosdep/sources.list.d/20-default.list
sudo rm ros2_ws/ros2.repos*

## Set locale
locale  # check for UTF-8

sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
#locale  # verify settings


## Add the ROS 2 apt repository
apt-cache policy | grep universe

sudo apt install software-properties-common
sudo add-apt-repository universe

sudo apt update && sudo apt install curl gnupg2 lsb-release
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key  -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(source /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

## Install development tools and ROS tools
sudo apt update && sudo apt install -y \
  build-essential \
  cmake \
  git \
  libbullet-dev \
  python3-colcon-common-extensions \
  python3-flake8 \
  python3-pip \
  python3-pytest-cov \
  python3-rosdep \
  python3-setuptools \
  python3-vcstool \
  wget
# install some pip packages needed for testing
python3 -m pip install -U \
  argcomplete \
  flake8-blind-except \
  flake8-builtins \
  flake8-class-newline \
  flake8-comprehensions \
  flake8-deprecated \
  flake8-docstrings \
  flake8-import-order \
  flake8-quotes \
  pytest-repeat \
  pytest-rerunfailures \
  pytest
# install Fast-RTPS dependencies
sudo apt install --no-install-recommends -y \
  libasio-dev \
  libtinyxml2-dev
# install Cyclone DDS dependencies
sudo apt install --no-install-recommends -y \
  libcunit1-dev


## Get ROS2 code
ROS2_WS=$(pwd)/ros2_ws
mkdir -p $ROS2_WS/src
cd $ROS2_WS
wget https://raw.githubusercontent.com/ros2/ros2/foxy/ros2.repos
vcs import src < ros2.repos

# Install dependencies using rosdep
#sudo apt upgrade
sudo rosdep init
rosdep update
rosdep install --from-paths src --ignore-src -y --skip-keys "fastcdr rti-connext-dds-5.3.1 urdfdom_headers"

cd -

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
git clone --branch foxy https://github.com/ros2/rclc.git $ROS2_WS/src/rclc

echo "
#######################
Patch rcpputils and error_handling
########################
"
cd $ROS2_WS/src/ros2/rcpputils
git apply ../../../../patches/rcpputils.patch

# can't patch here. patch after copied header under UE project.
# cd $ROS2_WS/src/ros2/rcutils
# git apply ../../../../patches/rcutils.patch

echo "
#######################
Other dependency to build and copy lib to UE
########################
"

sudo apt install patchelf
