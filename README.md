# UE_tools

## CodeGen
Python script to generate UE4 classes to interface with ROS2 messages.

### Usage
`python3 CodeGeneratorFromPath.py <ros2-base-share-path> [<custom-message-path>]`

`ros2-base-share-path` is used to find base definition of types
`custom-message-path` is the path of messages that need to be generated (multiple are allowed)

e.g. `python3 CodeGeneratorFromPath.py /opt/ros/foxy/share/ /opt/ros/foxy/share/geometry_msgs/` generates `geometry_msgs` using definitions in `/opt/ros/foxy/share/` and `/opt/ros/foxy/share/geometry_msgs/`


### Limitation
- only works with ROS2 message interface (in particular, ROS had built-in data types, such as `time`, defined in libraries and ROS2 now implements those as messages)
- code generation for nested arrays in messages is not supported
