from jinja2 import Environment, FileSystemLoader
from numpy.lib.stride_tricks import as_strided
import sys
import os
import glob
import re
import pandas as pd

def snake_to_pascal(in_text):
    if '_' in in_text:
        return in_text.replace("_", " ").title().replace(" ", "")
    elif in_text.islower():
        return in_text.title()
    else:
        return in_text

def remove_underscore(in_text):
    return in_text.replace("_", "")

# generate variable name for UE C++
# original_names: member names defined in .msg, .srv, .action
# return {(type, size): var_name}
def get_ue_var_name(original_names = {}, is_dynamic_array = False):
    if len(original_names) == 2:
        var_type = original_names[0]
        if '[' not in original_names[0] and ']' not in original_names[0] and is_dynamic_array:
            var_type += '[]'

        var_name = snake_to_pascal(original_names[1])
        if ('bool' == var_type):
            var_name = f'b{var_name}'
        return {convert_to_ue_type(var_type): var_name}
    elif len(original_names) == 3:
        res_ue = {}
        final = {}
        for v in original_names[2]:
            is_dynamic_array_var = is_dynamic_array
            if '[]' in v[0]:
                is_dynamic_array_var = True
            res_ue = get_ue_var_name(v, is_dynamic_array_var)
            for t_ue, v_ue in res_ue.items():
                # Type, Size, Var name (snake_case -> PascalCase)
                final[t_ue] = f'{snake_to_pascal(original_names[1])}{v_ue}'
        return final
    else:
        print('ERROR with ' + str(original_names) + ' (get_ue_var_name)')
        return '',''

# generate msg variable access for ROS msg
# original_names: member names defined in .msg, .srv, .action
def get_ros_var_name(original_names = {}, is_dynamic_array = False):
    if len(original_names) == 2:
        vartype = original_names[0]
        varname = original_names[1]
        if '[]' not in original_names[0] and is_dynamic_array:
            vartype += '[]'
        if '[]' in original_names[0]:
            varname += '.data[i]'
        return [str(vartype), str(varname)]
    elif len(original_names) == 3:
        res = []
        final = []
        for v in original_names[2]:
            is_dynamic_array_var = is_dynamic_array
            if '[]' in v[0]:
                is_dynamic_array_var = True
            res = get_ros_var_name(v, is_dynamic_array_var)
            it = iter(res)
            for r in it:
                final.append(r)
                if '[]' in original_names[0]:
                    final.append(original_names[1] + '.data[i].' + next(it))
                else:
                    final.append(original_names[1] + '.' + next(it))
        return final
    else:
        print('ERROR with ' + str(original_names) + ' (get_ros_var_name)')
    return '',''

# UE BP-supported types only?
def convert_to_ue_type(t):
    size = 0
    if t == 'int32':
        t = 'int'
    elif t == 'uint32':
        t = 'unsigned int'
    elif t == 'byte':
        t = 'uint8'
    elif t == 'char':
        t = 'uint8'
    elif t == 'float32':
        t = 'float'
    elif t == 'float64':
        t = 'double'
    elif t == 'string':
        t = 'FString'
    elif t == 'Vector3' or t == 'Point32':
        t = 'FVector'
    elif t == 'Quaternion':
        t = 'FQuat'
    elif '[]' in t:
        t = t.replace('[]','')
        t = f'TArray<{convert_to_ue_type(t)[0]}>'
    elif ('[' in t) and (']' in t):
        tmp = re.split('\[|\]', t)
        size = tmp[1].replace('<=','')
        t = f'TArray<{convert_to_ue_type(tmp[0])[0]}>'
    #elif t == 'geometry_msgs/Pose': -> {FRRDoubleVector, FQuat}
    #elif t == 'geometry_msgs/Twist': -> {FVector TwistLinear, FVector TwistAngular}
    return (t, size)

