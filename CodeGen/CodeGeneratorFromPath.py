from jinja2 import Environment, FileSystemLoader
from numpy.lib.stride_tricks import as_strided
import sys
import os
import glob
import re
import pandas as pd

# generate variable name for C++
def get_var_name(curval = {}, is_array = False):
    if len(curval) == 2:
        vartype = curval[0]
        if '[]' not in curval[0] and is_array:
            vartype += '[]'
        return [str(vartype), str(curval[1])]
    elif len(curval) == 3:
        res = []
        final = []
        for v in curval[2]:
            res = get_var_name(v, is_array)
            it = iter(res)
            for r in it:
                final.append(r)
                final.append(curval[1] + '_' + next(it))
        return final
    else:
        print('ERROR with ' + str(curval) + ' (get_var_name)')
    return '',''

# generate msg variable access for ROS msg - should this be merged with the above? or is this going to diverge? at the moment only the separator symbol is different!
def get_ros_var_name(curval = {}, is_array = False):
    if len(curval) == 2:
        vartype = curval[0]
        if '[]' not in curval[0] and is_array:
            vartype += '[]'
        return [str(vartype), str(curval[1])]
    elif len(curval) == 3:
        res = []
        final = []
        for v in curval[2]:
            res = get_ros_var_name(v, is_array)
            it = iter(res)
            for r in it:
                final.append(r)
                final.append(curval[1] + '.' + next(it)) # this won't work - need to add index access to it!
        return final
    else:
        print('ERROR with ' + str(curval) + ' (get_ros_var_name)')
    return '',''

def convert_to_cpp_type(t):
    if t == 'int32':
        return 'int'
    elif t == 'uint32':
        return 'unsigned int'
    elif t == 'byte':
        return 'uint8'
    elif t == 'char':
        return 'uint8'
    elif t == 'float32':
        return 'float'
    elif t == 'float64':
        return 'double'
    elif t == 'string':
        return 'FString'
    elif t == 'Vector3' or t == 'Point32':
        return 'FVector'
    elif t == 'Quaternion':
        return 'FQuat'
    return t

def check_deprecated(path, sdir, file):
    file_path = str(path) + '/' + str(sdir) + '/' + str(file)
    content = []
    with open(file_path) as f:
        content = f.readlines()
    for line in content:
        if 'deprecated as of Foxy' in line:
            print(file_path + ' is deprecated in foxy')
            return True
    return False

