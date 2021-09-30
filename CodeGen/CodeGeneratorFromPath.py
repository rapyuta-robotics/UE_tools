from jinja2 import Environment, FileSystemLoader
from numpy.lib.stride_tricks import as_strided
import sys
import os
import glob
import re
import pandas as pd

# generate variable name for C++
def get_var_name(curval = {}, is_dynamic_array = False):
    if len(curval) == 2:
        vartype = curval[0]
        if '[' not in curval[0] and ']' not in curval[0] and is_dynamic_array:
            vartype += '[]'
        return [str(vartype), str(curval[1])]
    elif len(curval) == 3:
        res = []
        final = []
        for v in curval[2]:
            is_dynamic_array_var = is_dynamic_array
            if '[]' in v[0]:
                is_dynamic_array_var = True
            res = get_var_name(v, is_dynamic_array_var)
            it = iter(res)
            for r in it:
                final.append(r)
                final.append(curval[1] + '_' + next(it))
        return final
    else:
        print('ERROR with ' + str(curval) + ' (get_var_name)')
    return '',''

# generate msg variable access for ROS msg
def get_ros_var_name(curval = {}, is_dynamic_array = False):
    if len(curval) == 2:
        vartype = curval[0]
        varname = curval[1]
        if '[]' not in curval[0] and is_dynamic_array:
            vartype += '[]'
        if '[]' in curval[0]:
            varname += '.data[i]'
        return [str(vartype), str(varname)]
    elif len(curval) == 3:
        res = []
        final = []
        for v in curval[2]:
            is_dynamic_array_var = is_dynamic_array
            if '[]' in v[0]:
                is_dynamic_array_var = True
            res = get_ros_var_name(v, is_dynamic_array_var)
            it = iter(res)
            for r in it:
                final.append(r)
                if '[]' in curval[0]:
                    final.append(curval[1] + '.data[i].' + next(it))
                else:
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
        return v_type + '.X = in_ros_data.' + v_ros + '.x;\n\t\t' + v_type + '.Y = in_ros_data.' + v_ros + '.y;\n\t\t' + v_type + '.Z = in_ros_data.' + v_ros + '.z;\n\n\t\t'
    elif r == 'FQuat':
        return v_type + '.X = in_ros_data.' + v_ros + '.x;\n\t\t' + v_type + '.Y = in_ros_data.' + v_ros + '.y;\n\t\t' + v_type + '.Z = in_ros_data.' + v_ros + '.z;\n\t\t' + v_type + '.W = in_ros_data.' + v_ros + '.w;\n\n\t\t'
    elif r == 'FString':
        return v_type + '.AppendChars(in_ros_data.' + v_ros + '.data, in_ros_data.' + v_ros + '.size);\n\n\t\t'
    elif 'TArray' in r:
        if 'FVector' in r:
            if size > 0:
                return 'for (int i = 0; i < ' + str(size) + '; i++)\n\t\t{\n\t\t\t' \
                    + v_type + '[i].X = in_ros_data.' + v_ros + '[i].x;\n\t\t\t' \
                    + v_type + '[i].Y = in_ros_data.' + v_ros + '[i].y;\n\t\t\t' \
                    + v_type + '[i].Z = in_ros_data.' + v_ros + '[i].z;\n\t\t}\n\n\t\t'
            else:
                # need to identify multidimensional arrays - need some sort of recursion with splits
                v_ros_size = v_ros.split('.data[i]',1)[0]
                return 'for (int i = 0; i < in_ros_data.' + v_ros_size + '.size; i++)\n\t\t{\n\t\t\t' \
                    + v_type + '[i].X = in_ros_data.' + v_ros + '.x;\n\t\t\t' \
                    + v_type + '[i].Y = in_ros_data.' + v_ros + '.y;\n\t\t\t' \
                    + v_type + '[i].Z = in_ros_data.' + v_ros + '.z;\n\t\t}\n\n\t\t'
        elif 'FQuat' in r:
            if size > 0:
                return 'for (int i = 0; i < ' + str(size) + '; i++)\n\t\t{\n\t\t\t' \
                    + v_type + '[i].X = in_ros_data.' + v_ros + '[i].x;\n\t\t\t' \
                    + v_type + '[i].Y = in_ros_data.' + v_ros + '[i].y;\n\t\t\t' \
                    + v_type + '[i].Z = in_ros_data.' + v_ros + '[i].z;\n\t\t}\n\n\t\t'
            else:
                # need to identify multidimensional arrays - need some sort of recursion with splits
                v_ros_size = v_ros.split('.data[i]',1)[0]
                return 'for (int i = 0; i < in_ros_data.' + v_ros_size + '.size; i++)\n\t\t{\n\t\t\t' \
                    + v_type + '[i].X = in_ros_data.' + v_ros + '.x;\n\t\t\t' \
                    + v_type + '[i].Y = in_ros_data.' + v_ros + '.y;\n\t\t\t' \
                    + v_type + '[i].Z = in_ros_data.' + v_ros + '.z;\n\t\t\t' \
                    + v_type + '[i].W = in_ros_data.' + v_ros + '.w;\n\t\t}\n\n\t\t'
        elif 'FString' in r:
            if size > 0:
                return 'for (int i = 0; i < ' + str(size) + '; i++)\n\t\t{\n\t\t\t' + v_type + '[i].AppendChars(in_ros_data.' + v_ros + '.data, in_ros_data.' + v_ros + '.size);\n\t\t}\n\n\t\t'
            else:
                # need to identify multidimensional arrays - need some sort of recursion with splits
                v_ros_size = v_ros.split('.data[i]',1)[0]
                return 'for (int i = 0; i < in_ros_data.' + v_ros_size + '.size; i++)\n\t\t{\n\t\t\t' + v_type + '[i].AppendChars(in_ros_data.' + v_ros + '.data,in_ros_data.' + v_ros + '.size);\n\t\t}\n\n\t\t'
        else:
            if size > 0:
                return 'for (int i = 0; i < ' + str(size) + '; i++)\n\t\t{\n\t\t\t' + v_type + '[i] = in_ros_data.' + v_ros + '[i];\n\t\t}\n\n\t\t'
            else:
                # need to identify multidimensional arrays - need some sort of recursion with splits
                v_ros_size = v_ros.split('.data[i]',1)[0]
                return 'for (int i = 0; i < in_ros_data.' + v_ros_size + '.size; i++)\n\t\t{\n\t\t\t' + v_type + '[i] = in_ros_data.' + v_ros + ';\n\t\t}\n\n\t\t'
    else:
        return v_type + ' = in_ros_data.' + v_ros + ';\n\n\t\t'