def get_type_default_value_str(t):
    if 'bool' == t:
        return 'false'
    if 'int' in t:
        return '0'
    elif 'float' in t:
        return '0.f'
    elif 'double' == t:
        return '0.f'
    elif 'FVector' == t:
        return 'FVector::ZeroVector'
    elif 'FQuat' == t:
        return 'FQuat::Identity'
    elif 'FTransform' == t:
        return 'FTransform::Identity'
    return None

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
def setter(r, v_ue, v_ros, size):
    if r == 'FVector':
        return v_ue + '.X = in_ros_data.' + v_ros + '.x;\n\t\t' + v_ue + '.Y = in_ros_data.' + v_ros + '.y;\n\t\t' + v_ue + '.Z = in_ros_data.' + v_ros + '.z;\n\n\t\t'
    elif r == 'FQuat':
        return v_ue + '.X = in_ros_data.' + v_ros + '.x;\n\t\t' + v_ue + '.Y = in_ros_data.' + v_ros + '.y;\n\t\t' + v_ue + '.Z = in_ros_data.' + v_ros + '.z;\n\t\t' + v_ue + '.W = in_ros_data.' + v_ros + '.w;\n\n\t\t'
    elif r == 'FString':
        return v_ue + '.AppendChars(in_ros_data.' + v_ros + '.data, in_ros_data.' + v_ros + '.size);\n\n\t\t'
    elif 'TArray' in r:
        if 'FVector' in r:
            if size > 0:
                return 'for (auto i = 0; i < ' + str(size) + '; ++i)\n\t\t{\n\t\t\t' \
                    + v_ue + '.Add(FVector::ZeroVector);\n\t\t\t' \
                    + v_ue + '[i].X = in_ros_data.' + v_ros + '[i].x;\n\t\t\t' \
                    + v_ue + '[i].Y = in_ros_data.' + v_ros + '[i].y;\n\t\t\t' \
                    + v_ue + '[i].Z = in_ros_data.' + v_ros + '[i].z;\n\t\t}\n\n\t\t'
            else:
                # need to identify multidimensional arrays - need some sort of recursion with splits
                v_ros_size = v_ros.split('.data[i]',1)[0]
                return 'for (auto i = 0; i < in_ros_data.' + v_ros_size + '.size; ++i)\n\t\t{\n\t\t\t' \
                    + v_ue + '.Add(FVector::ZeroVector);\n\t\t\t' \
                    + v_ue + '[i].X = in_ros_data.' + v_ros + '.x;\n\t\t\t' \
                    + v_ue + '[i].Y = in_ros_data.' + v_ros + '.y;\n\t\t\t' \
                    + v_ue + '[i].Z = in_ros_data.' + v_ros + '.z;\n\t\t}\n\n\t\t'
        elif 'FQuat' in r:
            if size > 0:
                return 'for (auto i = 0; i < ' + str(size) + '; ++i)\n\t\t{\n\t\t\t' \
                    + v_ue + '.Add(FQuat::Identity);\n\t\t\t' \
                    + v_ue + '[i].X = in_ros_data.' + v_ros + '[i].x;\n\t\t\t' \
                    + v_ue + '[i].Y = in_ros_data.' + v_ros + '[i].y;\n\t\t\t' \
                    + v_ue + '[i].Z = in_ros_data.' + v_ros + '[i].z;\n\t\t}\n\n\t\t'
            else:
                # need to identify multidimensional arrays - need some sort of recursion with splits
                v_ros_size = v_ros.split('.data[i]',1)[0]
                return 'for (auto i = 0; i < in_ros_data.' + v_ros_size + '.size; ++i)\n\t\t{\n\t\t\t' \
                    + v_ue + '.Add(FQuat::Identity);\n\t\t\t' \
                    + v_ue + '[i].X = in_ros_data.' + v_ros + '.x;\n\t\t\t' \
                    + v_ue + '[i].Y = in_ros_data.' + v_ros + '.y;\n\t\t\t' \
                    + v_ue + '[i].Z = in_ros_data.' + v_ros + '.z;\n\t\t\t' \
                    + v_ue + '[i].W = in_ros_data.' + v_ros + '.w;\n\t\t}\n\n\t\t'
        elif 'FString' in r:
            if size > 0:
                return 'for (auto i = 0; i < ' + str(size) + '; ++i)\n\t\t{\n\t\t\t' \
                    + v_ue + '.Add("");\n\t\t\t' \
                    + v_ue + '[i].AppendChars(in_ros_data.' + v_ros + '.data, in_ros_data.' + v_ros + '.size);\n\t\t}\n\n\t\t'
            else:
                # need to identify multidimensional arrays - need some sort of recursion with splits
                v_ros_size = v_ros.split('.data[i]',1)[0]
                return 'for (auto i = 0; i < in_ros_data.' + v_ros_size + '.size; ++i)\n\t\t{\n\t\t\t' \
                    + v_ue + '.Add("");\n\t\t\t' \
                    + v_ue + '[i].AppendChars(in_ros_data.' + v_ros + '.data,in_ros_data.' + v_ros + '.size);\n\t\t}\n\n\t\t'
        else:
            if size > 0:
                return 'for (auto i = 0; i < ' + str(size) + '; ++i)\n\t\t{\n\t\t\t' + v_ue + '.Add(in_ros_data.' + v_ros + '[i]);\n\t\t}\n\n\t\t'
            else:
                # need to identify multidimensional arrays - need some sort of recursion with splits
                v_ros_size = v_ros.split('.data[i]',1)[0]
                return 'for (auto i = 0; i < in_ros_data.' + v_ros_size + '.size; ++i)\n\t\t{\n\t\t\t' + v_ue + '.Add(in_ros_data.' + v_ros + ');\n\t\t}\n\n\t\t'
    else:
        return v_ue + ' = in_ros_data.' + v_ros + ';\n\n\t\t'

