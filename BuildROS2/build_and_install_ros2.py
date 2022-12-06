#!/usr/bin/env python3

import os, time
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
    remove = True,
    rosdistro = 'foxy'
):
    start = time.time()
    
    buildRosScript =  os.path.join(os.getcwd(), 'setup_ros2_' + buildType + '.sh')

    # Assume pluginFolderName is same as PluginName if it is empty.
    if pluginFolderName == '':
        pluginFolderName = pluginName

    # UE paths
    pluginPath =  os.path.join(projectPath, 'Plugins', pluginFolderName)
    pluginPathBinaries = os.path.join(pluginPath, 'Binaries')
    pluginPathRos =  os.path.join(pluginPath, 'ThirdParty', targetThirdpartyFolderName)
    pluginPathRosInclude =  os.path.join(pluginPathRos, 'include')
    pluginPathRosLib =  os.path.join(pluginPathRos, 'lib')
    pluginPathBuildCS =  os.path.join( pluginPath, 'Source', pluginName, pluginName + '.Build.cs')
    projectPathBinaries =  os.path.join(projectPath, 'Binaries' )
    infoRosOutput =  os.path.join(pluginPath, 'Scripts/info_ros')

    # ros paths
    ros =  os.path.join(os.getcwd(), 'ros2_ws')
    rosInstall  = os.path.join(ros, 'install')

    allowed_spaces.extend(pkgs)

    if remove:
        print('Cleanup workspace')
        shutil.rmtree(ros)


    print('Building ros ' + buildType + '...')
    os.system('chmod +x ' + buildRosScript)
    os.system('bash ' + buildRosScript + ' ' + ros + ' ' + rosdistro + ' ' +  ' "' + ' '.join(pkgs) + '"')

    if remove:
        if os.path.exists(pluginPathRosInclude):
            shutil.rmtree(pluginPathRosInclude)
        if os.path.exists(pluginPathRosLib):
            shutil.rmtree(pluginPathRosLib)

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

    RenameLibsWithVersion(pluginPathRosLib, projectPath)
    SetRPATH(pluginPathRosLib)
    InvalidateBinaries(projectPathBinaries, pluginPathBinaries, pluginPathBuildCS)

    # You also can try this:
    # CreateInfoForAll('objdump -x', pluginPathRosLib, infoRosOutput) # see also 'ldd'
    # CheckLibs(pluginPathRosLib)
    print('Done. Time:', '{:.2f}'.format(time.time() - start), '[s]')

if __name__ == '__main__':
    print("Please use build_ros function from other wrapper.")

