import os, sys, shutil, re, glob
from subprocess import check_output

# this script forces to link libraries again on next IDE run
# (inside present a workaround for build.cs file, that's trick is to avoid deleting 'intermediate' folder at all)
def InvalidateBinaries(projectPathBinaries, rclUEBinaries, rclUEBuildCS):
    cwd = os.getcwd()

    if os.path.isdir(projectPathBinaries):
        print('Removing:', projectPathBinaries)
        shutil.rmtree(projectPathBinaries)

    if os.path.isdir(rclUEBinaries):
        print('Removing:', rclUEBinaries)
        shutil.rmtree(rclUEBinaries)

    if os.path.isfile(rclUEBuildCS):
        print('Invalidating:', rclUEBuildCS)
        content = ''

        with open(rclUEBuildCS, 'r') as f:
            content = f.read()

        # workaround with extra-new symbol, flip-flop with-without that symbol
        if content[-1] == '\n':
            content = content[:-1]
        else:
            content += '\n'

        with open(rclUEBuildCS, 'w') as f:
            f.write(content)

# To find lib dependencies check colcon command:
# colcon graph --packages-up-to rmw_cyclonedds_cpp --packages-above fastrtps
def FindLibsDependencies():
    pass

def GetLibs(folder):
    libs = list()

    for dirpath,subdirs,files in os.walk(folder):
        for file in files:
            if file.startswith('lib') and (file.endswith('.so') or '.so.' in file):
                fullName = os.path.join(dirpath, file)
                libs.append(fullName)
    
    return libs

# Runs command for every lib in the folder, creates folder with output 'txt' file for every lib 
# commandName:
# 'readelf -d'
# 'readelf -Wa'
# 'readelf -Ws'
# 'objdump -x'
# 'ld'
# 'ldd'
# 'nm --demangle'
def CreateInfoForAll(commandName, folderWithLibs, folderOut):
    if os.path.isdir(folderOut):
        shutil.rmtree(folderOut)

    os.mkdir(folderOut)

    for lib in GetLibs(folderWithLibs):
        head, tail = os.path.split(lib)
        command = commandName + ' ' + lib + ' > ' + folderOut + '/' + tail + '.txt' # ' |head -20 > '  ' |grep RPATH'
        os.system(command)

# we really need to be sure that we don't use libraries from 'build' or 'install' folders
# which are metntioned in 'RPATH', 'LD_LIBRARY_PATH', 'RUNPATH'  values
def RenameDir(dir, suffix):
    if os.path.isdir(dir):
        print('> rename', dir, dir + suffix)
        os.rename(dir, dir + suffix)
    
    return dir + suffix

def GrabLibs(folderFrom, folderTo, allowed_spaces):
    filesCount = 0

    for dirpath,subdirs,files in os.walk(folderFrom):
        for file in files:
           if file.startswith('lib') and (file.endswith('.so') or '.so.' in file) and \
                any(elem in file for elem in allowed_spaces):
                filesCount += 1
                fileFrom = os.path.join(dirpath, file)
                fileTo = folderTo + '/' + file
                shutil.copy(fileFrom, fileTo)

    print('Grabbed libs (' + folderFrom + '): ' + str(filesCount))

def GrabIncludes(folderFrom, folderTo, allowed_spaces):
    foldersCount = 0

    for elemName in os.listdir(folderFrom):
        dirPath = os.path.join(folderFrom, elemName)
        includeFolder = os.path.join(dirPath, 'include')
        
        if os.path.isdir(dirPath) and os.path.isdir(includeFolder) and \
            any(elem in elemName for elem in allowed_spaces):
            for subincludeElem in os.listdir(includeFolder):
                subincludePath = os.path.join(includeFolder, subincludeElem)

                if os.path.isdir(subincludePath):
                    folderToFull = os.path.join(folderTo, subincludeElem)
                    shutil.copytree(subincludePath, folderToFull, dirs_exist_ok=True)
                    foldersCount += 1

    print('Grabbed include folders (' + folderFrom + '): ' + str(foldersCount))

def CleanLibs(dir, not_allowed_spaces):
    removedCount = 0
    for dirpath,subdirs,files in os.walk(dir):
        for file in files:
            if any(elem in file for elem in not_allowed_spaces):
                fileName = os.path.join(dirpath, file)
                removedCount += 1
                os.remove(fileName)

    print('Libs files cleaned:', removedCount)