def cpp2ros_vector(v_ros, v_ue, comp, is_array = False, is_fixed_size = False):
    iterator = ''
    iterator_ros = ''
    component = ''
    if comp != '':
        component = '.' + comp
    if is_array and is_fixed_size:
        iterator_ros = '[i]'
    if is_array:
        iterator = '[i]'
    return 'out_ros_data.' + v_ros + iterator_ros + component.lower() + ' = ' + v_ue + iterator + component.upper() + ';'

def free_and_malloc(v_ros, v_ue, type, Free=True):
    alloc_type = 'decltype(*out_ros_data.' + v_ros + '.data)'
    alloc_type_cast = 'decltype(out_ros_data.' + v_ros + '.data)'
    size = '(' + v_ue + '.Num())'
    if type == 'FString':
        size = '(strLength+1)'
    elif type == 'FVector':
        size = '(' + v_ue + '.Num() * 3)'
    elif type == 'FQuat':
        size = '(' + v_ue + '.Num() * 4)'
    free_mem = ''
    if Free:
        free_mem = 'if (out_ros_data.' + v_ros + '.data != nullptr)\n\t\t{\n\t\t\t'\
                 + 'free(out_ros_data.' + v_ros + '.data);\n\t\t}\n\t\t'
    return  free_mem \
            + 'out_ros_data.' + v_ros + '.data = (' + alloc_type_cast + ')malloc(' + size + '*sizeof(' + alloc_type + '));\n\t\t'

