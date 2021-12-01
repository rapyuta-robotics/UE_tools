import sys
import os
import shutil
import glob

current_dir = os.getcwd()

#todo use python arg parser
ue_project_path = sys.argv[1] #e.g. /home/common/io_amr_UE
ros_path = sys.argv[2] #e.g. /opt/ros/foxy
ros_package_name = sys.argv[3] #e.g. geometry_msgs

ue_prject_src_path = os.path.join(ue_project_path, 'Plugins/rclUE/Source')
private_path = os.path.join(ue_prject_src_path, 'rclUE/Private')
public_path = os.path.join(ue_prject_src_path, 'rclUE/Public')

#copy src
for type_name in ['Action','Srv','Msg']:
    for file_name in glob.glob('*'+type_name+'.h'):
        shutil.copy(os.path.join(current_dir, file_name), os.path.join(public_path, type_name+'s'))
    for file_name in glob.glob('*'+type_name+'.cpp'):
        shutil.copy(os.path.join(current_dir, file_name), os.path.join(private_path, type_name+'s'))

#copy header and library
ue_third_party_path = os.path.join(ue_prject_src_path, 'ThirdParty/ros2lib', ros_package_name)
ue_third_party_include_path = os.path.join(ue_third_party_path, 'include')
ue_third_party_lib_path = os.path.join(ue_third_party_path, 'lib')

ros_include_path = os.path.join(ros_path, 'include')
ros_lib_path = os.path.join(ros_path, 'lib')

os.makedirs(ue_third_party_include_path, exist_ok=True)
os.makedirs(ue_third_party_lib_path, exist_ok=True)

# copy header
try:
    src = os.path.join(ros_include_path, ros_package_name)
    dst = os.path.join(ue_third_party_include_path, ros_package_name)
    if os.path.exists(dst):
        shutil.rmtree(dst)
        shutil.copytree(src, dst)
except OSError as e:
    print(e)
    exit(0)

# copy lib
for file_name in glob.glob(os.path.join(ros_path, 'lib', 'lib'+ros_package_name+'__*.so')):
    shutil.copy(file_name, ue_third_party_lib_path)