#!/usr/bin/env python3

import sys
import os
import shutil
import argparse
import yaml
from contextlib import contextmanager

WS_PATH = os.path.join(os.getcwd(), 'BuildROS2/ros2_ws')
SRC_PATH = os.path.join(WS_PATH, 'src')
ADDITIONAL_PKG_PATH = os.path.join(WS_PATH, 'src/pkgs')

@contextmanager
def managed_chdir(path):
    prev_path = os.getcwd()
    os.chdir(path)
    try:
        yield 
    finally:
        os.chdir(prev_path)

def load_from_configs(file_names, remove = True):

    # overwritten params
    dependency = {}
    name_mapping = {}

    # get default values    
    with managed_chdir('CodeGen'):
        os.system('pwd')
        sys.path.append(os.getcwd())
        import CodeGen.gen_ue_from_ros as cg
        import CodeGen.post_generate as pg

        dependency = cg.DEFAULT_DEPENDENCY_PKGS
        name_mapping = cg.DEFAULT_NAME_MAPPING
        black_list = pg.DEFAULT_BLACK_LIST

    for file in file_names:
        UEPath, projectPath, pluginName, \
            pluginFolderName, targetThirdpartyFolderName, \
                target, black_list, dependency, name_mapping, repos = load_from_config(file, dependency, name_mapping)
    
    # cleanup
    if remove:
        if os.path.exists(ADDITIONAL_PKG_PATH):
            shutil.rmtree(ADDITIONAL_PKG_PATH)

    # pull
    home = os.environ['HOME']
    if repos:
        if not os.path.exists(ADDITIONAL_PKG_PATH):
            os.makedirs(ADDITIONAL_PKG_PATH)
        os.system('vcs import --repos --debug ' + ADDITIONAL_PKG_PATH + ' < ' + os.path.join(home, repos))

    return UEPath, projectPath, pluginName, \
        pluginFolderName, targetThirdpartyFolderName, \
            target, black_list, dependency, name_mapping

def load_from_config(file_name, dependency, name_mapping):
    try:
        with open(file_name) as file:
            config = yaml.safe_load(file)

    except:
        print('failed to open ' + file_name)
        sys.exit(0)

    home = os.environ['HOME']
    if 'args' in config:
        if  'ue_path' in config['args'] and \
            'ue_proj_path' in config['args'] and \
            'ue_plugin_name' in config['args'] and \
            'ue_target_3rd_name' in config['args']:
            UEPath = os.path.join(home, config['args']['ue_path'])
            projectPath = os.path.join(home, config['args']['ue_proj_path'])
            pluginName = config['args']['ue_plugin_name']
            pluginFolderName = config['args']['ue_plugin_folder_name'] \
                if 'ue_plugin_folder_name'  in config['args'] else pluginName
            targetThirdpartyFolderName = config['args']['ue_target_3rd_name'] \
                if 'ue_target_3rd_name' in config['args'] else 'ros'

        else:
            print('ue_proj_path and ue_plugin_name must be in config')
            sys.exit(0)
    else:
        print('args must be in config')
        sys.exit(0)
    
    repos = config['repos'] if 'repos' in config else None
    
    # target
    if 'target_pkgs' in config:
        if isinstance(config['target_pkgs'], dict):
            target = config['target_pkgs']
        else:
            print('target_pkgs must be dictionary')
            sys.exit(0)
    else:
        print('target_pkgs must be in config')
        sys.exit(0)

    # blacklist
    black_list = []
    if 'black_list_msgs' in config:
        if isinstance(config['black_list_msgs'], list):
            black_list = config['black_list_msgs']
        else:
            print('black_list_misgs must be list')
            sys.exit(0)

    # dependency
    if 'dependency' in config:
        dependency = config['dependency']
        if dependency == 'default':
            print('Use default dependency')
        elif dependency == 'target':
            print('Use target as a dependency')
            dependency = target
        elif isinstance(dependency, dict):
            pass
        else:
            print('dependency must be \'default\', \'target\' or dictionary')
    
    if 'dependency_append' in config:
        dependency_append = config['dependency_append']
        if isinstance(dependency_append, dict):
            dependency.update(dependency_append)
        else:
            print('dependency_append must be dictionary')
            sys.exit(0)

    # name mapping
    if 'name_mapping' in config:
        name_mapping = config['name_mapping']
        if isinstance(name_mapping, dict):
            pass
        else:
            print('name_mapping must be dictionary')
            sys.exit(0)
    
    if 'name_mapping_append' in config:
        name_mapping_append = config['name_mapping_append']
        if isinstance(name_mapping_append, dict):
            name_mapping.update(name_mapping_append)
        else:
            print('name_mapping_append must be dictionary')
            sys.exit(0)
    
    return UEPath, projectPath, pluginName, \
        pluginFolderName, targetThirdpartyFolderName, \
            target, black_list, dependency, name_mapping, repos



