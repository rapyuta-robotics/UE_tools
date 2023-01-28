#!/usr/bin/env python3

import os
import docker
import uuid
from build_install_codegen import args_setup, load_from_configs

DOCKER_IMAGE = 'yuokamoto1988/ue_ros2_base'

def create_dir_mount(dir=os.getcwd(), target='', exception=[]):
    volumes = []
    files = os.listdir(dir)
    for f in files:
        if f in exception:
            continue
        else:
            volumes.append(os.path.join(dir, f) + ':' + os.path.join(target, f))
    return volumes

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

    # common params
    user = 'admin'
    cur_dir = os.getcwd()
    home = os.environ['HOME']
    docker_hoeme_dir = '/home/' +  user

    # initialization of command and volumes for docker
    volumes = [projectPath + ':' + docker_hoeme_dir + '/' + os.path.basename(projectPath)]
    command = 'python3 build_install_codegen.py '
    
    # pass arg to command inside docker.
    arg_dict = vars(args)
    for arg in arg_dict:
        if arg in ['ros_ws', 'config', 'pull_inside_docker']: #skip some args
            continue
        arg_value = arg_dict[arg]
        if type(arg_value) == type(True):
            if arg_value:
                command += ' --' + arg
        elif arg_value is not None :
            command += ' --' + arg + ' ' + str(arg_value)

    # mount UE_tools except for ros2_ws
    volumes.extend(create_dir_mount(dir=cur_dir, target=docker_hoeme_dir + '/UE_tools', exception=['ros2_ws', 'tmp']))

    # handle additional repos
    command += ' --skip_pull '
    if args.build:
        if not args.pull_inside_docker:
            if not os.path.exists('tmp'):
                os.makedirs('tmp')
            cmd = 'vcs import --repos --debug ' + 'tmp' + ' < ' + os.path.join(home, repos)
            volumes.extend(create_dir_mount(os.path.join(cur_dir, 'tmp'), docker_hoeme_dir + '/UE_tools/ros2_ws/src/pkgs'))
        elif repos:
            volumes.append(os.path.join(os.environ['HOME'], repos) + ':' + docker_hoeme_dir + '/' + os.path.basename(repos))

    # mount config  
    for config_file in config_files:
        id = str(uuid.uuid4())
        target_path = docker_hoeme_dir + '/config_' + id + '.yaml'
        volumes.append(os.path.abspath(config_file) + ':' + target_path)
        command += ' --config ' + target_path
    

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
    print('mount volumes:', volumes)
    container = client.containers.run(
        DOCKER_IMAGE + ':' + args.rosdistro, 
        'sleep infinity', 
        name=container_name, 
        volumes=volumes,
        detach=True)

    if args.build and repos and args.pull_inside_docker:
        pull_cmd = '/bin/bash -c "vcs import --repos --debug ' + \
            docker_hoeme_dir + '/UE_tools/ros2_ws/src/pkgs' +  ' < ' + \
            docker_hoeme_dir + '/' + os.path.basename(repos) + '"'
        print('Pull repo inside container with ' + pull_cmd)
        exec_run_with_log(container, pull_cmd)

    # execute command
    print('Execute command in conatainer: ' + command)
    exec_run_with_log(container, command)