# generate code for getterAoS - Array-of-Structures (SetROS2)
def getterAoS(r, v_ue, v_ros, size):
    if r == 'FVector':
        return cpp2ros_vector(v_ros, v_ue, 'x') + '\n\t\t' \
             + cpp2ros_vector(v_ros, v_ue, 'y') + '\n\t\t' \
             + cpp2ros_vector(v_ros, v_ue, 'z') + '\n\n\t\t'
    elif r == 'FQuat':
        return cpp2ros_vector(v_ros, v_ue, 'x') + '\n\t\t' \
             + cpp2ros_vector(v_ros, v_ue, 'y') + '\n\t\t' \
             + cpp2ros_vector(v_ros, v_ue, 'z') + '\n\t\t' \
             + cpp2ros_vector(v_ros, v_ue, 'w') + '\n\n\t\t'
    elif r == 'FString':  
        return '{\n\t\t\t' \
            + 'FTCHARToUTF8 strUtf8( *' + v_ue + ' );\n\t\t\tint32 strLength = strUtf8.Length();\n\t\t\t' \
            + free_and_malloc(v_ros, v_ue, r) \
            + 'memcpy(out_ros_data.' + v_ros + '.data, TCHAR_TO_UTF8(*' + v_ue + '), (strLength+1)*sizeof(char));\n\t\t\t' \
            + 'out_ros_data.' + v_ros + '.size = strLength;\n\t\t\t' \
            + 'out_ros_data.' + v_ros + '.capacity = strLength + 1;\n\t\t' \
            + '}\n\n\t\t'
    elif 'TArray' in r:
        for_loop_fixed = 'for (auto i = 0; i < ' + str(size) + '; ++i)\n\t\t{\n\t\t\t'
        for_loop_dynamic = 'for (auto i = 0; i < ' + v_ue + '.Num(); ++i)\n\t\t{\n\t\t\t'
        if 'FVector' in r:
            if size > 0:
                return for_loop_fixed \
                    + cpp2ros_vector(v_ros, v_ue, 'x', True, True) + '\n\t\t\t' \
                    + cpp2ros_vector(v_ros, v_ue, 'y', True, True) + '\n\t\t\t' \
                    + cpp2ros_vector(v_ros, v_ue, 'z', True, True) + '\n\t\t}\n\n\t\t'
            else:
                # need to identify multidimensional arrays - need some sort of recursion with splits
                v_ros_size = v_ros.split('.data[i]',1)[0]
                return free_and_malloc(v_ros_size, v_ue, 'FVector') + '\n\t\t' \
                    + for_loop_dynamic \
                    + cpp2ros_vector(v_ros, v_ue, 'x', True, False) + '\n\t\t\t' \
                    + cpp2ros_vector(v_ros, v_ue, 'y', True, False) + '\n\t\t\t' \
                    + cpp2ros_vector(v_ros, v_ue, 'z', True, False) + '\n\t\t}\n\n\t\t' \
                    + 'out_ros_data.' + v_ros_size + '.size = ' + v_ue + '.Num();\n\t\t' \
                    + 'out_ros_data.' + v_ros_size + '.capacity = ' + v_ue + '.Num();\n\n\t\t'
        elif 'FQuat' in r:
            if size > 0:
                return for_loop_fixed \
                    + cpp2ros_vector(v_ros, v_ue, 'x', True, True) + '\n\t\t\t' \
                    + cpp2ros_vector(v_ros, v_ue, 'y', True, True) + '\n\t\t\t' \
                    + cpp2ros_vector(v_ros, v_ue, 'z', True, True) + '\n\t\t\t' \
                    + cpp2ros_vector(v_ros, v_ue, 'w', True, True) + '\n\t\t}\n\n\t\t'
            else:
                # need to identify multidimensional arrays - need some sort of recursion with splits
                v_ros_size = v_ros.split('.data[i]',1)[0]
                return free_and_malloc(v_ros_size, v_ue, 'FQuat') + '\n\t\t' \
                    + for_loop_dynamic \
                    + cpp2ros_vector(v_ros, v_ue, 'x', True, False) + '\n\t\t\t' \
                    + cpp2ros_vector(v_ros, v_ue, 'y', True, False) + '\n\t\t\t' \
                    + cpp2ros_vector(v_ros, v_ue, 'z', True, False) + '\n\t\t\t' \
                    + cpp2ros_vector(v_ros, v_ue, 'w', True, False) + '\n\t\t}\n\n\t\t' \
                    + 'out_ros_data.' + v_ros_size + '.size = ' + v_ue + '.Num();\n\t\t' \
                    + 'out_ros_data.' + v_ros_size + '.capacity = ' + v_ue + '.Num();\n\n\t\t'
        elif 'FString' in r:
            if size > 0:
                return for_loop_fixed \
                    + '{\n\t\t\t' \
                    + 'FTCHARToUTF8 strUtf8( *' + v_ue + '[i] );\n\t\t\t\tint32 strLength = strUtf8.Length();\n\t\t\t' \
                    + 'if (out_ros_data.' + v_ros + '.data != nullptr)\n\t\t\t\t{\n\t\t\t\t\t' \
                    + 'free(out_ros_data.' + v_ros + '.data);\n\t\t\t\t}\n\t\t\t\t' \
                    + 'out_ros_data.' + v_ros + '.data = (char*)malloc((strLength+1)*sizeof(char));\n\t\t\t\t' \
                    + 'memcpy(out_ros_data.' + v_ros + '.data, TCHAR_TO_UTF8(*' + v_ue + '[i]), (strLength+1)*sizeof(char));\n\t\t\t\t' \
                    + 'out_ros_data.' + v_ros + '.size = strLength;\n\t\t\t\t' \
                    + 'out_ros_data.' + v_ros + '.capacity = strLength + 1;\n\t\t\t}\n\n\t\t' \
                    + '}\n\n\t\t'
            else:
                # need to identify multidimensional arrays - need some sort of recursion with splits
                v_ros_size = v_ros.split('.data[i]',1)[0]
                return free_and_malloc(v_ros_size.split('[i]',1)[0], v_ue, 'Pointer') \
                    + for_loop_dynamic \
                    + '{\n\t\t\t\t' \
                    + 'FTCHARToUTF8 strUtf8( *' + v_ue + '[i] );\n\t\t\t\t' \
                    + 'int32 strLength = strUtf8.Length();\n\t\t\t\t' \
                    + 'if (out_ros_data.' + v_ros + '.data != nullptr)\n\t\t\t\t{\n\t\t\t\t\t' \
                    + 'free(out_ros_data.' + v_ros + '.data);\n\t\t\t\t}\n\t\t\t\t' \
                    + 'out_ros_data.' + v_ros + '.data = (char*)malloc((strLength+1)*sizeof(char));\n\t\t\t\t' \
                    + 'memcpy(out_ros_data.' + v_ros + '.data, TCHAR_TO_UTF8(*' + v_ue + '[i]), (strLength+1)*sizeof(char));\n\t\t\t\t' \
                    + 'out_ros_data.' + v_ros + '.size = strLength;\n\t\t\t\t' \
                    + 'out_ros_data.' + v_ros + '.capacity = strLength + 1;\n\t\t\t}\n\t\t' \
                    + '}\n\n\t\t'
        else:
            if size > 0:
                return for_loop_fixed \
                    + cpp2ros_vector(v_ros, v_ue, '', True, True) + '\n\t\t}\n\n\t\t'
            else:
                # need to identify multidimensional arrays - need some sort of recursion with splits
                v_ros_size = v_ros.split('.data[i]',1)[0]
                cpp_base_type = r.split('>',1)[0].split('TArray<',1)[1]
                return free_and_malloc(v_ros_size, v_ue, cpp_base_type) + '\n\t\t' \
                    + for_loop_dynamic \
                    + cpp2ros_vector(v_ros, v_ue, '', True, False) + '\n\t\t}\n\n\t\t' \
                    + 'out_ros_data.' + v_ros_size + '.size = ' + v_ue + '.Num();\n\t\t' \
                    + 'out_ros_data.' + v_ros_size + '.capacity = ' + v_ue + '.Num();\n\n\t\t'
    else:
        return 'out_ros_data.' + v_ros + ' = ' + v_ue + ';\n\n\t\t'

