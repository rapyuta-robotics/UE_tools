UE_tools
==========
# Overview
This repo has tools to build and install ros2 lib to UnrealEngine Plugins.
[rclUE](https://github.com/rapyuta-robotics/rclUE) has lib and codes build/generated from this repo.
This repo can be used to build custom msg and install into your own UE plugins as well.

*[Details](#details) and [Module Overview](#module-overview) is for developers.

# Build and install with docker
Execute operation inside docker container and copy inside from container.

Available images:
- `yuokamoto1988/ue_ros2_base:foxy` : Ubuntu 20.04 with ROS2 foxy
- `yuokamoto1988/ue_ros2_base:humble` : Ubuntu 22.04 with ROS2 humble
- `yuokamoto1988/ue_ros2_base:jazzy` : Ubuntu 24.04 with ROS2 jazzy

## General usage
- 
    `python3 docker_build_install_codegen.py --type <base or pkgs> [--build] [--install] [--codegen] [--rosdistro <foxy, humble or jazzy>]  [--config <path to yaml>]`
- options
    - --type: 
        - base: Build core ros2 libs and copy to target plugin. see [ROS2 Lib Update](#ros2-lib-update) 
        - pkgs: Build given pkgs in config and copy to target plugin . see [Interface update](#interface-update) 
    - --build: 

        Build core lib or pkgs in config under ros2_ws. `--type base --build` is done as part of Docker image build.
    - --install:

        install lib and header from ros2_ws. lib and headers are installed into UE project written in config file specify by `--config` option.
    - --codegen: 

        Generate UE code and copy to target plugins. Only valid with `--type pkgs`. Generated codes are copied to UE project written in config file specify by `--config` option.
    - --config:

        config file path. please refer default_config.yaml. you can provide multiple config file and parameters are overwritten by later config files. Scripts loads `default.config` always as a first yaml file.
    - --pull_inside_docker:

        Pull additional repo specified in config file inside or outside of docker. If you not specify this option, repo is copied in `<current dir>/tmp` dir, which is useful to clone private repos. Please refer ros2_additional_pkgs.repos.

## Usage/example
### Add custom lib to your Plugin
1. Create yaml file which has path to your project and plugin which you want to install ros2 libs. Please refer default.yaml file as a config file template. 
2. `python3 docker_build_install_codegen.py --type pkgs --build --install --codegen --rosdistro foxy --config <path to your yaml file>`
    1. example is `custom_config.yaml`
3. Update your plugin build.cs to build with lib and headers. Please refer rclUE.buid.cs.

### Base roslib update in rclUE(for developer)
    *This build operation is done as part of image build process. Please check Dockerfile.
    *rclUE already has installed lib and headers and generated codes.
    *You can run without `--build` to just install and generate code from docker container. 
1. `python3 docker_build_install_codegen.py --type base [--build] --install --codegen --rosdistro foxy`
 


## Docker Image build
`./build_docker.sh <foxy, humble or jazzy>`

# Build and install without docker
    *build inside docker is recommended.
    *This can broke your locally installed ROS2. Please re-run `sudo apt install ros-<foxy, humble or jazzy>-destop` after this operation.

- `python3 build_install_codegen.py --type <base or pkgs> --codegen --build --config <path to yaml>`
- options
    - --type: 
        - base: Build core ros2 libs and copy to target plugin. see [ROS2 Lib Update](#ros2-lib-update) 
        - pkgs: Build given pkgs in config and copy to target plugin . see [Interface update](#interface-update) 
    - --build: 
        
        Build core lib or pkgs in config under BuildROS2/ros2_ws. You need to copy custom src manually if you need.
    - --codegen: 

        Generate UE code and copy to target plugins. Only valid with --type==pkgs
    - --config:

        Config file path. please refer default_config.yaml. you can provide multiple config file and parameters are overwritten by later config files.
    - --skip_pull:
        
        Avoid pulling repos.



*need to build core lib once with `--type base` to build other pkgs.

*this helper script uses [ROS2 Lib Update](#ros2-lib-update) and [Interface update](#interface-update) internally.

## Usage/example
### Add custom lib to your Plugin
1. Create yaml file which has path to your project and plugin which you want to install ros2 libs. Please refer default.yaml file as a config file template.
2. build ros2 base and base msg. This will build pkgs inside `ros2_ws` dir
    ```
    python3 build_install_codegen.py --type base --build
    python3 build_install_codegen.py --type pkgs --build
    ```
3. build your custom msgs
    ```
    python3 build_install_codegen.py --type pkgs --build --codegen --install --config custom_config.yaml 

    ```
4. Update your plugin build.cs to build with lib and headers. Please refer rclUE.buid.cs.

# Module Overview

## ROS2 Lib update

[rclUE](https://github.com/rapyuta-robotics/rclUE) has ros2 lib and header files to use ROS2 core 
    functionality from UnrealEngine. 
    
If you want to update ros2 lib in rclUE, need to follow [Build core lib](#build-core-lib) which build libs and copy lib and header files under rclUE.

## Interface update

Commonly used interfaces such as std_msgs are inside rclUE, but sometime you want to use your custom msg from UnrealEngine.

To use new msg in UnrealEngine Project,

1. [Build msg lib](#build-msg-lib) :build msg lib with patches
2. [Generate source files](#generate-source-files) :generate .h and .cpp files which are used inside UnrealEngine
3. [Copy source files to Unreal Project](#copy-source-files-to-unreal-project) :copy generated .h and .cpp files to UnrealEngine project.
4. Build your UnrealEngine project.
 

# Details

## BuiildROS2
Python scripts to build ros2 foxy pkgs from [source](https://docs.ros.org/en/foxy/Installation/Ubuntu-Development-Setup.html) with necessary changes to be used inside UnrealEngine project. Generated lib and header files are used inside UnrealEngine project, mainly by [rclUE](https://github.com/rapyuta-robotics/rclUE).

### Patches
We apply patch for ros2 to avoid setting LD_LIBRARY_PATH environment variable to the dynamic libs paths.
You can find changes in BuildROS2/patches
- rcpputils: return library names instead of empty string to make it use without setting env variable LD_LIBRARY_PATH.
- rcutils: comment out \_\_STDC_VERSION\_\_ since it is not always defined.

### Usage
#### Build core lib

1. cd UE_tools/BuildROS2 
2. python3 build_and_install_ros2_base.py --ue_path /home/user/UnrealEngine/ --ue_proj_path /home/user/turtlebot3-UE/`

    e.g. 

    `python3 build_and_install_ros2_base.py --ue_path /home/user/UnrealEngine --ue_proj_path /home/user/turtlebot3-UE`

#### Build msg lib
    
1. cd UE_tools/BuildROS2
2. python3 build_and_install_ros2_pkgs.py --ue_path <path to UnrealEngine> --ue_proj_path <path to UnrealEngine project>  --ros_pkgs <target pkgs>

    e.g. 

    `python3 build_and_install_ros2_pkgs.py --ue_path /home/user/UnrealEngine/ --ue_proj_path /home/user/turtlebot3-UE/ --ros_pkgs ue_msgs std_msgs example_interfaces`

### Scripts
- **build_and_install_ros2_base.py**: 
    
    Build ros2 foxy from source with patches and copy lib and header files to UnrealEngine project folder. 
    
    This is mainly used to update ros2 lib in the [rclUE](https://github.com/rapyuta-robotics/rclUE). This is required to create lib and header for core ros2 functionality, e.g. creating node, publisher, subscriber, etc.


    This script will create **ros2_ws** under BuildROS2 and build there.
    
    \* This script will modify local ros2 installation. Need to `sudo apt install ros-foxy-desktop` if you want to use standard ros2 foxy. todo: build inside docker to avoid affecting local setup.
    

    \* **Note**
    
    - Reinstall python package due to issues https://github.com/ros-visualization/qt_gui_core/issues/212:
    - [Apply patch](#patches) Apply patch for ros2 to avoid setting LD_LIBRARY_PATH environment variable to the dynamic libs paths
    - 


- **build_and_install_ros2_pkgs.py**: 
    
    Build ros2 foxy package inside **ros2_ws** which is created by `build_and_install_ros2_pkgs.py` and copy lib and header files to UnrealEngine project folder. This is mainly used to add/update new msgs to UnrealEngine project.

    This script will get source listed in **ros2_additional_pkgs.repos** and build pkgs listed in top of the script or given arg.

    You need to follow CodeGen tutorial as well to use msg from UnrealEngine.

## CodeGen
Python script to generate UE4 .h and .cpp files for UnrealEngine to interface with ROS2 messages.

\* Based on Jinja2 to generate msg

\* Ignores message types deprecated in Foxy.

### Usage

#### Generate source files
1. cd UE_tools/CodeGen
2. python3 gen_ue_from_ros.py --module <UE module name used in class/struct definition> --dependency <path to ros2 dependency pkgs> --target <names of target pkgs>

    e.g.

    `python3 gen_ue_from_ros.py`

    \* default dependency and target pkgs are defined at top of gen_ue_from_ros.py

#### Copy source files to Unreal Project
1. cd UE_tools/CodeGen
2. python3 post_genrate.py --ue_proj_path <path to UnrealEngine project> 

    e.g.

    `python3 post_generate.py --ue_proj_path /home/user/turtlebot3-UE`



### Scripts
- **gen_ue_from_ros.py**: 

    Generate .h and cpp files for UnrealEngine project from msg/srv/action definitions. Generated class/struct can be used from UnrealEngine C++ and Blueprint. 
    
    All properties can be accessible from C++. Not all properties but only Blueprint compatible type member can be accessible from Blueprint.

    If your custom msg need other msg dependency, you need to specify that dependency from arg.

    \* Default dependencies and targets are defined near the top of files.


    \* Please check [limitations](#limitation) as well.

- **post_generate.py**: 

    Copy generated .h and cpp to target UnrealEngine project folder such as **turtlebot3-UE/Plugin/rclUE/Source/Thirdparty/ros**. 

    \* Black list is defined near the beginning of the script which are not copied to Unreal project since there are [Limitations](#limitation)

### Limitation
- only works with ROS2 message interface (in particular, ROS had built-in data types, such as `time`, defined in libraries and ROS2 now implements those as messages)
- currently it has only been tested with messages used in RR projects
- not all types are supported in UE4 Blueprint (e.g. `double`): `get_types_cpp` does the check, however it is currently checking against a list of unsupported types that have been encountered (and there's more that are not checked against, so if the code fails compilation due to this problem, the type in question should be currently be added to the list). The alternative, and better implementation, would check for supported types (but must be careful with various aliases, like `int` and `int32`
- fixed size array comes with TArray<>. User should reserve array with proper size by themselves.

### Todo
- use object oriented python
- the script iterates multiple times over the files - this can be avoided if performance is a real issue (messages shouldn't change often however, so clarity should be prioritized over performance
- add automated testing: minimum should be to include all of the generated files and try to compile
- Use TStaticArray instead of TArray for fixed size array.

### Maintainer
yu.okamoto@rapyuta-robotics.com
