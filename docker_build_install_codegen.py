#!/usr/bin/env python3

import sys
import os
import shutil
import argparse
import yaml
import docker
import uuid
from build_install_codegen import args_setup, load_from_configs

def exec_run_with_log(container, command):
    _, stream = container.exec_run(command, stream=True)
    for data in stream:
        print(data.decode())        

if __name__ == '__main__':

    parser = args_setup()
    parser.add_argument(
        '--pull_inside_docker', 
        help='pull additonal repos inside docker or outside docker and mount',
        action='store_true'
    )
    args = parser.parse_args()

    config_files = ['default_config.yaml']
    if args.config is not None:
        config_files.extend(args.config)

    UEPath, projectPath, pluginName, \
        pluginFolderName, targetThirdpartyFolderName, \
        target, black_list, dependency, name_mapping, repos = load_from_configs(config_files, args.ros_ws, False, False)

    user = 'admin'
    volumes = [projectPath + ':/home/' + user + '/' + os.path.basename(projectPath)]
    # todo pass all args except for pull_inside_docker and config
    command = 'python3 build_install_codegen.py --type ' + args.type + ' --rosdistro ' + args.rosdistro
    
    # handle repos
    if not args.pull_inside_docker:
        command += ' --skip_pull '
        # todo vcs import outside and mount
    elif repos:
        volumes.append(os.path.join(os.environ['HOME'], repos) + ':/home/' + user + '/' + repos)

    # mount config and repos    
    for config_file in config_files:
        id = str(uuid.uuid4())
        target_path = '/home/' + user + '/config_' + id + '.yaml'
        volumes.append(os.path.abspath(config_file) + ':' + target_path)
        command += ' --config ' + target_path
    
    # build, install and codegen
    if args.build:
        command += ' --build '

    if args.install:
        command += ' --install '

    if args.type == 'pkgs' and args.codegen:
        command += ' --codegen '

    # create containers
    client = docker.from_env()
    container_name = 'ue_ros2_base'
    try: #if docker exists, remove
        c = client.containers.get(container_name)
        c.stop()
        c.remove()
    except:
        pass

    print('Run docker conatiner named:' + container_name)
    container = client.containers.run(
        'yuokamoto1988/ue_ros2_base:latest', 
        'sleep infinity', 
        name=container_name, 
        volumes=volumes,
        detach=True)

    # copy local UE_tools to docker
    cur_dir = os.getcwd()
    files = os.listdir()
    print('Copy local UE_tools to docker')
    for f in files:
        if f == 'ros2_ws':
            continue
        else:
            os.system('docker cp ' + os.path.join(cur_dir, f) + ' ' + container_name + ':/home/' + user + '/UE_tools/')

    exec_run_with_log(container, "/bin/bash -c \"find BuildROS2 -type f | xargs sed -i 's/sudo //g'\"")

    # execute command
    print('execute command in conatainer: ' + command)
    exec_run_with_log(container, command)