def CleanIncludes(dir, not_allowed_spaces):
    removedCount = 0
    for elemName in os.listdir(dir):
        dirPath = os.path.join(dir, elemName)
        
        if os.path.isdir(dirPath) and any(elem in elemName for elem in not_allowed_spaces):
            shutil.rmtree(dirPath)
            removedCount += 1

    print('Include folders cleaned:', removedCount)

def RunCommandForEveryLib(folderName, commandArgsList):
    print('>', ' '.join(commandArgsList))
    for fullName in GetLibs(folderName):
        resultRaw = ''
        command = commandArgsList
        command.append(fullName)
        try:
            resultRaw = check_output(command)
        except Exception:
            print('[Error] file:', fullName)
    
def ReplaceSonameWithFileRemove(folderName, libDir, soname, fileName):
    libFileNameNew = libDir + '/' + soname
    libFileNameOld = libDir + '/' + fileName
    # leave only one file, starting from *.so.*, but rename it after all to *.so
    if libFileNameNew != libFileNameOld and os.path.exists(libFileNameOld):
        if os.path.exists(libFileNameNew):
            os.remove(libFileNameNew)

        os.rename(libFileNameOld, libFileNameNew)

    command = 'patchelf --set-soname ' + soname + ' ' + libFileNameNew
    print('> ', command)
    os.system(command)

    RunCommandForEveryLib(folderName, ['patchelf', '--replace-needed', fileName, soname])

# UE4.27 can't deal with so libs with version (for example libmyname.so.2.0.3)
# you can fix it by adding:
# /home/vilkun/UE/UnrealEngine/Engine/Source/Programs/UnrealBuildTool/Platform/Linux/LinuxToolChain.cs
# in LinkFiles() add 1 line:
# string LibName = Path.GetFileNameWithoutExtension(AdditionalLibrary);
# +++LibName = LibName.Split('.')[0];
# but it's not a proper fix, since we provide plugin for end users, and can't change their UE4.27
# So solution can be run renaming for all of this libraries 'SONAME' and links to this libraries inside all others
def RenameLibsWithVersion(pluginPath, projectPath):
    print('Looking for libs with version...')
    versionMarker = '.so.'
    libsReplacements = dict()
    # map {libname:dir}
    lib_files = {os.path.basename(x):os.path.dirname(x) for x in glob.glob(os.path.join(projectPath, 'Plugins/**/*.so'), recursive=True)}
    for fullName in GetLibs(pluginPath):
        lddInfoRaw = os.popen('ldd ' + fullName).read()
        for rawInfoLine in lddInfoRaw.split('\n'):
            if versionMarker in rawInfoLine and 'not found' in rawInfoLine:
                libNameVersioning = rawInfoLine.split('=>')[0].lstrip().rstrip()
                soname = libNameVersioning.split(versionMarker)[0] + '.so'

                if soname in lib_files:
                    libsReplacements[libNameVersioning] = [soname, lib_files[soname]]
                else:
                    print('[Error] Failed to find potential lib:', soname)
                
    libsReplacements = dict(sorted(libsReplacements.items())) 
    print('Libs with version which needed to be renamed: {}'.format(libsReplacements))
    for libNameVersioning, soname_and_dir in libsReplacements.items():
        ReplaceSonameWithFileRemove(pluginPath, soname_and_dir[1], soname_and_dir[0], libNameVersioning)

# this arguments order like '--remove-rpath' and  '--force-rpath --set-rpath' is a hack
# check https://github.com/NixOS/patchelf/issues/94

# every lib already contains ORIGIN due to linker flag, which I provided by '-rpath', see:
# build_ros_libs.sh
# but here we can 'reset' all other additional user paths which appears inside RPATH during build
def SetRPATH(folderName):
    RunCommandForEveryLib(folderName, ['patchelf', '--remove-rpath'])
    RunCommandForEveryLib(folderName, ['patchelf', '--force-rpath', '--set-rpath', r'${ORIGIN}'])

# help function during investigation
def CheckLibs(folderName):
    libs = GetLibs(folderName)
    libs.sort()
    libsSet = set()

    print('Found libs:', len(libs))
    print('"' + '",\n"'.join(libs) + '"')

    print('Checking duplications...')

    for lib in libs:
        if lib in libsSet:
            print('Duplication:', lib)
        else:
            libsSet.add(lib)

    print('Error. Duplications were found') if len(libs) != len(libsSet) else print('All ok. Duplications are not found')