def cpp2ros_vector(v_ros, v_type, comp, is_array = False, is_fixed_size = False):
    iterator = ''
    iterator_ros = ''
    component = ''
    if comp != '':
        component = '.' + comp
    if is_array and is_fixed_size:
        iterator_ros = '[i]'
    if is_array:
        iterator = '[i]'
    return 'out_ros_data.' + v_ros + iterator_ros + component.lower() + ' = ' + v_type + iterator + component.upper() + ';'

def free_and_malloc(v_ros, v_type, type, Free=True):
    alloc_type = 'decltype(*out_ros_data.' + v_ros + '.data)'
    alloc_type_cast = 'decltype(out_ros_data.' + v_ros + '.data)'
    size = '(' + v_type + '.Num())'
    if type == 'FString':
        size = '(strLength+1)'
    elif type == 'FVector':
        size = '(' + v_type + '.Num() * 3)'
    elif type == 'FQuat':
        size = '(' + v_type + '.Num() * 4)'
    free_mem = ''
    if Free:
        free_mem = 'if (out_ros_data.' + v_ros + '.data != nullptr)\n\t\t{\n\t\t\t'\
                 + 'free(out_ros_data.' + v_ros + '.data);\n\t\t}\n\t\t'
    return  free_mem \
            + 'out_ros_data.' + v_ros + '.data = (' + alloc_type_cast + ')malloc(' + size + '*sizeof(' + alloc_type + '));\n\t\t'

