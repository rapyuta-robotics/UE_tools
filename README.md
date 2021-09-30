# UE_tools

usage:

`python3 CodeGeneratorFromPath.py <ros2-base-share-path> [<custom-message-path>]`

`ros2-base-share-path` is used to find base definition of types
`custom-message-path` is the path of messages that need to be generated (multiple are allowed)

e.g. `python3 CodeGeneratorFromPath.py /opt/ros/foxy/share/ /opt/ros/foxy/share/geometry_msgs/` generates `geometry_msgs` using definitions in `/opt/ros/foxy/share/` and `/opt/ros/foxy/share/geometry_msgs/`
