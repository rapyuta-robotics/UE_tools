#!/usr/bin/env python3

import argparse

from build_and_install_ros2 import build_ros2, install_ros2

DEFAULT_PKGS = [
    'action_msgs',
    'actionlib_msgs',
    'builtin_interfaces',
    'unique_identifier_msgs',
    'diagnostic_msgs',
    'rosgraph_msgs',
    'geometry_msgs',
    'nav_msgs',
    'sensor_msgs',
    'shape_msgs',
    'std_msgs',
    'std_srvs',
    'stereo_msgs',
    'trajectory_msgs',
    'visualization_msgs',
    'tf2_msgs',
    'pcl_msgs',
    # 'ackermann_msgs',
    'example_interfaces',
    'ue_msgs'
]
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Build ros2 from source with necessasary patches to be used with UnrealEngine. And copy lib and header files under Unreal Project folder."
    )
    parser.add_argument(
        "--ue_path",
        help="Path to UE",
        required=True
    )
    parser.add_argument(
        "--ue_proj_path",
        help="Path to target UE project",
        required=True
    )
    parser.add_argument(
        "--ue_plugin_name",
        help="UE plugin module name, eg: rclUE",
        default='rclUE'
    )
    parser.add_argument(
        "--ue_plugin_folder_name",
        help="UE plugin folder name, eg: rclUE",
        default=''
    )
    parser.add_argument(
        "--ue_target_3rd_name",
        help="Target 3rd name under ThirdParty, eg: ros",
        default='ros'
    )
    parser.add_argument(
        "--ros_pkgs",
        help="ROS package name, eg: geometry_msgs",
        nargs='*',
        default=DEFAULT_PKGS
    )
    args = parser.parse_args()

    ue_plugin_folder_name = args.ue_plugin_folder_name
    if ue_plugin_folder_name == '':
        ue_plugin_folder_name = args.ue_plugin_name

    build_ros2(
        buildType = 'pkgs',
        allowed_spaces = args.ros_pkgs,
        pkgs = args.ros_pkgs
    )
    install_ros2(
        projectPath = args.ue_proj_path,
        pluginName = args.ue_plugin_name,
        pluginFolderName = ue_plugin_folder_name,
        targetThirdpartyFolderName = args.ue_target_3rd_name,
        buildType = 'pkgs',
        allowed_spaces = args.ros_pkgs,
        not_allowed_spaces = [],
    )