#!/usr/bin/env python3

import sys
import os
import argparse
import yaml
from contextlib import contextmanager

@contextmanager
def managed_chdir(path):
    prev_path = os.getcwd()
    os.chdir(path)
    try:
        yield 
    finally:
        os.chdir(prev_path)
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Build ros2 from source with necessasary patches to be used with UnrealEngine. And copy lib and header files under Unreal Project folder."
    )

    parser.add_argument(
        '--type', 
        help='base: build base ros2 libs. pkgs: build given ros2 pkgs',
        default='pkgs'
    )

    parser.add_argument(
        '-b',
        '--build', 
        help='Build ros2 pkgs in yaml.',
        action='store_true'
    )
    parser.add_argument(
        '-c',
        '--codegen', 
        help='Generate UE codes from pkgs',
        action='store_true'
    )
    parser.add_argument(
        '--config', 
        help='config file path'
    )

    args = parser.parse_args()
    if args.config is None:
        config_file = 'default_config.yaml'
    else:
        config_file = args.config

    # open config

    try:
        with open(config_file) as file:
            config = yaml.safe_load(file)

    except:
        print('failed to open ' + config_file)
        sys.exit(1)

    home = os.environ['HOME']
    projectPath = os.path.join(home, config['args']['ue_proj_path'])
    pluginName = config['args']['ue_plugin_name']
    pluginFolderName = config['args']['ue_plugin_folder_name']
    ros_pkgs = config['target_pkgs']

    # build lib and copy to ue project
    if args.build:
        with managed_chdir('BuildROS2'):
            os.system('pwd')
            sys.path.append(os.getcwd())
            from BuildROS2.build_and_install_ros2 import build_ros2
            from BuildROS2.build_and_install_ros2_base import DEFAULT_NOT_ALLOWED_SPACES, DEFAULT_ALLOWED_SPACES
                        
            if args.type == 'base':
                allowed_spaces = DEFAULT_ALLOWED_SPACES
                not_allowed_spaces = DEFAULT_NOT_ALLOWED_SPACES
                pkgs = ['ue_msgs']
            elif args.type == 'pkgs':
                allowed_spaces = ros_pkgs
                not_allowed_spaces = []
                pkgs = ros_pkgs
            
            build_ros2(
                UEPath = os.path.join(home, config['args']['ue_path']),
                projectPath = projectPath,
                pluginName = pluginName,
                pluginFolderName = pluginFolderName,
                targetThirdpartyFolderName = config['args']['ue_target_3rd_name'],
                buildType = args.type,
                allowed_spaces = allowed_spaces,
                not_allowed_spaces = not_allowed_spaces,
                pkgs = pkgs
            )

    # codegen
    if args.type == 'pkgs' and args.codegen:
        with managed_chdir('CodeGen'):
            os.system('pwd')
            sys.path.append(os.getcwd())
            import CodeGen.gen_ue_from_ros as cg
            import CodeGen.post_generate as pg
            
            ue_target_ros_wrapper_path = config['args']['ue_target_ros_wrapper_path']
            
            # generate cpp and h codes
            cg.codegen(
                module = pluginName,
                dependency = [],
                target = ros_pkgs,
                ue_target_ros_wrapper_path = ue_target_ros_wrapper_path
            )
            
            # post generate. copy generated code to ue project
            pg.copy_ros_to_ue(
                ue_project_path = projectPath, 
                ue_plugin_name = pluginName, 
                ue_plugin_folder_name = pluginFolderName, 
                ue_target_ros_wrapper_path = ue_target_ros_wrapper_path,
                black_list = config['black_list_msgs']
            )