from jinja2 import Environment, FileSystemLoader
from numpy.lib.stride_tricks import as_strided
import sys
import os
import glob
import re
import pandas as pd

#base_types = { 'bool', 'char', 'string', 'int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32', 'uint64', 'float32', 'float64' }

def get_var_name(curval = {}):
    if len(curval) == 2:
        return [str(curval[0]), str(curval[1])]
    elif len(curval) == 3:
        res = []
        final = []
        for v in curval[2]:
            res = get_var_name(v)
            it = iter(res)
            for r in it:
                final.append(r)
                final.append(curval[1] + '_' + next(it))
        return final
    else:
        print('ERROR with ' + str(curval))
    return '',''

def convert_to_cpp_type(t):
    if t == 'int32':
        return 'int'
    elif t == 'uint32':
        return 'unsigned int'
    elif t == 'float32':
        return 'float'
    elif t == 'float64':
        return 'double'
    return t

def get_types(target_paths):
    types = set()
    for target_path in target_paths:
        for subdir, dirs, files in os.walk(target_path):
            files = [ fi for fi in files if fi.endswith(('.msg','.srv','.action')) ]
            filepaths = [ os.path.join(subdir, filename) for filename in files]
            for fp in filepaths:
                content = []
                with open(fp) as f:
                    content = f.readlines()
                content = [ x.strip() for x in content ]
                content = [ re.sub(r'<=.*','',re.sub(r'\[.*\]', '', c.split()[0])) for c in content if not c.startswith('#') and c != '' and c != '---' ]
                
                for c in content:
                    types.add(c)
                el = fp.split('/')
                types.add(el[len(el)-3] + '/' + os.path.splitext(os.path.basename(fp))[0])

    return types

def get_types_dict(target_paths):
    types_dict = {}
    types = get_types(target_paths)
    for target_path in target_paths:
        for t in types:
            tsplit = t.split('/')
            for subdir, dirs, files in os.walk(target_path):
                files = [ fi for fi in files if fi.endswith(('.msg','.srv','.action')) ]
                for fi in files:
                    content = []
                    if (len(tsplit) == 1 and os.path.splitext(fi)[0] == t) or (len(tsplit) == 2 and tsplit[0] in subdir and os.path.splitext(fi)[0] == tsplit[1]):
                        with open(os.path.join(subdir,fi)) as f:
                            content = f.readlines()
                        content = [ x.strip() for x in content ]
                        content = [ c.split()[0:2] for c in content if not c.startswith('#') and c != '' and c != '---' ]
                        types_dict[t] = content

    for key, value in types_dict.items():
        for index, c in enumerate(value):
            v = c[0].replace('[]','')
            if v in types_dict:
                value[index] = [c[0],c[1],types_dict[v]]

    return types_dict

def get_types_cpp(target_paths):
    types_dict = get_types_dict(target_paths)
    types_cpp = {}
    for key, value in types_dict.items():
        cpp_type = ''
        for v in value:
            res = get_var_name(v)
            it = iter(res)
            for r in it:
                r = convert_to_cpp_type(r)
                if '[]' in r:
                    r = r.replace('[]','')
                    r = 'TArray<' + convert_to_cpp_type(r) + '>'
                elif '[' in r and ']' in r:
                    tmp = re.split('\[|\]', r)
                    tmp[1] = tmp[1].replace('<=','')
                    r = 'TArray<' + convert_to_cpp_type(tmp[0]) + ', TFixedAllocator<' + tmp[1] + '>>'
                cpp_type += r + ' ' + next(it) + ';\n\t'
        types_cpp[key] = cpp_type
    return types_cpp




file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)

current_dir = os.getcwd()

ros_path = sys.argv[1]
ue_path = sys.argv[2]
Group = os.path.basename(os.path.dirname(ue_path))

types_cpp = get_types_cpp([ros_path, os.path.split(os.path.dirname(ue_path))[0]])

# for key,value in types_cpp.items():
#     print(key + ' -> ' + str(value))

#[print(key + ' -> ' + value) for key, value in types_cpp.items() if 'Fibonacci' in key]

# generate code
for subdir in ['action','srv','msg']:
    if os.path.exists(ue_path+'/'+subdir):
        os.chdir(ue_path+'/'+subdir)
        for file in glob.glob('*.'+subdir):
            print(file)
            # message = pd.read_csv(file, header=None, index_col=None, sep=' ')
            # message_d = dict(zip(message[[1]].values.ravel(), message[[0]].values.ravel()))
            
            info = {}
            info['Group'] = Group
            info['Name'] = re.sub(r'(?<!^)(?=[A-Z])', '_', os.path.splitext(file)[0]).lower()
            info['NameCap'] = os.path.splitext(file)[0]
            info['StructName'] = info['NameCap']
            info['Types'] = types_cpp[Group + '/' + info['NameCap']]
            # for key, value in message_d.items():
            #         if message_d[key] != '---':
            #             info['Types'] += value + ' ' + key + ';\n\t'
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
