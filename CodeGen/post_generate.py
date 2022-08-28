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
    # 'stereo_msgs',
    # 'trajectory_msgs',
    'visualization_msgs',
    'tf2_msgs',
    # 'pcl_msgs',
    # 'ackermann_msgs',
    'example_interfaces',
    'ue_msgs'
]

# temporary black list msgs which can't be parsed properly
BLACK_LIST = [
    "ROS2WStringMsg",
    "ROS2CancelGoalSrv",
    "ROS2MeshMsg",
    "ROS2SolidPrimitiveMsg"
]

def check_blacklist(file_name, black_list=BLACK_LIST):
    for b in black_list:
        if b in file_name:
            return True
    return False

def copy_ros_to_ue(
    # ros_install_path, ros_pkgs,
    ue_project_path, ue_plugin_name, ue_plugin_folder_name, ue_target_3rd_name, ue_target_ros_wrapper_path):

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

    # legacy code to cpy lib and include 
    # Copy ROS pkg' include & lib (generated by `colcon build`)
    for ros_pkg_name in ros_pkgs:
        if 'share' not in ros_install_path.split('/'):
            ros_path = os.path.join(ros_install_path, ros_pkg_name)
        ros_include_path = os.path.join(ros_path, 'include', ros_pkg_name)
        ros_lib_path = os.path.join(ros_path, 'lib')
        print(f'COPY {ros_pkg_name} FROM')
        print(ros_include_path)
        print(ros_lib_path)
        
        ue_target_3rd_include_path = os.path.join(ue_target_3rd_path, 'include', ros_pkg_name)
        ue_target_3rd_lib_path = os.path.join(ue_target_3rd_path, 'lib', ros_pkg_name)
        os.makedirs(ue_target_3rd_include_path, exist_ok=True)
        os.makedirs(ue_target_3rd_lib_path, exist_ok=True)
        print('TO')
        print(ue_target_3rd_include_path)
        print(ue_target_3rd_lib_path)
        
        # include
        try:
            src = ros_include_path
            dst = ue_target_3rd_include_path
            if os.path.exists(src):
                shutil.rmtree(dst)
                shutil.copytree(src, dst)
        except OSError as e:
            print(e)
            exit(0)
        
        # lib
        for file_name in glob.glob(os.path.join(ros_lib_path, f'lib{ros_pkg_name}__*.so')):
            shutil.copy(file_name, ue_target_3rd_lib_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Copy ros package's include + lib from installation folder to target UE plugin's ThirdParty folder"
    )
    # parser.add_argument(
    #     "--ros_install_path",
    #     help="Path to ros installation. eg: /opt/ros/foxy or colcon_ws/install",
    #     default=BASE_ROS_INSTALL_PATH
    # )
    # parser.add_argument(
    #     "--ros_pkgs",
    #     help="ROS package name, eg: geometry_msgs",
    #     nargs='*',
    #     default=DEFAULT_DEPENDENCY_PKGS
    # )
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
    