# generate code for setter (SetFromROS2)
def setter(r, v_type, v_ros, size):
    if r == 'FVector':
        return v_type + '.X = data.' + v_ros + '.x;\n\t\t' + v_type + '.Y = data.' + v_ros + '.y;\n\t\t' + v_type + '.Z = data.' + v_ros + '.z;\n\n\t\t'
    elif r == 'FQuat':
        return v_type + '.X = data.' + v_ros + '.x;\n\t\t' + v_type + '.Y = data.' + v_ros + '.y;\n\t\t' + v_type + '.Z = data.' + v_ros + '.z;\n\t\t' + v_type + '.W = data.' + v_ros + '.w;\n\n\t\t'
    elif r == 'FString':
        return v_type + '.AppendChars(data.' + v_ros + '.data, data.' + v_ros + '.size);\n\n\t\t'
    elif 'TArray' in r:
        if 'FVector' in r:
            if size > 0:
                return 'for (int i = 0; i < ' + str(size) + '; i++)\n\t\t{\n\t\t\t' + v_type + '[i].X = data.' + v_ros + '.data[i].x;\n\t\t\t' + v_type + '[i].Y = data.' + v_ros + '.data[i].y;\n\t\t\t' + v_type + '[i].Z = data.' + v_ros + '.data[i].z;\n\t\t}\n\n\t\t'
            else:
                # problem: need to identify which of the variables in the chain is the vector
                if '.' in v_ros:
                    v_ros_split = v_ros.split('.')
                    return 'for (int i = 0; i < data.' + v_ros_split[0] + '.size; i++)\n\t\t{\n\t\t\t' + v_type + '[i].X = data.' + v_ros_split[0] + '.data[i].' + v_ros_split[1] + '.x;\n\t\t\t' + v_type + '[i].Y = data.' + v_ros_split[0] + '.data[i].' + v_ros_split[1] + '.y;\n\t\t\t' + v_type + '[i].Z = data.' + v_ros_split[0] + '.data[i].' + v_ros_split[1] + '.z;\n\t\t}\n\n\t\t'
                else:
                    return 'for (int i = 0; i < data.' + v_ros + '.size; i++)\n\t\t{\n\t\t\t' + v_type + '[i].X = data.' + v_ros + '.data[i].x;\n\t\t\t' + v_type + '[i].Y = data.' + v_ros + '.data[i].y;\n\t\t\t' + v_type + '[i].Z = data.' + v_ros + '.data[i].z;\n\t\t}\n\n\t\t'
        elif 'FQuat' in r:
            if size > 0:
                return 'for (int i = 0; i < ' + str(size) + '; i++)\n\t\t{\n\t\t\t' + v_type + '[i].X = data.' + v_ros + '.data[i].x;\n\t\t\t' + v_type + '[i].Y = data.' + v_ros + '.data[i].y;\n\t\t\t' + v_type + '[i].Z = data.' + v_ros + '.data[i].z;\n\t\t}\n\n\t\t'
            else:
                # problem: need to identify which of the variables in the chain is the vector
                if '.' in v_ros:
                    v_ros_split = v_ros.split('.')
                    return 'for (int i = 0; i < data.' + v_ros_split[0] + '.size; i++)\n\t\t{\n\t\t\t' + v_type + '[i].X = data.' + v_ros_split[0] + '.data[i].' + v_ros_split[1] + '.x;\n\t\t\t' + v_type + '[i].Y = data.' + v_ros_split[0] + '.data[i].' + v_ros_split[1] + '.y;\n\t\t\t' + v_type + '[i].Z = data.' + v_ros_split[0] + '.data[i].' + v_ros_split[1] + '.z;\n\t\t\t' + v_type + '[i].W = data.' + v_ros_split[0] + '.data[i].' + v_ros_split[1] + '.w;\n\t\t}\n\n\t\t'
                else:
                    return 'for (int i = 0; i < data.' + v_ros + '.size; i++)\n\t\t{\n\t\t\t' + v_type + '[i].X = data.' + v_ros + '.data[i].x;\n\t\t\t' + v_type + '[i].Y = data.' + v_ros + '.data[i].y;\n\t\t\t' + v_type + '[i].Z = data.' + v_ros + '.data[i].z;\n\t\t\t' + v_type + '[i].W = data.' + v_ros + '.data[i].w;\n\t\t}\n\n\t\t'
        elif 'FString' in r:
            if size > 0:
                return 'TODO - for (int i = 0; i < ' + str(size) + '; i++)\n\t\t{\n\t\t\t' + v_type + '[i].AppendChars(data.' + v_ros + '.data[i], data.' + v_ros + '.size);\n\t\t}\n\n\t\t'
            else:
                # problem: need to identify which of the variables in the chain is the vector
                if '.' in v_ros:
                    v_ros_split = v_ros.split('.')
                    return 'TODO - for (int i = 0; i < data.' + v_ros_split[0] + '.size; i++)\n\t\t{\n\t\t\t' + v_type + '[i] = data.' + v_ros_split[0] + '.data[i].' + v_ros_split[1] + ';\n\t\t}\n\n\t\t'
                else:
                    return 'TODO - for (int i = 0; i < data.' + v_ros + '.size; i++)\n\t\t{\n\t\t\t' + v_type + '[i] = data.' + v_ros + '.data[i];\n\t\t}\n\n\t\t'
        else:
            if size > 0:
                return 'for (int i = 0; i < ' + str(size) + '; i++)\n\t\t{\n\t\t\t' + v_type + '[i] = data.' + v_ros + '.data[i];\n\t\t}\n\n\t\t'
            else:
                # problem: need to identify which of the variables in the chain is the vector
                if '.' in v_ros:
                    v_ros_split = v_ros.split('.')
                    return 'for (int i = 0; i < data.' + v_ros_split[0] + '.size; i++)\n\t\t{\n\t\t\t' + v_type + '[i] = data.' + v_ros_split[0] + '.data[i].' + v_ros_split[1] + ';\n\t\t}\n\n\t\t'
                else:
                    return 'for (int i = 0; i < data.' + v_ros + '.size; i++)\n\t\t{\n\t\t\t' + v_type + '[i] = data.' + v_ros + '.data[i];\n\t\t}\n\n\t\t'
    else:
        return v_type + ' = data.' + v_ros + ';\n\n\t\t'