# generate code for getterAoS - Array-of-Structures (SetROS2)
def getterAoS(r, v_type, v_ros, size):
    if r == 'FVector':
        return cpp2ros_vector(v_ros, v_type, 'x') + '\n\t\t' \
             + cpp2ros_vector(v_ros, v_type, 'y') + '\n\t\t' \
             + cpp2ros_vector(v_ros, v_type, 'z') + '\n\n\t\t'
    elif r == 'FQuat':
        return cpp2ros_vector(v_ros, v_type, 'x') + '\n\t\t' \
             + cpp2ros_vector(v_ros, v_type, 'y') + '\n\t\t' \
             + cpp2ros_vector(v_ros, v_type, 'z') + '\n\t\t' \
             + cpp2ros_vector(v_ros, v_type, 'w') + '\n\n\t\t'
    elif r == 'FString':  
        return '{\n\t\t\t' \
            + 'FTCHARToUTF8 strUtf8( *' + v_type + ' );\n\t\t\tint32 strLength = strUtf8.Length();\n\t\t\t' \
            + free_and_malloc(v_ros, v_type, r) \
            + 'memcpy(out_ros_data.' + v_ros + '.data, TCHAR_TO_UTF8(*' + v_type + '), (strLength+1)*sizeof(char));\n\t\t\t' \
            + 'out_ros_data.' + v_ros + '.size = strLength;\n\t\t\t' \
            + 'out_ros_data.' + v_ros + '.capacity = strLength + 1;\n\t\t' \
            + '}\n\n\t\t'
    elif 'TArray' in r:
        for_loop_fixed = 'for (int i = 0; i < ' + str(size) + '; i++)\n\t\t{\n\t\t\t'
        for_loop_dynamic = 'for (int i = 0; i < ' + v_type + '.Num(); i++)\n\t\t{\n\t\t\t'
        if 'FVector' in r:
            if size > 0:
                return for_loop_fixed \
                    + cpp2ros_vector(v_ros, v_type, 'x', True, True) + '\n\t\t\t' \
                    + cpp2ros_vector(v_ros, v_type, 'y', True, True) + '\n\t\t\t' \
                    + cpp2ros_vector(v_ros, v_type, 'z', True, True) + '\n\t\t}\n\n\t\t'
            else:
                # need to identify multidimensional arrays - need some sort of recursion with splits
                v_ros_size = v_ros.split('.data[i]',1)[0]
                return free_and_malloc(v_ros_size, v_type, 'FVector') + '\n\t\t' \
                    + for_loop_dynamic \
                    + cpp2ros_vector(v_ros, v_type, 'x', True, False) + '\n\t\t\t' \
                    + cpp2ros_vector(v_ros, v_type, 'y', True, False) + '\n\t\t\t' \
                    + cpp2ros_vector(v_ros, v_type, 'z', True, False) + '\n\t\t}\n\n\t\t' \
                    + 'out_ros_data.' + v_ros_size + '.size = ' + v_type + '.Num();\n\t\t' \
                    + 'out_ros_data.' + v_ros_size + '.capacity = ' + v_type + '.Num();\n\n\t\t'
        elif 'FQuat' in r:
            if size > 0:
                return for_loop_fixed \
                    + cpp2ros_vector(v_ros, v_type, 'x', True, True) + '\n\t\t\t' \
                    + cpp2ros_vector(v_ros, v_type, 'y', True, True) + '\n\t\t\t' \
                    + cpp2ros_vector(v_ros, v_type, 'z', True, True) + '\n\t\t\t' \
                    + cpp2ros_vector(v_ros, v_type, 'w', True, True) + '\n\t\t}\n\n\t\t'
            else:
                # need to identify multidimensional arrays - need some sort of recursion with splits
                v_ros_size = v_ros.split('.data[i]',1)[0]
                return free_and_malloc(v_ros_size, v_type, 'FQuat') + '\n\t\t' \
                    + for_loop_dynamic \
                    + cpp2ros_vector(v_ros, v_type, 'x', True, False) + '\n\t\t\t' \
                    + cpp2ros_vector(v_ros, v_type, 'y', True, False) + '\n\t\t\t' \
                    + cpp2ros_vector(v_ros, v_type, 'z', True, False) + '\n\t\t\t' \
                    + cpp2ros_vector(v_ros, v_type, 'w', True, False) + '\n\t\t}\n\n\t\t' \
                    + 'out_ros_data.' + v_ros_size + '.size = ' + v_type + '.Num();\n\t\t' \
                    + 'out_ros_data.' + v_ros_size + '.capacity = ' + v_type + '.Num();\n\n\t\t'
        elif 'FString' in r:
            if size > 0:
                return for_loop_fixed \
                    + '{\n\t\t\t' \
                    + 'FTCHARToUTF8 strUtf8( *' + v_type + '[i] );\n\t\t\t\tint32 strLength = strUtf8.Length();\n\t\t\t' \
                    + 'if (out_ros_data.' + v_ros + '.data != nullptr)\n\t\t\t\t{\n\t\t\t\t\t' \
                    + 'free(out_ros_data.' + v_ros + '.data);\n\t\t\t\t}\n\t\t\t\t' \
                    + 'out_ros_data.' + v_ros + '.data = (char*)malloc((strLength+1)*sizeof(char));\n\t\t\t\t' \
                    + 'memcpy(out_ros_data.' + v_ros + '.data, TCHAR_TO_UTF8(*' + v_type + '[i]), (strLength+1)*sizeof(char));\n\t\t\t\t' \
                    + 'out_ros_data.' + v_ros + '.size = strLength;\n\t\t\t\t' \
                    + 'out_ros_data.' + v_ros + '.capacity = strLength + 1;\n\t\t\t}\n\n\t\t' \
                    + '}\n\n\t\t'
            else:
                # need to identify multidimensional arrays - need some sort of recursion with splits
                v_ros_size = v_ros.split('.data[i]',1)[0]
                return free_and_malloc(v_ros_size.split('[i]',1)[0], v_type, 'Pointer') \
                    + for_loop_dynamic \
                    + '{\n\t\t\t\t' \
                    + 'FTCHARToUTF8 strUtf8( *' + v_type + '[i] );\n\t\t\t\t' \
                    + 'int32 strLength = strUtf8.Length();\n\t\t\t\t' \
                    + 'if (out_ros_data.' + v_ros + '.data != nullptr)\n\t\t\t\t{\n\t\t\t\t\t' \
                    + 'free(out_ros_data.' + v_ros + '.data);\n\t\t\t\t}\n\t\t\t\t' \
                    + 'out_ros_data.' + v_ros + '.data = (char*)malloc((strLength+1)*sizeof(char));\n\t\t\t\t' \
                    + 'memcpy(out_ros_data.' + v_ros + '.data, TCHAR_TO_UTF8(*' + v_type + '[i]), (strLength+1)*sizeof(char));\n\t\t\t\t' \
                    + 'out_ros_data.' + v_ros + '.size = strLength;\n\t\t\t\t' \
                    + 'out_ros_data.' + v_ros + '.capacity = strLength + 1;\n\t\t\t}\n\t\t' \
                    + '}\n\n\t\t'
        else:
            if size > 0:
                return for_loop_fixed \
                    + cpp2ros_vector(v_ros, v_type, '', True, True) + '\n\t\t}\n\n\t\t'
            else:
                # need to identify multidimensional arrays - need some sort of recursion with splits
                v_ros_size = v_ros.split('.data[i]',1)[0]
                cpp_base_type = r.split('>',1)[0].split('TArray<',1)[1]
                return free_and_malloc(v_ros_size, v_type, cpp_base_type) + '\n\t\t' \
                    + for_loop_dynamic \
                    + cpp2ros_vector(v_ros, v_type, '', True, False) + '\n\t\t}\n\n\t\t' \
                    + 'out_ros_data.' + v_ros_size + '.size = ' + v_type + '.Num();\n\t\t' \
                    + 'out_ros_data.' + v_ros_size + '.capacity = ' + v_type + '.Num();\n\n\t\t'
    else:
        return 'out_ros_data.' + v_ros + ' = ' + v_type + ';\n\n\t\t'

