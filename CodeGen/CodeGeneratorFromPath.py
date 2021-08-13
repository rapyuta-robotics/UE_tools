from jinja2 import Environment, FileSystemLoader
from numpy.lib.stride_tricks import as_strided
import sys
import os
import glob
import re
import pandas as pd

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

def get_ros_var_name(curval = {}):
    if len(curval) == 2:
        return [str(curval[0]), str(curval[1])]
    elif len(curval) == 3:
        res = []
        final = []
        for v in curval[2]:
            res = get_ros_var_name(v)
            it = iter(res)
            for r in it:
                final.append(r)
                final.append(curval[1] + '.' + next(it))
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
    elif t == 'string':
        return 'FString'
    elif t == 'Vector3' or t == 'Point':
        return 'FVector'
    elif t == 'Quaternion':
        return 'FQuat'
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

    types_dict.pop('Vector3', None)
    types_dict.pop('Point', None)
    types_dict.pop('Quaternion', None)
    for key, value in types_dict.items():
        for index, c in enumerate(value):
            v = c[0].replace('[]','')
            if v in types_dict:
                value[index] = [c[0],c[1],types_dict[v]]

    return types_dict

def setter(r, v_type, v_ros):
    if r == 'FVector':
        return v_type + '.X = data.' + v_ros + '.x;\n\t\t' + v_type + '.Y = data.' + v_ros + '.y;\n\t\t' + v_type + '.Z = data.' + v_ros + '.z;\n\n\t\t'
    elif r == 'FQuat':
        return v_type + '.X = data.' + v_ros + '.x;\n\t\t' + v_type + '.Y = data.' + v_ros + '.y;\n\t\t' + v_type + '.Z = data.' + v_ros + '.z;\n\t\t' + v_type + '.W = data.' + v_ros + '.w;\n\n\t\t'
    elif r == 'FString':
        return v_type + '.AppendChars(data.' + v_ros + '.data, data.' + v_ros + '.size);\n\n\t\t'
    else:
        return v_type + ' = data.' + v_ros + ';\n\n\t\t'

def getter(r, v_type, v_ros):
    if r == 'FVector':
        return 'data.' + v_ros + '.x = ' + v_type + '.X;\n\t\tdata.' + v_ros + '.y = ' + v_type + '.Y;\n\t\tdata.' + v_ros + '.z = ' + v_type + '.Z;\n\n\t\t'
    elif r == 'FQuat':
        return 'data.' + v_ros + '.x = ' + v_type + '.X;\n\t\tdata.' + v_ros + '.y = ' + v_type + '.Y;\n\t\tdata.' + v_ros + '.z = ' + v_type + '.Z;\n\t\tdata.' + v_ros + '.w = ' + v_type + '.W;\n\n\t\t'
    elif r == 'FString':
        return 'if (data.' + v_ros + '.data != nullptr)\n\t\t{\n\t\t\tfree(data.' + v_ros + '.data);\n\t\t}' \
            + '\n\t\tdata.' + v_ros + '.data = (char*)malloc((' + v_type + '.Len()+1)*sizeof(char));\n\t\tmemcpy(data.' + v_ros + '.data, TCHAR_TO_ANSI(*' + v_type + '), (' + v_type + '.Len()+1)*sizeof(char));\n\t\t' \
            + 'data.' + v_ros + '.size = ' + v_type + '.Len();\n\t\tdata.' + v_ros + '.capacity = ' + v_type + '.Len() + 1;\n\n\t\t'
    else:
        return 'data.' + v_ros + ' = ' + v_type + ';\n\n\t\t'

def get_types_cpp(target_paths):
    types_dict = get_types_dict(target_paths)
    types_cpp = {}
    set_ros2_cpp = {}
    set_from_ros2_cpp = {}
    for key, value in types_dict.items():
        cpp_type = ''
        set_ros2 = ''
        set_from_ros2 = ''
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

            res_ros = get_ros_var_name(v)
            it_ros = iter(res_ros)
            it_type = iter(res)
            for r in it_ros:
                r = convert_to_cpp_type(r)
                if '[]' in r:
                    r = r.replace('[]','')
                    r = 'TArray<' + convert_to_cpp_type(r) + '>'
                elif '[' in r and ']' in r:
                    tmp = re.split('\[|\]', r)
                    tmp[1] = tmp[1].replace('<=','')
                    r = 'TArray<' + convert_to_cpp_type(tmp[0]) + ', TFixedAllocator<' + tmp[1] + '>>'
                v_ros = next(it_ros)
                next(it_type)
                v_type = next(it_type)
                set_from_ros2 += setter(r, v_type, v_ros)
                set_ros2      += getter(r, v_type, v_ros)

        types_cpp[key] = cpp_type
        set_from_ros2_cpp[key] = set_from_ros2
        set_ros2_cpp[key] = set_ros2
    return types_cpp, set_from_ros2_cpp, set_ros2_cpp




file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)

current_dir = os.getcwd()

ros_path = sys.argv[1]
ue_path = sys.argv[2]
Group = os.path.basename(os.path.dirname(ue_path))

types_cpp, set_from_ros2_cpp, set_ros2_cpp = get_types_cpp([ros_path, os.path.split(os.path.dirname(ue_path))[0]])


# generate code
for subdir in ['action','srv','msg']:
    if os.path.exists(ue_path+'/'+subdir):
        os.chdir(ue_path+'/'+subdir)
        for file in glob.glob('*.'+subdir):
            print(file)            
            info = {}
            info['Group'] = Group
            info['Name'] = re.sub(r'(?<!^)(?=[A-Z])', '_', os.path.splitext(file)[0]).lower()
            info['NameCap'] = os.path.splitext(file)[0]
            info['StructName'] = info['NameCap']
            info['Types'] = types_cpp[Group + '/' + info['NameCap']]
            info['SetFromROS2'] = set_from_ros2_cpp[Group + '/' + info['NameCap']]
            info['SetROS2'] = set_ros2_cpp[Group + '/' + info['NameCap']]

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
            filename=current_dir+'/ROS2'+info['NameCap']+subdir.title()
            file_h = open(filename+'.h', "w")
            file_cpp = open(filename+'.cpp', "w")

            file_h.write(output_h)
            file_cpp.write(output_cpp)

            file_h.close()
            file_cpp.close()
