# Copyright 2021-2022 Rapyuta Robotics Co., Ltd.
import argparse
import os
import shutil
import glob

# default dependency pkgs. Commonly used pkgs
# https://github.com/ros2/common_interfaces +  alpha
# BASE_ROS_INSTALL_PATH = '/opt/ros/foxy/'
BASE_ROS_INSTALL_PATH = os.path.join(os.getcwd(), '../BuildROS2/ros2_ws/install')
DEFAULT_DEPENDENCY_PKGS = [
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

# temporary black list msgs which can't be parsed properly
BLACK_LIST = [
    "ROS2WStringMsg", # can't handle wstring in UE.
    
    # array parser issue
    "ROS2CancelGoalSrv",
    "ROS2MeshMsg",
    "ROS2SolidPrimitiveMsg" 
    
    "ROS2TFMessageMsg", # memcpy/free issues. fixed version in rclUE but can't autogenerate.
]

def check_blacklist(file_name, black_list=BLACK_LIST):
    for b in black_list:
        if b in file_name:
            return True
    return False

def copy_ros_to_ue(ue_project_path, ue_plugin_name, ue_plugin_folder_name, ue_target_3rd_name, ue_target_ros_wrapper_path):

    ue_target_src_path = os.path.join(ue_project_path, 'Plugins', ue_plugin_folder_name, 'Source')
    ue_target_3rd_path = os.path.join(ue_project_path, 'Plugins', ue_plugin_folder_name, 'Source', 'ThirdParty', ue_target_3rd_name)
    ue_public_path = os.path.join(ue_target_src_path, ue_plugin_name, 'Public', ue_target_ros_wrapper_path)
    ue_private_path = os.path.join(ue_target_src_path, ue_plugin_name, 'Private', ue_target_ros_wrapper_path)
    
    # Copy UE wrapper of ros src
    current_dir = os.getcwd()
    for type_name in ['Action','Srv','Msg']:
        for file_name in glob.glob(f'*{type_name}.h'):
            if check_blacklist(file_name, BLACK_LIST):
                continue
            shutil.copy(os.path.join(current_dir, file_name), os.path.join(ue_public_path, f'{type_name}s'))
        for file_name in glob.glob(f'*{type_name}.cpp'):
            if check_blacklist(file_name, BLACK_LIST):
                continue
            shutil.copy(os.path.join(current_dir, file_name), os.path.join(ue_private_path, f'{type_name}s'))
    
    return 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Copy ros package's include + lib from installation folder to target UE plugin's ThirdParty folder"
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
        default='rclUE'
    )
    parser.add_argument(
        "--ue_target_3rd_name",
        help="Target 3rd name under ThirdParty, eg: ros",
        default='ros'
    )
    parser.add_argument(
        "--ue_target_ros_wrapper_path",
        help="Target ros wrapper relative folder path under Source's Private/Public, eg: ROS2",
        default=''
    )
    args = parser.parse_args()
    
    copy_ros_to_ue(
        # args.ros_install_path, 
        # args.ros_pkgs,           
        args.ue_proj_path, 
        args.ue_plugin_name, 
        args.ue_plugin_folder_name,
        args.ue_target_3rd_name, 
        args.ue_target_ros_wrapper_path
    )
    
