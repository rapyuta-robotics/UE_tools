#!/usr/bin/env python3
'''
How to update ros:

- Install 'ros2' (foxy) (until section 'Build the code in the workspace') https://docs.ros.org/en/foxy/Installation/Ubuntu-Development-Setup.html
- Reinstall python package due to issues https://github.com/ros-visualization/qt_gui_core/issues/212:
sudo apt remove shiboken2 libshiboken2-dev libshiboken2-py3-5.14
pip3 install --user shiboken2
- Make replacement for ros2 to avoid LD_LIBRARY_PATH dependency issue:
src/ros2/rcpputils/src/find_library.cpp:
in function find_library_path():
---//return "";
+++return "lib" + library_name + ".so";
- Clone 'rclc' package (which is not a part of official ros2), branch 'foxy' https://github.com/ros2/rclc/tree/foxy
- Clone 'ue_msgs' (RR project) https://github.com/rapyuta-robotics/UE_msgs
- Run this script with providing main path arguments, for example:
python3 update_ros.py /home/vilkun/UE/UnrealEngine /home/vilkun/ros2_foxy /home/vilkun/work/build_foxy/rclc /home/vilkun/work/build_foxy/UE_msgs /home/vilkun/work/turtlebot3-UE

Notes:
- 304 packages finished, 1 'rviz_ogre_vendor' error, 6 packages not processed at the end of the ros-foxy build - is okay. Also 1 'Failed to find ROS1', and several 'connext' errors, and 'rviz' errors during 'local_setup.bash' - are okay too.
- we rename SONAME of libs with version by 'patchelf' since UE4.27 can't deal with that in LinuxToolChain.cs, see more in RenameLibsWithVersion().
- script uses project path (which includes this plugin) just to invalidate binaries, and forces IDE to clean cache and link them again.
'''

import os, sys, shutil, re, time, subprocess
from libs_utils import *

def build_ros2(
    UEPath,
    projectPath,
    pluginName,
    pluginFolderName, #pluginFolderName is not always same as pluginName
    targetThirdpartyFolderName,
    buildType,
    allowed_spaces = [],
    not_allowed_spaces = [],
    pkgs = [],
):
    start = time.time()

    buildRosScript =  os.path.join(os.getcwd(), 'setup_ros2_' + buildType + '.sh')

    # Assume pluginFolderName is same as PluginName if it is empty.
    if pluginFolderName == '':
        pluginFolderName = pluginName

    # UE paths
    pluginPath =  os.path.join(projectPath, 'Plugins', pluginFolderName)
    pluginPathBinaries = os.path.join(pluginPath, 'Binaries')
    pluginPathRos =  os.path.join(pluginPath, 'Source/ThirdParty', targetThirdpartyFolderName)
    pluginPathRosInclude =  os.path.join(pluginPathRos, 'include')
    pluginPathRosLib =  os.path.join(pluginPathRos, 'lib')
    pluginPathBuildCS =  os.path.join( pluginPath, 'Source', pluginName, pluginName + '.Build.cs')
    projectPathBinaries =  os.path.join(projectPath, 'Binaries' )
    infoRosOutput =  os.path.join(pluginPath, 'Scripts/info_ros')

    # ros paths
    ros =  os.path.join(os.getcwd(), 'ros2_ws')
    rosInstall  = os.path.join(ros, 'install')

    allowed_spaces.extend(pkgs)
    
    print('Building ros ' + buildType + '...')
    os.system('chmod +x ' + buildRosScript)
    os.system('bash ' + buildRosScript + ' ' + UEPath + ' "' + ' '.join(pkgs) + '"')

    os.makedirs(pluginPathRosInclude, exist_ok=True)
    os.makedirs(pluginPathRosLib, exist_ok=True)

    print('Grabbing includes...')
    GrabIncludes(rosInstall, pluginPathRosInclude, allowed_spaces)
    CleanIncludes(pluginPathRosInclude, not_allowed_spaces)

    if buildType == 'base':
        print('Applying includes patch...')
        os.system('cd ' + pluginPath + '; git apply ' + 
                    os.path.join(os.getcwd(), 'patches/rcutils.patch'))

    print('Grabbing libs...')
    GrabLibs(rosInstall, pluginPathRosLib, allowed_spaces)
    CleanLibs(pluginPathRosLib, not_allowed_spaces)

    RenameLibsWithVersion(pluginPathRosLib)
    SetRPATH(pluginPathRosLib)
    InvalidateBinaries(projectPathBinaries, pluginPathBinaries, pluginPathBuildCS)

    # You also can try this:
    # CreateInfoForAll('objdump -x', pluginPathRosLib, infoRosOutput) # see also 'ldd'
    # CheckLibs(pluginPathRosLib)
    print('Done. Time:', '{:.2f}'.format(time.time() - start), '[s]')

if __name__ == '__main__':
    print("Please use build_ros function from other wrapper.")

