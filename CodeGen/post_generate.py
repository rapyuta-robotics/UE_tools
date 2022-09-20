# Copyright 2021-2022 Rapyuta Robotics Co., Ltd.
import argparse
import os
import shutil
import glob

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

def copy_files(target_path, type_name, extension, black_list):
    current_dir = os.getcwd()
    target_path = os.path.join(target_path, f'{type_name}s')
    os.makedirs(target_path, exist_ok=True)
    print('Copy generated files to ' + target_path)
    for file_name in glob.glob(f'*{type_name}{extension}'):
        if check_blacklist(file_name, black_list):
            print(' *' + file_name + ' is in BLACK_LIST and not copied.')
            continue
        shutil.copy(os.path.join(current_dir, file_name), target_path)
        print(' Copied ' + file_name)

def copy_ros_to_ue(ue_project_path, ue_plugin_name, ue_plugin_folder_name, ue_target_ros_wrapper_path, black_list=BLACK_LIST):

    ue_target_src_path = os.path.join(ue_project_path, 'Plugins', ue_plugin_folder_name, 'Source')
    ue_public_path = os.path.join(ue_target_src_path, ue_plugin_name, 'Public', ue_target_ros_wrapper_path)
    ue_private_path = os.path.join(ue_target_src_path, ue_plugin_name, 'Private', ue_target_ros_wrapper_path)
    
    # Copy UE wrapper of ros src
    for type_name in ['Action','Srv','Msg']:
        copy_files(ue_public_path, type_name, '.h', black_list)
        copy_files(ue_private_path, type_name,'.cpp', black_list)
        
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
        "--ue_target_ros_wrapper_path",
        help="Target ros wrapper relative folder path under Source's Private/Public, eg: ROS2",
        default=''
    )
    args = parser.parse_args()
    
    copy_ros_to_ue(      
        args.ue_proj_path, 
        args.ue_plugin_name, 
        args.ue_plugin_folder_name,
        args.ue_target_ros_wrapper_path,
        BLACK_LIST
    )
    