# generate code for getter (SetROS2)
def getter(r, v_type, v_ros, size):
    if r == 'FVector':
        return 'data.' + v_ros + '.x = ' + v_type + '.X;\n\t\tdata.' + v_ros + '.y = ' + v_type + '.Y;\n\t\tdata.' + v_ros + '.z = ' + v_type + '.Z;\n\n\t\t'
    elif r == 'FQuat':
        return 'data.' + v_ros + '.x = ' + v_type + '.X;\n\t\tdata.' + v_ros + '.y = ' + v_type + '.Y;\n\t\tdata.' + v_ros + '.z = ' + v_type + '.Z;\n\t\tdata.' + v_ros + '.w = ' + v_type + '.W;\n\n\t\t'
    elif r == 'FString':
        return 'if (data.' + v_ros + '.data != nullptr)\n\t\t{\n\t\t\tfree(data.' + v_ros + '.data);\n\t\t}' \
            + '\n\t\tdata.' + v_ros + '.data = (char*)malloc((' + v_type + '.Len()+1)*sizeof(char));\n\t\tmemcpy(data.' + v_ros + '.data, TCHAR_TO_ANSI(*' + v_type + '), (' + v_type + '.Len()+1)*sizeof(char));\n\t\t' \
            + 'data.' + v_ros + '.size = ' + v_type + '.Len();\n\t\tdata.' + v_ros + '.capacity = ' + v_type + '.Len() + 1;\n\n\t\t'
    elif 'TArray' in r:
        if 'FVector' in r:
            if size > 0:
                return 'for (int i = 0; i < ' + str(size) + '; i++)\n\t\t{\n\t\t\tdata.' + v_ros + '.data[i].x = ' + v_type + '[i].X;\n\t\t\tdata.' + v_ros + '.data[i].y = ' + v_type + '[i].Y;\n\t\t\tdata.' + v_ros + '.data[i].z = ' + v_type + '[i].Z;\n\t\t}\n\n\t\t'
            else:
                # problem: need to identify which of the variables in the chain is the vector
                if '.' in v_ros:
                    v_ros_split = v_ros.split('.')
                    return 'for (int i = 0; i < ' + v_type + '.Num(); i++)\n\t\t{\n\t\t\tdata.' + v_ros_split[0] + '.data[i].' + v_ros_split[1] + '.x = ' + v_type + '[i].X;\n\t\t\tdata.' + v_ros_split[0] + '.data[i].' + v_ros_split[1] + '.y = ' + v_type + '[i].Y;\n\t\t\tdata.' + v_ros_split[0] + '.data[i].' + v_ros_split[1] + '.z = ' + v_type + '[i].Z;\n\t\t}\n\n\t\t'
                else:
                    return 'for (int i = 0; i < ' + v_type + '.Num(); i++)\n\t\t{\n\t\t\tdata.' + v_ros + '.data[i].x = ' + v_type + '[i].X;\n\t\t\tdata.' + v_ros + '.data[i].y = ' + v_type + '[i].Y;\n\t\t\tdata.' + v_ros + '.data[i].z = ' + v_type + '[i].Z;\n\t\t}\n\n\t\t'
        elif 'FQuat' in r:
            if size > 0:
                return 'for (int i = 0; i < ' + str(size) + '; i++)\n\t\t{\n\t\t\tdata.' + v_ros + '.data[i].x = ' + v_type + '[i].X;\n\t\t\tdata.' + v_ros + '.data[i].y = ' + v_type + '[i].Y;\n\t\t\tdata.' + v_ros + '.data[i].z = ' + v_type + '[i].Z;\n\t\t\tdata.' + v_ros + '.data[i].w = ' + v_type + '[i].W;\n\t\t}\n\n\t\t'
            else:
                # problem: need to identify which of the variables in the chain is the vector
                if '.' in v_ros:
                    v_ros_split = v_ros.split('.')
                    return 'for (int i = 0; i < ' + v_type + '.Num(); i++)\n\t\t{\n\t\t\tdata.' + v_ros_split[0] + '.data[i].' + v_ros_split[1] + '.x = ' + v_type + '[i].X;\n\t\t\tdata.' + v_ros_split[0] + '.data[i].' + v_ros_split[1] + '.y = ' + v_type + '[i].Y;\n\t\t\tdata.' + v_ros_split[0] + '.data[i].' + v_ros_split[1] + '.z = ' + v_type + '[i].Z;\n\t\t\tdata.' + v_ros_split[0] + '.data[i].' + v_ros_split[1] + '.w = ' + v_type + '[i].W;\n\t\t}\n\n\t\t'
                else:
                    return 'for (int i = 0; i < ' + v_type + '.Num(); i++)\n\t\t{\n\t\t\tdata.' + v_ros + '.data[i].x = ' + v_type + '[i].X;\n\t\t\tdata.' + v_ros + '.data[i].y = ' + v_type + '[i].Y;\n\t\t\tdata.' + v_ros + '.data[i].z = ' + v_type + '[i].Z;\n\t\t\tdata.' + v_ros + '.data[i].w = ' + v_type + '[i].W;\n\t\t}\n\n\t\t'
        elif 'FString' in r:
            if size > 0:
                return 'TODO - for (int i = 0; i < ' + str(size) + '; i++)\n\t\t{\n\t\t\tdata.' + v_ros + '.data[i] = ' + v_type + '[i];\n\t\t}\n\n\t\t'
            else:
                # problem: need to identify which of the variables in the chain is the vector
                if '.' in v_ros:
                    v_ros_split = v_ros.split('.')
                    return 'TODO - for (int i = 0; i < ' + v_type + '.Num(); i++)\n\t\t{\n\t\t\tdata.' + v_ros_split[0] + '.data[i].' + v_ros_split[1] + ' = ' + v_type + '[i];\n\t\t}\n\n\t\t'
                else:
                    return 'TODO - for (int i = 0; i < ' + v_type + '.Num(); i++)\n\t\t{\n\t\t\tdata.' + v_ros + '.data[i] = ' + v_type + '[i];\n\t\t}\n\n\t\t'
        else:
            if size > 0:
                return 'for (int i = 0; i < ' + str(size) + '; i++)\n\t\t{\n\t\t\tdata.' + v_ros + '.data[i] = ' + v_type + '[i];\n\t\t}\n\n\t\t'
            else:
                # problem: need to identify which of the variables in the chain is the vector
                if '.' in v_ros:
                    v_ros_split = v_ros.split('.')
                    return 'for (int i = 0; i < ' + v_type + '.Num(); i++)\n\t\t{\n\t\t\tdata.' + v_ros_split[0] + '.data[i].' + v_ros_split[1] + ' = ' + v_type + '[i];\n\t\t}\n\n\t\t'
                else:
                    return 'for (int i = 0; i < ' + v_type + '.Num(); i++)\n\t\t{\n\t\t\tdata.' + v_ros + '.data[i] = ' + v_type + '[i];\n\t\t}\n\n\t\t'
    else:
        return 'data.' + v_ros + ' = ' + v_type + ';\n\n\t\t'


