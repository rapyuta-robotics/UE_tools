FROM ros:humble-ros-base

RUN useradd -ms /bin/bash user 

RUN mkdir -p /home/user/
WORKDIR /home/user/
# clang-13
RUN echo 'deb http://archive.ubuntu.com/ubuntu/ focal-proposed universe' >> /etc/apt/sources.list
RUN sudo apt update && sudo apt upgrade -y  
RUN sudo apt install -y wget clang-13 patchelf libacl1-dev pip

RUN python3 -m pip install -U \
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
  setuptools==58.2.0 \
  pytest

# install Fast-RTPS and Cyclone DDS dependencies
RUN sudo apt install --no-install-recommends -y \
  libasio-dev \
  libtinyxml2-dev \
  libcunit1-dev

ENV ROS2_WS="/home/user/ros2_ws"
ENV ROS2_DISTRO="humble"

RUN mkdir -p ros2_ws/src
WORKDIR $ROS2_WS
RUN wget https://raw.githubusercontent.com/ros2/ros2/$ROS2_DISTRO/ros2.repos
RUN vcs import src < ros2.repos
RUN echo "############################################## \n Ignore ros1_bridge and example_interfaces.  \n ############################################### \n"
RUN touch src/ros2/example_interfaces/COLCON_IGNORE
RUN rosdep update
# ADD RTI_LICENSE.TXT /opt/rti.com/rti_connext_dds-6.0.1/ 

RUN export \
      DEBIAN_FRONTEND=noninteractive \
      RTI_NC_LICENSE_ACCEPTED=yes \
    && apt-get update \
    && if [ "${ROS2_DISTRO}" = "foxy" -o \
            "${ROS2_DISTRO}" = "eloquent" -o \
            "${ROS2_DISTRO}" = "dashing" ]; then \
         connext_version=5.3.1;\
         connext_arch=x64Linux3gcc5.4.0;\
       else\
         connext_version=6.0.1;\
         connext_arch=x64Linux4gcc7.3.0;\
       fi \
    && apt-get install -y rti-connext-dds-${connext_version}\
    && rm -f /opt/rti.com/rti_connext_dds \
    && ln -s /opt/rti.com/rti_connext_dds-${connext_version} /opt/rti.com/rti_connext_dds \
    && printf "%s" "${connext_arch}" > /opt/rti.com/rti_connext_dds.arch

ENV CONNEXTDDS_DIR=/opt/rti.com/rti_connext_dds

ARG RMW_CONNEXTDDS_DIR=/opt/rmw_connextdds
ENV RMW_CONNEXTDDS_DIR=${RMW_CONNEXTDDS_DIR}
ARG RMW_CONNEXTDDS_URL=https://github.com/ros2/rmw_connextdds
ARG RMW_CONNEXTDDS_BRANCH=
RUN if [ -n "${RMW_CONNEXTDDS_BRANCH}" ]; then \
      rmw_branch="${RMW_CONNEXTDDS_BRANCH}"; \
    elif [ "${ROS_DISTRO}" = "rolling" ]; then\
      rmw_branch="master";\
    else\
      rmw_branch="${ROS_DISTRO}";\
    fi \
    && git clone -b ${rmw_branch} ${RMW_CONNEXTDDS_URL} ${RMW_CONNEXTDDS_DIR}

# RUN rosdep install --from-paths src --ignore-src -y --skip-keys "fastcdr rti-connext-dds-5.3.1 urdfdom_headers"
WORKDIR /home/user/
RUN git clone --branch humble https://github.com/ros2/rclc.git $ROS2_WS/src/rclc



################################################################

# build_ros2_base file

ENV LANG=en_US.UTF-8

# pay attention it can be 'rmw_fastrtps_dynamic_cpp' too
ENV RMW_IMPLEMENTATION=rmw_fastrtps_cpp


# use locally installed clang-13
ENV CC="/usr/bin/clang-13"
ENV CXX="/usr/bin/clang++-13"

# -latomic issue - see more here https://github.com/ros2/ros2/issues/418
ENV MY_LINKER_FLAGS="-latomic "\
"-Wl,-rpath=\${ORIGIN} "\
"-Wl,-rpath-link=/usr/lib/x86_64-linux-gnu "\
"-Wl,-rpath-link=/usr/lib "
# "-Wl,-rpath-link=/lib32 "\
# "-Wl,-rpath-link=/lib/i386-linux-gnu " 

# options when you build with UE's build tool chaain
# "-Wl,-rpath-link="$MY_SYS_ROOT_PATH" "\
# "-Wl,-rpath-link="$MY_SYS_ROOT_PATH"/usr/lib "\
# "-Wl,-rpath-link="$MY_SYS_ROOT_PATH"/usr/lib64 "\
# "-Wl,-rpath-link="$MY_SYS_ROOT_PATH"/lib "\
# "-Wl,-rpath-link="$MY_SYS_ROOT_PATH"/lib64 "\


WORKDIR $ROS2_WS
RUN . /opt/ros/humble/setup.sh \
    && export CONNEXTDDS_ARCH=$(cat /opt/rti.com/rti_connext_dds.arch)\
    && MAKEFLAGS=-j$(nproc) colcon build \
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

WORKDIR /home/user/
ADD --chown=user:user build_and_install_ros2.py /home/user/
ADD --chown=user:user libs_utils.py /home/user/
ADD --chown=user:user patches /home/user/patches
ADD --chown=user:user build_and_install_ros2_base.py /home/user/


RUN python3 build_and_install_ros2_base.py --ue_path /home/user --ue_proj_path /home/user/Project
RUN ls /home/user/Project/Plugins/rclUE/ThirdParty/ros
# USER user
# RUN python3 build_and_install_ros2_base.py --ue_path /home/user/UnrealEngine --ue_proj_path /home/user/Documents/Unreal\ Projects/Cabane\ 5.1