if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Build ros2 from source with necessasary patches to be used with UnrealEngine. And copy lib and header files under Unreal Project folder."
    )

    parser.add_argument(
        '--type', 
        choices=['base', 'pkgs'],
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
        '-i',
        '--install', 
        help='Install ros2 lib to UE project in yaml.',
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
        nargs='*',
        help='config files path'
    )
    parser.add_argument(
        '--remove', 
        help='Delete source before pull. Valid only with type==pkgs',
        action='store_true'
    )
    parser.add_argument(
        '--rosdistro', 
        choices=['foxy', 'humble'],
        default='humble'
    )

    args = parser.parse_args()

    config_files = ['default_config.yaml']
    if args.config is not None:
        config_files.extend(args.config)

    UEPath, projectPath, pluginName, \
        pluginFolderName, targetThirdpartyFolderName, \
        target, black_list, dependency, name_mapping = load_from_configs(config_files, args.remove and args.type == 'pkgs')

    # build lib and copy to ue project
    if args.build or args.install:
        with managed_chdir('BuildROS2'):
            os.system('pwd')
            sys.path.append(os.getcwd())
            from BuildROS2.build_and_install_ros2 import build_ros2, install_ros2
            from BuildROS2.build_and_install_ros2_base import DEFAULT_NOT_ALLOWED_SPACES, DEFAULT_ALLOWED_SPACES
            if args.type == 'base':
                allowed_spaces = DEFAULT_ALLOWED_SPACES
                not_allowed_spaces = DEFAULT_NOT_ALLOWED_SPACES
                pkgs = []
            elif args.type == 'pkgs':
                allowed_spaces = list(target.keys())
                not_allowed_spaces = []
                pkgs = list(target.keys())

            if args.build:    
                build_ros2(
                    buildType = args.type,
                    allowed_spaces = allowed_spaces,
                    pkgs = pkgs,
                    remove = args.remove,
                    rosdistro = args.rosdistro
                )
            if args.install:
                install_ros2(
                    projectPath = projectPath,
                    pluginName = pluginName,
                    pluginFolderName = pluginFolderName,
                    targetThirdpartyFolderName = targetThirdpartyFolderName,
                    buildType = args.type,
                    allowed_spaces = allowed_spaces,
                    not_allowed_spaces = not_allowed_spaces,
                    remove = args.remove,
                )

    # codegen
    if args.type == 'pkgs' and args.codegen:
        with managed_chdir('CodeGen'):
            os.system('pwd')
            sys.path.append(os.getcwd())
            import CodeGen.gen_ue_from_ros as cg
            import CodeGen.post_generate as pg

            # generate cpp and h codes
            cg.codegen(
                module = pluginName,
                dependency = dependency,
                target = target,
                name_mapping = name_mapping
            )
            
            # post generate. copy generated code to ue project
            pg.copy_ros_to_ue(
                ue_project_path = projectPath, 
                ue_plugin_name = pluginName, 
                ue_plugin_folder_name = pluginFolderName, 
                black_list = black_list,
                remove = args.remove
            )