def free_and_malloc_SoA(v_ros, v_ue, type):
    alloc_type = 'decltype(*out_ros_data.' + v_ros + '.data)'
    alloc_type_cast = 'decltype(out_ros_data.' + v_ros + '.data)'
    size = '(' + v_ue + '.Num())'
    if type == 'FString':
        size = '(strLength+1)'
    elif type == 'FVector':
        size = '(' + v_ue + '.Num() * 3)'
    elif type == 'FQuat':
        size = '(' + v_ue + '.Num() * 4)'
    return 'if (out_ros_data.' + v_ros + '.data != nullptr)\n\t\t{\n\t\t\t' \
            + 'free(out_ros_data.' + v_ros + '.data);\n\t\t}\n\t\t' \
            + 'out_ros_data.' + v_ros + '.data = (' + alloc_type_cast + ')malloc(' + size + '*sizeof(' + alloc_type + '));\n\t\t'

# generate code for getterSoA - Structure-of-Arrays (SetROS2)
def getterSoA(r_array, v_ue_array, v_ros_array, size_array):
    # WARNING: there could be multiple groups of SoA - need to go by matching substrings in v_ros_array
    SoAs_ros = {}
    SoAs_types = {}
    SoAs_r = {}
    for e in range(len(v_ros_array)):
        if v_ros_array[e].split('.data[i].')[0] in SoAs_ros:
            SoAs_ros[v_ros_array[e].split('.data[i].')[0]].append(v_ros_array[e])
            SoAs_types[v_ros_array[e].split('.data[i].')[0]].append(v_ue_array[e])
            SoAs_r[v_ros_array[e].split('.data[i].')[0]].append(r_array[e])
        else:
            SoAs_ros[v_ros_array[e].split('.data[i].')[0]] = [v_ros_array[e]]
            SoAs_types[v_ros_array[e].split('.data[i].')[0]] = [v_ue_array[e]]
            SoAs_r[v_ros_array[e].split('.data[i].')[0]] = [r_array[e]]

    malloc_size = {}
    for t in SoAs_types:
        if t not in malloc_size:
            malloc_size[t] = ''
        malloc_size[t] += SoAs_types[t][0] + '.Num() * '
        malloc_size[t] += '('
        for e in SoAs_types[t]:
            malloc_size[t] += 'sizeof(' + e + ') + '
        malloc_size[t] = malloc_size[t][:-3]
        malloc_size[t] += ')'

    getterSoA_result = ''
    for t in SoAs_types:
        # free_and_malloc
        getterSoA_result += 'if (out_ros_data.' + t + '.data != nullptr)\n\t\t{\n\t\t\t' \
            + 'free(out_ros_data.' + t + '.data);\n\t\t}\n\t\t' \
            + 'out_ros_data.' + t + '.data = (decltype(out_ros_data.' + t + '.data))malloc(' + malloc_size[t] + ');\n\t\t' \
            + 'out_ros_data.' + t + '.size = ' + SoAs_types[t][0] + '.Num();\n\t\t' \
            + 'out_ros_data.' + t + '.capacity = ' + SoAs_types[t][0] + '.Num();\n\t\t'
        # fill
        getterSoA_result += 'for (auto i = 0; i < ' + SoAs_types[t][0] + '.Num(); ++i)\n\t\t{\n\t\t\t'
        for i in range(len(SoAs_types[t])):
            v_ue = SoAs_types[t][i]
            v_ros = SoAs_ros[t][i]
            r = SoAs_r[t][i]
            if 'TArray' in r:
                r = r.split('<',1)[1].split('>')[0]
            if r == 'FVector':
                getterSoA_result += cpp2ros_vector(v_ros, v_ue, 'x', True, False) + '\n\t\t\t' \
                                  + cpp2ros_vector(v_ros, v_ue, 'y', True, False) + '\n\t\t\t' \
                                  + cpp2ros_vector(v_ros, v_ue, 'z', True, False) + '\n\n\t\t\t'
            elif r == 'FQuat':
                getterSoA_result += cpp2ros_vector(v_ros, v_ue, 'x', True, False) + '\n\t\t\t' \
                                  + cpp2ros_vector(v_ros, v_ue, 'y', True, False) + '\n\t\t\t' \
                                  + cpp2ros_vector(v_ros, v_ue, 'z', True, False) + '\n\t\t\t' \
                                  + cpp2ros_vector(v_ros, v_ue, 'w', True, False) + '\n\n\t\t\t'
            elif r == 'FString':  
                getterSoA_result += '{\n\t\t\t\t' \
                    + 'FTCHARToUTF8 strUtf8( *' + v_ue + '[i] );\n\t\t\tint32 strLength = strUtf8.Length();\n\t\t\t\t' \
                    + free_and_malloc(v_ros, v_ue, r, False) \
                    + 'memcpy(out_ros_data.' + v_ros + '.data, TCHAR_TO_UTF8(*' + v_ue + '[i]), (strLength+1)*sizeof(char));\n\t\t\t\t' \
                    + 'out_ros_data.' + v_ros + '.size = strLength;\n\t\t\t\t' \
                    + 'out_ros_data.' + v_ros + '.capacity = strLength + 1;\n\t\t\t' \
                    + '}\n\n\t\t\t'
            elif 'TArray' in r:
                getterSoA_result += '\t\t\tUE_LOG(LogTemp, Error, TEXT("Not Implemented Yet!"));\n\n'
            else:
                getterSoA_result += 'out_ros_data.' + v_ros + ' = ' + v_ue + '[i];\n\n\t\t\t'
        getterSoA_result += '}\n\t'

    return getterSoA_result


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
                struct_type = el[len(el)-3] + '/' + remove_underscore(os.path.splitext(os.path.basename(fp))[0])
                types.add(struct_type)
    
    #print(types)

    return types


