from jinja2 import Environment, FileSystemLoader
from numpy.lib.stride_tricks import as_strided
import pandas
import sys
import os
import glob
import re

file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)

current_dir = os.getcwd()

path = sys.argv[1]
Group = os.path.basename(os.path.dirname(path))

for subdir in ['action','srv','msg']:
    if os.path.exists(path+'/'+subdir):
        os.chdir(path+'/'+subdir)
        for file in glob.glob('*.idl'):
            info = {}
            info['Group'] = Group
            info['Name'] = re.sub(r'(?<!^)(?=[A-Z])', '_', os.path.splitext(file)[0]).lower()
            info['NameCap'] = os.path.splitext(file)[0]
            print(info)

            os.chdir(current_dir)
    
            output_h = ''
            output_cpp = ''
            if subdir == 'msg':
                output_h = env.get_template('Msg.h').render(data=info)
                output_cpp = env.get_template('Msg.cpp').render(data=info)
            elif subdir == 'srv':
                output_h = env.get_template('Srv.h').render(data=info)
                output_cpp = env.get_template('Srv.cpp').render(data=info)
            elif subdir == 'action':
                output_h = env.get_template('Action.h').render(data=info)
                output_cpp = env.get_template('Action.cpp').render(data=info)
            else:
                print('type not found')

            # this should only happen if the file does not exist
            filename=current_dir+'/ROS2'+info['NameCap']+'Msg'
            file_h = open(filename+'.h', "w")
            file_cpp = open(filename+'.cpp', "w")

            file_h.write(output_h)
            file_cpp.write(output_cpp)

            file_h.close()
            file_cpp.close()
