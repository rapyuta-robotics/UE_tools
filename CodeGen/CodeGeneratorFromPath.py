from jinja2 import Environment, FileSystemLoader
from numpy.lib.stride_tricks import as_strided
import sys
import os
import glob
import re
import pandas as pd

file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)

current_dir = os.getcwd()

ros_path = sys.argv[1]
path = sys.argv[2]
Group = os.path.basename(os.path.dirname(path))

# if a type is not part of this list, we need to recurse
base_types = { 'bool', 'char', 'string', 'int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32', 'uint64', 'float32', 'float64' }

for subdir, dirs, files in os.walk(ros_path):
    files = [ fi for fi in files if fi.endswith(('.msg','.srv','.action')) ]
    filepaths = [ os.path.join(subdir, filename) for filename in files]
    for fp in filepaths:
        if 'srv' not in fp:
            content = []
            with open(fp) as f:
                content = f.readlines()
            content = [ x.strip() for x in content ]
            content = [ c.split() for c in content if '#' not in c and c != '' ]
            for c in content:
                base_types.add(c[0])

# types substitutions
# if populated correctly, it can be used to recurse definitions
types_dict = { 'int32': 'int', 'float32': 'float', 'float64': 'double' }

for t in base_types:
    tsplit = t.split('/')
    for subdir, dirs, files in os.walk(ros_path):
        files = [ fi for fi in files if fi.endswith(('.msg','.srv','.action')) ]
        for fi in files:
            if len(tsplit) == 1:
                if os.path.splitext(fi)[0] in t:
                    content = []
                    with open(os.path.join(subdir,fi)) as f:
                        content = f.readlines()
                    content = [ x.strip() for x in content ]
                    content = [ c.split()[0] for c in content if '#' not in c and c != '' ]
                    types_dict[t] = content
            elif len(tsplit) == 2:
                if t[0] in subdir and os.path.splitext(fi)[0] in t:
                    content = []
                    with open(os.path.join(subdir,fi)) as f:
                        content = f.readlines()
                    content = [ x.strip() for x in content ]
                    content = [ c.split()[0] for c in content if '#' not in c and c != '' ]
                    types_dict[t] = content
            else:
                print('ERROR')




for subdir in ['action','srv','msg']:
    if os.path.exists(path+'/'+subdir):
        os.chdir(path+'/'+subdir)
        for file in glob.glob('*.'+subdir):
            print(file)
            message = pd.read_csv(file, header=None, index_col=None, sep=' ')
            message_d = dict(zip(message[[1]].values.ravel(), message[[0]].values.ravel()))

            # recursion to reduce to base types



            # cleanup types
            for key, value in message_d.items():
                if '[]' in value:
                    base_type = value.replace('[]','')
                    if base_type in types_dict.keys():
                        message_d[key] = 'TArray<' + types_dict[base_type] + '>'
                    else:
                        message_d[key] = 'TArray<' + base_type + '>'
                if value in types_dict.keys():
                    message_d[key] = types_dict[value]

            info = {}
            info['Group'] = Group
            info['Name'] = re.sub(r'(?<!^)(?=[A-Z])', '_', os.path.splitext(file)[0]).lower()
            info['NameCap'] = os.path.splitext(file)[0]
            info['StructName'] = info['NameCap']
            info['Types'] = ''
            for key, value in message_d.items():
                    if message_d[key] != '---':
                        info['Types'] += value + ' ' + key + ';\n\t'
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