# create a dictionary matching types with the corresponding expanded contents expressed with basic types
def get_types_dict(target_paths):
    types_dict = {}
    types = get_types(target_paths)

    # for every folder to scan
    for target_path in target_paths:

        # for every type
        for t in types:
            tSplit = t.split('/')
            tRequest = f'{t}Request'
            tResponse = f'{t}Response'
            tSendGoal = f'{t}SendGoal'
            tGetResult = f'{t}GetResult'
            tFeedback = f'{t}Feedback'

            # iterate all subfolders
            for subdir, dirs, files in os.walk(target_path):

                # iterate over all msg, srv and action files
                files = [ fi for fi in files if fi.endswith(('.msg','.srv','.action')) ]
                for fi in files:
                    content = []

                    # if the file corresponds to the type t being processed
                    fi_name = os.path.splitext(fi)[0]
                    struct_type = remove_underscore(fi_name)
                    if (len(tSplit) == 1 and (struct_type == t)) or (len(tSplit) == 2 and (tSplit[0] in subdir) and (struct_type == tSplit[1])):

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

                        if fi.endswith('.msg'):
                            # remove comments, empty and separator lines; keep only variable type and name
                            content = [ c.split()[0:2] for c in content if  c != '---' ]
                            #content = [ c for c in content if '=' not in c[1] ] # ignore constants
                            types_dict[t] = content
                        elif fi.endswith('.srv'):
                            content = [ c.split()[0:2] for c in content ]
                            counter = 0
                            for c in content:
                                if not c == ['---']:
                                    if counter == 0:
                                        if (tRequest in types_dict) and (c not in types_dict[tRequest]):
                                            types_dict[tRequest].append(c)
                                        else:
                                            types_dict[tRequest] = [c]
                                    elif counter == 1:
                                        if (tResponse in types_dict) and (c not in types_dict[tResponse]):
                                            types_dict[tResponse].append(c)
                                        else:
                                            types_dict[tResponse] = [c]
                                else:
                                    counter += 1
                        elif fi.endswith('.action'):
                            # remove comments and empty lines; keep only variable type and name
                            content = [ c.split()[0:2] for c in content ]
                            counter = 0
                            for c in content:
                                if not c == ['---']:
                                    if '=' not in c[1]:
                                        if counter == 0:
                                            if (tSendGoal in types_dict) and (c not in types_dict[tSendGoal]):
                                                types_dict[tSendGoal].append(c)
                                            else:
                                                types_dict[tSendGoal] = [c]
                                        elif counter == 1:
                                            if (tGetResult in types_dict) and (c not in types_dict[tGetResult]):
                                                types_dict[tGetResult].append(c)
                                            else:
                                                types_dict[tGetResult] = [c]
                                        elif counter == 2:
                                            if (tFeedback in types_dict) and (c not in types_dict[tFeedback]):
                                                types_dict[tFeedback].append(c)
                                            else:
                                                types_dict[tFeedback] = [c]
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


