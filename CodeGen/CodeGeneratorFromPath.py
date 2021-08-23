from jinja2 import Environment, FileSystemLoader
from numpy.lib.stride_tricks import as_strided
import sys
import os
import glob
import re
import pandas as pd

# generate variable name for C++
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
        print('ERROR with ' + str(curval) + ' (get_var_name)')
    return '',''

# generate msg variable access for ROS msg
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
        print('ERROR with ' + str(curval) + ' (get_ros_var_name)')
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

# scan msg, srv and action files to find all types present in the given target_paths
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

# create a dictionary matching types with the corresponding expanded contents expressed with basic types
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
                        if not fi.endswith('.action'):
                            content = [ c.split()[0:2] for c in content if not c.startswith('#') and c != '' and c != '---' ] # this needs to be changed to parse actions correctly
                            types_dict[t] = content
                        else:
                            tmpdata = [ c.split()[0:2] for c in content if not c.startswith('#') and c != '' ]
                            counter = 0
                            for td in tmpdata:
                                if not td == ['---']:
                                    if counter == 0:
                                        if (t+'_SendGoal') in types_dict and td not in types_dict[t+'_SendGoal']:
                                            types_dict[t+'_SendGoal'].append(td)
                                        else:
                                            types_dict[t+'_SendGoal'] = [td]
                                    elif counter == 1:
                                        if (t+'_GetResult') in types_dict and td not in types_dict[t+'_GetResult']:
                                            types_dict[t+'_GetResult'].append(td)
                                        else:
                                            types_dict[t+'_GetResult'] = [td]
                                    elif counter == 2:
                                        if (t+'_Feedback') in types_dict and td not in types_dict[t+'_Feedback']:
                                            types_dict[t+'_Feedback'].append(td)
                                        else:
                                            types_dict[t+'_Feedback'] = [td]
                                else:
                                    counter += 1

    types_dict.pop('Vector3', None)
    types_dict.pop('Point', None)
    types_dict.pop('Quaternion', None)
    for key, value in types_dict.items():
        for index, c in enumerate(value):
            v = c[0].replace('[]','')
            if v in types_dict:
                value[index] = [c[0],c[1],types_dict[v]]

    return types_dict

# generate code for setter (SetFromROS2)
def setter(r, v_type, v_ros, size):
    if r == 'FVector':
        return v_type + '.X = data.' + v_ros + '.x;\n\t\t' + v_type + '.Y = data.' + v_ros + '.y;\n\t\t' + v_type + '.Z = data.' + v_ros + '.z;\n\n\t\t'
    elif r == 'FQuat':
        return v_type + '.X = data.' + v_ros + '.x;\n\t\t' + v_type + '.Y = data.' + v_ros + '.y;\n\t\t' + v_type + '.Z = data.' + v_ros + '.z;\n\t\t' + v_type + '.W = data.' + v_ros + '.w;\n\n\t\t'
    elif r == 'FString':
        return v_type + '.AppendChars(data.' + v_ros + '.data, data.' + v_ros + '.size);\n\n\t\t'
    elif 'TArray' in r:
        return 'for (int i = 0; i < ' + str(size) + '; i++)\n\t\t{\n\t\t\t' + v_type + '[i] = data.' + v_ros + '.data[i];\n\t\t}\n\n\t\t'
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
        return 'for (int i = 0; i < ' + str(size) + '; i++)\n\t\t{\n\t\t\tdata.' + v_ros + '.data[i] = ' + v_type + '[i];\n\t\t}\n\n\t\t'
    else:
        return 'data.' + v_ros + ' = ' + v_type + ';\n\n\t\t'