def free_and_malloc_SoA(v_ros, v_type, type):
    alloc_type = 'decltype(*out_ros_data.' + v_ros + '.data)'
    alloc_type_cast = 'decltype(out_ros_data.' + v_ros + '.data)'
    size = '(' + v_type + '.Num())'
    if type == 'FString':
        size = '(strLength+1)'
    elif type == 'FVector':
        size = '(' + v_type + '.Num() * 3)'
    elif type == 'FQuat':
        size = '(' + v_type + '.Num() * 4)'
    return 'if (out_ros_data.' + v_ros + '.data != nullptr)\n\t\t{\n\t\t\t' \
            + 'free(out_ros_data.' + v_ros + '.data);\n\t\t}\n\t\t' \
            + 'out_ros_data.' + v_ros + '.data = (' + alloc_type_cast + ')malloc(' + size + '*sizeof(' + alloc_type + '));\n\t\t'

# generate code for getterSoA - Structure-of-Arrays (SetROS2)
def getterSoA(r_array, v_type_array, v_ros_array, size_array):
    # WARNING: there could be multiple groups of SoA - need to go by matching substrings in v_ros_array
    SoAs_ros = {}
    SoAs_types = {}
    SoAs_r = {}
    for e in range(len(v_ros_array)):
        if v_ros_array[e].split('.data[i].')[0] in SoAs_ros:
            SoAs_ros[v_ros_array[e].split('.data[i].')[0]].append(v_ros_array[e])
            SoAs_types[v_ros_array[e].split('.data[i].')[0]].append(v_type_array[e])
            SoAs_r[v_ros_array[e].split('.data[i].')[0]].append(r_array[e])
        else:
            SoAs_ros[v_ros_array[e].split('.data[i].')[0]] = [v_ros_array[e]]
            SoAs_types[v_ros_array[e].split('.data[i].')[0]] = [v_type_array[e]]
            SoAs_r[v_ros_array[e].split('.data[i].')[0]] = [r_array[e]]

    malloc_size = {}
    for t in SoAs_types:
        if t not in malloc_size:
            malloc_size[t] = ''
        for e in SoAs_types[t]:
            malloc_size[t] += 'sizeof(' + e + ') + '
        malloc_size[t] = malloc_size[t][:-2]

    getterSoA_result = ''
    for t in SoAs_types:
        # free_and_malloc
        getterSoA_result += 'if (out_ros_data.' + t + '.data != nullptr)\n\t\t{\n\t\t\t' \
            + 'free(out_ros_data.' + t + '.data);\n\t\t}\n\t\t' \
            + 'out_ros_data.' + t + '.data = (decltype(out_ros_data.' + t + '.data))malloc(' + malloc_size[t] + ');\n\t\t'
        # fill
        getterSoA_result += 'for (int i = 0; i < ' + SoAs_types[t][0] + '.Num(); i++)\n\t\t{\n\t\t\t'
        for i in range(len(SoAs_types[t])):
            v_type = SoAs_types[t][i]
            v_ros = SoAs_ros[t][i]
            r = SoAs_r[t][i]
            if 'TArray' in r:
                r = r.split('<',1)[1].split('>')[0]
            if r == 'FVector':
                getterSoA_result += cpp2ros_vector(v_ros, v_type, 'x', True, False) + '\n\t\t\t' \
                                  + cpp2ros_vector(v_ros, v_type, 'y', True, False) + '\n\t\t\t' \
                                  + cpp2ros_vector(v_ros, v_type, 'z', True, False) + '\n\n\t\t\t'
            elif r == 'FQuat':
                getterSoA_result += cpp2ros_vector(v_ros, v_type, 'x', True, False) + '\n\t\t\t' \
                                  + cpp2ros_vector(v_ros, v_type, 'y', True, False) + '\n\t\t\t' \
                                  + cpp2ros_vector(v_ros, v_type, 'z', True, False) + '\n\t\t\t' \
                                  + cpp2ros_vector(v_ros, v_type, 'w', True, False) + '\n\n\t\t\t'
            elif r == 'FString':  
                getterSoA_result += '{\n\t\t\t\t' \
                    + 'FTCHARToUTF8 strUtf8( *' + v_type + '[i] );\n\t\t\tint32 strLength = strUtf8.Length();\n\t\t\t\t' \
                    + free_and_malloc(v_ros, v_type, r, False) \
                    + 'memcpy(out_ros_data.' + v_ros + '.data, TCHAR_TO_UTF8(*' + v_type + '[i]), (strLength+1)*sizeof(char));\n\t\t\t\t' \
                    + 'out_ros_data.' + v_ros + '.size = strLength;\n\t\t\t\t' \
                    + 'out_ros_data.' + v_ros + '.capacity = strLength + 1;\n\t\t\t' \
                    + '}\n\n\t\t\t'
            elif 'TArray' in r:
                getterSoA_result += '\t\t\tUE_LOG(LogTemp, Error, TEXT("Not Implemented Yet!"));\n\n'
            else:
                getterSoA_result += 'out_ros_data.' + v_ros + ' = ' + v_type + '[i];\n\n\t\t\t'
        getterSoA_result += '}\n\t'

        print('unfinished')

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
            is_dynamic_array = False
            if '[]' in v[0]:
                is_dynamic_array = True

            res = get_var_name(v, is_dynamic_array)
            res_ros = get_ros_var_name(v, is_dynamic_array)

            r_array = []
            v_type_array = []
            v_ros_array = []
            size_array = []

            it_type = iter(res)
            it_ros = iter(res_ros)
            for r in it_type:
                size = 0
                r = convert_to_cpp_type(r)
                if '[]' in r:
                    r = r.replace('[]','')
                    r = 'TArray<' + convert_to_cpp_type(r) + '>'
                elif '[' in r and ']' in r:
                    tmp = re.split('\[|\]', r)
                    tmp[1] = tmp[1].replace('<=','')
                    size = tmp[1].replace('<=','')
                    r = 'TArray<' + convert_to_cpp_type(tmp[0]) + '>'
                next(it_ros)
                v_type = next(it_type)
                v_ros = next(it_ros)

                if ('unsigned int' in r or 'double' in r or 'int8' in r or 'uint16' in r or 'uint64' in r):
                    cpp_type += r + ' ' + v_type + ';\n\n\t'
                else:
                    cpp_type += 'UPROPERTY(EditAnywhere, BlueprintReadWrite)\n\t' + r + ' ' + v_type + ';\n\n\t'
                set_from_ros2 += setter(r, v_type, v_ros, int(size))

                if '.data[i].' not in v_ros:
                    set_ros2 += getterAoS(r, v_type, v_ros, int(size))
                else:
                    r_array.append(r)
                    v_type_array.append(v_type)
                    v_ros_array.append(v_ros)
                    size_array.append(int(size))

            if any('.data[i].' in vr for vr in v_ros_array) and any('fields_' in vt for vt in v_type_array) and not any('_fields_' in vt for vt in v_type_array):
                print('getter with:\n' + str(r_array) + '\n' + str(v_type_array) + '\n' + str(v_ros_array) + '\n' + str(size_array))

            if len(r_array) > 0:
                set_ros2 += getterSoA(r_array, v_type_array, v_ros_array, size_array)
                

        types_cpp[key] = [cpp_type, set_from_ros2, set_ros2]

    # for key, value in types_cpp.items():
    #     print(str(key) + ' -> ' + str(value[2]))
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
            # PascalCase to snake_case; correctly handles acronyms: TLA -> tla instead of t_l_a
            name_lower = re.sub('([a-z0-9])([A-Z])', r'\1_\2', re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)).lower()
            info['Name'] = name_lower
            info['NameCap'] = name
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
                info['GoalSetFromROS2'] = types_cpp[Group + '/' + name + '_SendGoal'][1].replace('in_ros_data.','in_ros_data.goal.')
                info['GoalSetROS2'] = types_cpp[Group + '/' + name + '_SendGoal'][2].replace('out_ros_data.','out_ros_data.goal.')
                
                info['ResultTypes'] = types_cpp[Group + '/' + name + '_GetResult'][0]
                info['ResultSetFromROS2'] = types_cpp[Group + '/' + name + '_GetResult'][1].replace('in_ros_data.','in_ros_data.result.')
                info['ResultSetROS2'] = types_cpp[Group + '/' + name + '_GetResult'][2].replace('out_ros_data.','out_ros_data.result.')
                
                info['FeedbackTypes'] = types_cpp[Group + '/' + name + '_Feedback'][0]
                info['FeedbackSetFromROS2'] = types_cpp[Group + '/' + name + '_Feedback'][1].replace('in_ros_data.','in_ros_data.feedback.')
                info['FeedbackSetROS2'] = types_cpp[Group + '/' + name + '_Feedback'][2].replace('out_ros_data.','out_ros_data.feedback.')

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