# generate UE & ROS C++ code snippets to be inserted in their respective placeholders in the templates
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
            is_dynamic_array = False
            if '[]' in v[0]:
                is_dynamic_array = True

            res_ue = get_ue_var_name(v, is_dynamic_array)
            #print("res_ue", res_ue)
            res_ros = get_ros_var_name(v, is_dynamic_array)
            #print("res_ros", res_ros)

            t_ue_array = []
            v_ue_array = []
            v_ros_array = []
            size_array = []

            it_ros = iter(res_ros)
            for t_ue, v_ue in res_ue.items():
                size = int(t_ue[1])
                
                # ros_type
                next(it_ros)
                # ros_var
                v_ros = next(it_ros)
                
                # BP does not support these types
                dft_val = get_type_default_value_str(t_ue[0])
                var_initialization = f' = {dft_val}' if (dft_val != None) else ''
                var_declaration = f'{t_ue[0]} {v_ue}{var_initialization};\n\n\t'
                if (('unsigned int' in t_ue[0]) or
                    ('double' in t_ue[0]) or
                    ('int8' in t_ue[0]) or
                    ('int16' in t_ue[0]) or
                    ('uint16' in t_ue[0]) or
                    ('uint64' in t_ue[0])):
                    cpp_type += 'UPROPERTY(EditAnywhere)\n\t' + var_declaration
                else:
                    cpp_type += 'UPROPERTY(EditAnywhere, BlueprintReadWrite)\n\t' + var_declaration
                set_from_ros2 += setter(t_ue[0], v_ue, v_ros, size)

                if '.data[i].' not in v_ros:
                    set_ros2 += getterAoS(t_ue[0], v_ue, v_ros, size)
                else:
                    t_ue_array.append(t_ue[0])
                    v_ue_array.append(v_ue)
                    v_ros_array.append(v_ros)
                    size_array.append(size)

            # if any('.data[i].' in vr for vr in v_ros_array) and any('fields_' in vt for vt in v_ue_array) and not any('_fields_' in vt for vt in v_ue_array):
            #     print('getter with:\n' + str(t_ue_array) + '\n' + str(v_ue_array) + '\n' + str(v_ros_array) + '\n' + str(size_array))

            if len(t_ue_array) > 0:
                set_ros2 += getterSoA(t_ue_array, v_ue_array, v_ros_array, size_array)
                

        types_cpp[key] = [cpp_type, set_from_ros2, set_ros2]

    
    #for key, value in types_cpp.items():
    #    print(str(key) + ' -> ' + str(value[2]))
    #    print(str(key) + ' -> ' + str(value[0]))

    return types_cpp