# generate C++ code snippets to be inserted in their respective placeholders in the templates
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
                    r = 'TArray<' + convert_to_cpp_type(tmp[0]) + '>'
                if ('unsigned int' in r):
                    cpp_type += r + ' ' + next(it) + ';\n\n\t'
                else:
                    cpp_type += 'UPROPERTY(EditAnywhere, BlueprintReadWrite)\n\t' + r + ' ' + next(it) + ';\n\n\t'

            res_ros = get_ros_var_name(v)
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
                set_from_ros2 += setter(r, v_type, v_ros, size)
                set_ros2      += getter(r, v_type, v_ros, size)

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
            package_name = os.path.split(os.path.split(ue_path)[0])[1]
            print(package_name + '/' + file)
            
            info = {}
            info['Filename'] = package_name + '/' + file
            info['Group'] = Group
            info['Name'] = re.sub(r'(?<!^)(?=[A-Z])', '_', os.path.splitext(file)[0]).lower()
            info['NameCap'] = os.path.splitext(file)[0]
            info['StructName'] = info['NameCap']
            if subdir == 'msg':
                info['Types'] = types_cpp[Group + '/' + info['NameCap']]
                info['SetFromROS2'] = set_from_ros2_cpp[Group + '/' + info['NameCap']]
                info['SetROS2'] = set_ros2_cpp[Group + '/' + info['NameCap']]
            elif subdir == 'srv':
                info['ReqTypes'] = types_cpp[Group + '/' + info['NameCap'] + '_Request']
                info['ReqSetFromROS2'] = set_from_ros2_cpp[Group + '/' + info['NameCap'] + '_Request']
                info['ReqSetROS2'] = set_ros2_cpp[Group + '/' + info['NameCap'] + '_Request']
                info['ResTypes'] = types_cpp[Group + '/' + info['NameCap'] + '_Response']
                info['ResSetFromROS2'] = set_from_ros2_cpp[Group + '/' + info['NameCap'] + '_Response']
                info['ResSetROS2'] = set_ros2_cpp[Group + '/' + info['NameCap'] + '_Response']
            elif subdir == 'action':
                info['GoalTypes'] = types_cpp[Group + '/' + info['NameCap'] + '_SendGoal']
                goal_set_from_ros2 = set_from_ros2_cpp[Group + '/' + info['NameCap'] + '_SendGoal']
                idx = goal_set_from_ros2.find('data.')+4
                info['GoalSetFromROS2'] = goal_set_from_ros2[:idx] + '.goal' + goal_set_from_ros2[idx:]
                goal_set_ros2 = set_ros2_cpp[Group + '/' + info['NameCap'] + '_SendGoal']
                idx = goal_set_ros2.find('data.')+4
                info['GoalSetROS2'] = goal_set_ros2[:idx] + '.goal' + goal_set_ros2[idx:]
                
                info['ResultTypes'] = types_cpp[Group + '/' + info['NameCap'] + '_GetResult']
                result_set_from_ros2 = set_from_ros2_cpp[Group + '/' + info['NameCap'] + '_GetResult']
                idx = result_set_from_ros2.find('data.')+4
                info['ResultSetFromROS2'] = result_set_from_ros2[:idx] + '.result' + result_set_from_ros2[idx:]
                result_set_ros2 = set_ros2_cpp[Group + '/' + info['NameCap'] + '_GetResult']
                idx = result_set_ros2.find('data.')+4
                info['ResultSetROS2'] = result_set_ros2[:idx] + '.result' + result_set_ros2[idx:]
                
                info['FeedbackTypes'] = types_cpp[Group + '/' + info['NameCap'] + '_Feedback']
                feedback_set_from_ros2 = set_from_ros2_cpp[Group + '/' + info['NameCap'] + '_Feedback']
                idx = feedback_set_from_ros2.find('data.')+4
                info['FeedbackSetFromROS2'] = feedback_set_from_ros2[:idx] + '.feedback' + feedback_set_from_ros2[idx:]
                feedback_set_ros2 = set_ros2_cpp[Group + '/' + info['NameCap'] + '_Feedback']
                idx = feedback_set_ros2.find('data.')+4
                info['FeedbackSetROS2'] = feedback_set_ros2[:idx] + '.feedback' + feedback_set_ros2[idx:]

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