# scan msg, srv and action files to find all types present in the given target_paths
def get_types(target_paths):
    types = set()
    for target_path in target_paths:
        for subdir, dirs, files in os.walk(target_path):
            files = [ fi for fi in files if fi.endswith(('.msg','.srv','.action')) ]
            filepaths = [ os.path.join(subdir, filename) for filename in files] # compose filename with path
            for fp in filepaths:
                content = []
                # load all data of the file into content, line by line
                with open(fp) as f:
                    content = f.readlines()
                                    
                # remove leading and trailing spaces, including new lines '\n'
                content = [ x.strip() for x in content ]
                
                # ignore empty lines ''
                content = [ c for c in content if c != '' ]
                
                # ignore comment lines '#'
                content = [ c for c in content if not c.startswith('#') ]
                
                # ignore separator lines '---'
                content = [ c for c in content if c != '---' ]
                
                # Get type
                content = [ c.split()[0] for c in content ]
                
                # remove array markers '[]'
                content = [ re.sub(r'\[.*\]', '', c) for c in content ]
                
                # remove array sizes
                content = [ re.sub(r'<=.*','',c) for c in content ]
                
                # include complex types (self)
                for c in content:
                    types.add(c)

                el = fp.split('/')
                file_type = el[len(el)-3] + '/' + os.path.splitext(os.path.basename(fp))[0]
                types.add(file_type)

    # for t in types:
    #     print(t)

    return types