file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)

current_dir = os.getcwd()

ros_paths = [sys.argv[1]]
ue_paths = []
Groups = []
for i in range(2,len(sys.argv)):
    ue_paths.append(sys.argv[i])
    if '/share/' in sys.argv[i]:
        ros_paths.append(os.path.split(os.path.dirname(sys.argv[i]))[0])
    else:
        ros_paths.append(sys.argv[i])
    Groups.append(os.path.basename(os.path.dirname(sys.argv[i])))

types_cpp = get_types_cpp(ros_paths)
def is_valid_group_name(in_group_name):
    return ((in_group_name in types_cpp) and len(types_cpp[in_group_name]) >= 3)

def print_group_name_info(in_group_name):
    print(f"types_cpp[{in_group_name}] size:{len(types_cpp[in_group_name]) if (in_group_name in types_cpp) else 0}")

# generate code
for p in range(len(ue_paths)):
    for subdir in ['action','srv','msg']:
        if os.path.exists(ue_paths[p]+'/'+subdir):
            os.chdir(ue_paths[p]+'/'+subdir)
            for file in glob.glob('*.'+subdir):
                package_name = os.path.split(os.path.split(ue_paths[p])[0])[1]
                #print(package_name + '/' + file)

                if check_deprecated(ue_paths[p], subdir, file):
                    continue
                
                info = {}
                info['Filename'] = package_name + '/' + file
                info['Group'] = Groups[p]
                name = os.path.splitext(file)[0]
                # PascalCase to snake_case; correctly handles acronyms: TLA -> tla instead of t_l_a
                name_lower = re.sub('([a-z0-9])([A-Z])', r'\1_\2', re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)).lower()
                info['Name'] = name_lower
                info['NameCap'] = name
                info['StructName'] = 'ROS' + info['NameCap']
                
                p_group_name = f"{Groups[p]}/{name}"
                group_name = p_group_name
                if subdir == 'msg':
                    if(is_valid_group_name(group_name)):
                        info['Types'] = types_cpp[group_name][0]
                        info['SetFromROS2'] = types_cpp[group_name][1]
                        info['SetROS2'] = types_cpp[group_name][2]
                    else:
                        print_group_name_info(group_name)

                elif subdir == 'srv':
                    group_name = f"{p_group_name}Request"
                    if(is_valid_group_name(group_name)):
                        info['ReqTypes'] = types_cpp[group_name][0]
                        info['ReqSetFromROS2'] = types_cpp[group_name][1]
                        info['ReqSetROS2'] = types_cpp[group_name][2]
                    else:
                        print_group_name_info(group_name)

                    group_name = f"{p_group_name}Response"
                    if(is_valid_group_name(group_name)):
                        info['ResTypes'] = types_cpp[group_name][0]
                        info['ResSetFromROS2'] = types_cpp[group_name][1]
                        info['ResSetROS2'] = types_cpp[group_name][2]
                    else:
                        print_group_name_info(group_name)

                elif subdir == 'action':
                    group_name = f"{p_group_name}SendGoal"
                    if(is_valid_group_name(group_name)):
                        info['GoalTypes'] = types_cpp[group_name][0]
                        info['GoalSetFromROS2'] = types_cpp[group_name][1].replace('in_ros_data.','in_ros_data.goal.')
                        info['GoalSetROS2'] = types_cpp[group_name][2].replace('out_ros_data.','out_ros_data.goal.')
                    else:
                        print_group_name_info(group_name)

                    group_name = f"{p_group_name}GetResult"
                    if(is_valid_group_name(group_name)):
                        info['ResultTypes'] = types_cpp[group_name][0]
                        info['ResultSetFromROS2'] = types_cpp[group_name][1].replace('in_ros_data.','in_ros_data.result.')
                        info['ResultSetROS2'] = types_cpp[group_name][2].replace('out_ros_data.','out_ros_data.result.')
                    else:
                        print_group_name_info(group_name)

                    group_name = f"{p_group_name}Feedback"
                    if(is_valid_group_name(group_name)):
                        info['FeedbackTypes'] = types_cpp[group_name][0]
                        info['FeedbackSetFromROS2'] = types_cpp[group_name][1].replace('in_ros_data.','in_ros_data.feedback.')
                        info['FeedbackSetROS2'] = types_cpp[group_name][2].replace('out_ros_data.','out_ros_data.feedback.')
                    else:
                        print_group_name_info(group_name)

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
