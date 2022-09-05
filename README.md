UE_tools
==========

# Overview

## ROS2 Lib update

[rclUE](https://github.com/rapyuta-robotics/rclUE) has ros2 lib and header files to use ROS2 core 
    functionality from UnrealEngine. 
    
If you want to update ros2 lib in rclUE, need to follow [Build core lib](#build-core-lib) which build libs and copy lib and header files under rclUE.

## Interface update

Commonly used interfaces are inside rclUE, but sometime you want to use your custom msg from UnrealEngine.

To use new msg in UnrealEngine Project,

1. [Build msg lib](#build-msg-lib) :build msg lib with patches
2. [Generate source files](#generate-source-files) :generate .h and .cpp files which are used inside UnrealEngine
3. [Copy source files to Unreal Project](#copy-source-files-to-unreal-project) :copy generated .h and .cpp files to UnrealEngine project.
4. Build your UnrealEngine project.
 

# Details

## BuiildROS2
Python scripts to build ros2 foxy pkgs from [source](https://docs.ros.org/en/foxy/Installation/Ubuntu-Development-Setup.html) with necessary changes to be used inside UnrealEngine project. Generated lib and header files are used inside UnrealEngine project, mainly by [rclUE](https://github.com/rapyuta-robotics/rclUE).

### Patches
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
    
    All properties can be accessible from C++. Not all properties but only Blueprint comaptible type member can be accesible from  Blueprint.

    If your custom msg need other msg dependency, you need to specify that dependnecy from arg.

    \* Default dependencies and targets are defined near the top of files.


    \* Please check [limitiations](#limitation) as well.

- **post_generate.py**: 

    Copy generated .h and cpp to target UnrealEngine project folder such as **turtlebot3-UE/Plugin/rclUE/Source/Thirdparty/ros**. 

    \* Black list is defined near the beginning of the script which are not copied to Unreal project since there are [Limitations](#limitation)

### Limitation
- only works with ROS2 message interface (in particular, ROS had built-in data types, such as `time`, defined in libraries and ROS2 now implements those as messages)
- code generation for nested arrays in messages is not supported
- currently it has only been tested with messages used in RR projects
- not all types are supported in UE4 Blueprint (e.g. `double`): `get_types_cpp` does the check, however it is currently checking against a list of unsupported types that have been encountered (and there's more that are not checked against, so if the code fails compilation due to this problem, the type in question should be currently be added to the list). The alternative, and better implementation, would check for supported types (but must be careful with various aliases, like `int` and `int32`
- fixed size array comes with TArray<>. User should researve array with proper size by themselves.

### Todo
- use object oriented python
- the script iterates multiple times over the files - this can be avoided if performance is a real issue (messages shouldn't change often however, so clarity should be prioritized over performance
- add automated testing: minimum should be to include all of the generated files and try to compile
- Use TStaticArray instead of TArray for fixed size array.

### Maintainer
yu.okamoto@rapyuta-robotics.com