# create a dictionary matching types with the corresponding expanded contents expressed with basic types
def get_types_dict(target_paths):
    types_dict = {}
    types = get_types(target_paths)

    # for every folder to scan
    for target_path in target_paths:

        # for every type
        for t in types:
            tsplit = t.split('/')

            # iterate all subfolders
            for subdir, dirs, files in os.walk(target_path):

                # iterate over all msg, srv and action files
                files = [ fi for fi in files if fi.endswith(('.msg','.srv','.action')) ]
                for fi in files:
                    content = []

                    # if the file corresponds to the type t being processed
                    if (len(tsplit) == 1 and os.path.splitext(fi)[0] == t) or (len(tsplit) == 2 and tsplit[0] in subdir and os.path.splitext(fi)[0] == tsplit[1]):

                        # load all data of the file into content, line by line
                        with open(os.path.join(subdir,fi)) as f:
                            content = f.readlines()

                        # remove leading and trailing spaces, including new lines '\n'
                        content = [ x.strip() for x in content ]

                        content = [ re.sub(r'<=','',c) for c in content ]
                        content = [ c for c in content if not c.startswith('#') and c != '' ]
                        content = [ c.split('#')[0] for c in content ]

                        # remove constants - these will eventually need to be used
                        content = [ c for c in content if '=' not in c ]

                        if not fi.endswith('.action'):
                            # remove comments, empty and separator lines; keep only variable type and name
                            content = [ c.split()[0:2] for c in content if  c != '---' ]
                            #content = [ c for c in content if '=' not in c[1] ] # ignore constants
                            types_dict[t] = content
                        else:
                            # remove comments and empty lines; keep only variable type and name
                            content = [ c.split()[0:2] for c in content ]
                            counter = 0
                            for c in content:
                                if not c == ['---']:
                                    if '=' not in c[1]:
                                        if counter == 0:
                                            if (t+'_SendGoal') in types_dict and c not in types_dict[t+'_SendGoal']:
                                                types_dict[t+'_SendGoal'].append(c)
                                            else:
                                                types_dict[t+'_SendGoal'] = [c]
                                        elif counter == 1:
                                            if (t+'_GetResult') in types_dict and c not in types_dict[t+'_GetResult']:
                                                types_dict[t+'_GetResult'].append(c)
                                            else:
                                                types_dict[t+'_GetResult'] = [c]
                                        elif counter == 2:
                                            if (t+'_Feedback') in types_dict and c not in types_dict[t+'_Feedback']:
                                                types_dict[t+'_Feedback'].append(c)
                                            else:
                                                types_dict[t+'_Feedback'] = [c]
                                else:
                                    counter += 1

    # remove complex types that have a corresponding UE type
    types_dict.pop('Vector3', None)
    types_dict.pop('Point32', None)
    types_dict.pop('Quaternion', None)

    # traverse and add complex type breakdown
    for key, value in types_dict.items():
        for index, c in enumerate(value):
            v = c[0].replace('[]','')
            if v in types_dict:
                value[index] = [c[0],c[1],types_dict[v]]

    # for key, value in types_dict.items():
    #     print(str(key) + ' -> ' + str(value))

    return types_dict


# generate C++ code snippets to be inserted in their respective placeholders in the templates
# element 0: type
# element 1: set from ros2
# element 2: set ros2
def get_types_cpp(target_paths):
    types_dict = get_types_dict(target_paths)
    types_cpp = {}

    for key, value in types_dict.items():
        cpp_type = ''
        set_ros2 = ''
        set_from_ros2 = ''
        for v in value:
            is_array = False
            if '[]' in v[0]:
                is_array = True
            res = get_var_name(v, is_array)
            it = iter(res)
            for r in it:
                r = convert_to_cpp_type(r)
                if '[]' in r:
                    r = r.replace('[]','')
                    r = 'TArray<' + convert_to_cpp_type(r) + '>'
                elif '[' in r and ']' in r:
                    tmp = re.split('\[|\]', r)
                    tmp[1] = tmp[1].replace('<=','')
                    r = 'TArray<' + convert_to_cpp_type(tmp[0]) + '>'
                if ('unsigned int' in r or 'double' in r or 'int8' in r or 'uint16' in r):
                    cpp_type += r + ' ' + next(it) + ';\n\n\t'
                else:
                    cpp_type += 'UPROPERTY(EditAnywhere, BlueprintReadWrite)\n\t' + r + ' ' + next(it) + ';\n\n\t'

            res_ros = get_ros_var_name(v, is_array)
            it_ros = iter(res_ros)
            it_type = iter(res)
            for r in it_ros:
                size = 0
                r = convert_to_cpp_type(r)
                if '[]' in r:
                    r = r.replace('[]','')
                    r = 'TArray<' + convert_to_cpp_type(r) + '>'
                elif '[' in r and ']' in r:
                    tmp = re.split('\[|\]', r)
                    size = tmp[1].replace('<=','')
                    r = 'TArray<' + convert_to_cpp_type(tmp[0]) + '>'
                v_ros = next(it_ros)
                next(it_type)
                v_type = next(it_type)
                set_from_ros2 += setter(r, v_type, v_ros, int(size))
                set_ros2      += getter(r, v_type, v_ros, int(size))

        types_cpp[key] = [cpp_type, set_from_ros2, set_ros2]

    # for key, value in types_cpp.items():
    #     print(str(key) + ' -> ' + str(value[0]))

    return types_cpp


