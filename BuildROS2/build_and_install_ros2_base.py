#!/usr/bin/env python3

import argparse

from build_and_install_ros2 import build_ros2

DEFAULT_ALLOWED_SPACES = [ 
    'fastcdr', 
    'fastrtps', 
    'rcl', 
    'rcutils', 
    'rcpputils', 
    'rmw', 
    'rosidl', 
    'tracetools', 
    'ament'
    ]
DEFAULT_NOT_ALLOWED_SPACES = [ 
    '.so.', 
    'python', 
    'rclcpp', 
    'rclpy', 
    'rcl_logging_log4cxx', 
    'rcl_logging_noop', 
    'rclc_examples', 
    'rclc_parameter', 
    'connext', 
    'cyclonedds', 
    'action_tutorials', 
    'turtlesim', 
    'rmw_fastrtps_dynamic_cpp', 
    'rosidl_cmake', 
    'rosidl_default', 
    'rosidl_generator_cpp', 
    'rosidl_generator_dds_idl', 
    # 'rosidl_generator_py', 
    'rosidl_runtime_cpp', 
    'rosidl_runtime_py', 
    #msgs
    'action_msgs', 
    'unique_identifier_msgs' ,
    'builtin_interfaces', 
    'example_interfaces', 
    'actionlib_msgs', 
    'composition_interfaces', 
    'diagnostic_msgs', 
    'lifecycle_msgs', 
    'logging_demo', 
    'map_msgs', 
    'move_base_msgs', 
    'pendulum_msgs', 
    'shape_msgs', 
    'statistics_msgs', 
    'std_srvs', 
    'stereo_msgs', 
    'test_msgs', 
    'trajectory_msgs', 
    'visualization_msgs', 
    'geometry_msgs', 
    'nav_msgs', 
    'sensor_msgs', 
    'std_msgs', 
    'tf2_msgs', 
    'sensor_msgs_py', 
    'tf2_sensor_msgs', 
    'rosgraph_msgs', 
    'tracetools_', 
    'Codec_', 
    'Plugin_', 
    'RenderSystem_', 
    '_test_type_support'
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
    args = parser.parse_args()

    ue_plugin_folder_name = args.ue_plugin_folder_name
    if ue_plugin_folder_name == '':
        ue_plugin_folder_name = args.ue_plugin_name

    build_ros2(
        UEPath = args.ue_path,
        projectPath = args.ue_proj_path,
        pluginName = args.ue_plugin_name,
        pluginFolderName = ue_plugin_folder_name,
        targetThirdpartyFolderName = args.ue_target_3rd_name,
        buildType = 'base',
        allowed_spaces = DEFAULT_ALLOWED_SPACES,
        not_allowed_spaces = DEFAULT_NOT_ALLOWED_SPACES,
        pkgs = ['ue_msgs'],
    )