file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)

current_dir = os.getcwd()

ros_path = sys.argv[1]
ue_path = sys.argv[2]
Group = os.path.basename(os.path.dirname(ue_path))

types_cpp = get_types_cpp([ros_path, os.path.split(os.path.dirname(ue_path))[0]])


# generate code
for subdir in ['action','srv','msg']:
    if os.path.exists(ue_path+'/'+subdir):
        os.chdir(ue_path+'/'+subdir)
        for file in glob.glob('*.'+subdir):
            package_name = os.path.split(os.path.split(ue_path)[0])[1]
            #print(package_name + '/' + file)

            if check_deprecated(ue_path, subdir, file):
                continue
            
            info = {}
            info['Filename'] = package_name + '/' + file
            info['Group'] = Group
            name = os.path.splitext(file)[0]
            name_lower = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
            info['Name'] = name_lower
            info['NameCap'] = name
            # if (name == 'String'):
            #     info['Name'] = 'rosstring'
            #     info['NameCap'] = 'ROSString'
            info['StructName'] = 'ROS' + info['NameCap']
            if subdir == 'msg':
                info['Types'] = types_cpp[Group + '/' + name][0]
                info['SetFromROS2'] = types_cpp[Group + '/' + name][1]
                info['SetROS2'] = types_cpp[Group + '/' + name][2]
            elif subdir == 'srv':
                info['ReqTypes'] = types_cpp[Group + '/' + name + '_Request'][0]
                info['ReqSetFromROS2'] = types_cpp[Group + '/' + name + '_Request'][1]
                info['ReqSetROS2'] = types_cpp[Group + '/' + name + '_Request'][2]
                info['ResTypes'] = types_cpp[Group + '/' + name + '_Response'][0]
                info['ResSetFromROS2'] = types_cpp[Group + '/' + name + '_Response'][1]
                info['ResSetROS2'] = types_cpp[Group + '/' + name + '_Response'][2]
            elif subdir == 'action':
                info['GoalTypes'] = types_cpp[Group + '/' + name + '_SendGoal'][0]
                info['GoalSetFromROS2'] = types_cpp[Group + '/' + name + '_SendGoal'][1].replace('data.','data.goal.')
                info['GoalSetROS2'] = types_cpp[Group + '/' + name + '_SendGoal'][2].replace('data.','data.goal.')
                
                info['ResultTypes'] = types_cpp[Group + '/' + name + '_GetResult'][0]
                info['ResultSetFromROS2'] = types_cpp[Group + '/' + name + '_GetResult'][1].replace('data.','data.result.')
                info['ResultSetROS2'] = types_cpp[Group + '/' + name + '_GetResult'][2].replace('data.','data.result.')
                
                info['FeedbackTypes'] = types_cpp[Group + '/' + name + '_Feedback'][0]
                info['FeedbackSetFromROS2'] = types_cpp[Group + '/' + name + '_Feedback'][1].replace('data.','data.feedback.')
                info['FeedbackSetROS2'] = types_cpp[Group + '/' + name + '_Feedback'][2].replace('data.','data.feedback.')

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
            filename=current_dir+'/ROS2'+name+subdir.title()
            file_h = open(filename+'.h', "w")
            file_cpp = open(filename+'.cpp', "w")

            file_h.write(output_h)
            file_cpp.write(output_cpp)

            file_h.close()
            file_cpp.close()
