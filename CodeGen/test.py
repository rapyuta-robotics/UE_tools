import os
import sys
import pandas as pd
import re

# need to handle multiple paths
ros_path = sys.argv[1]

def getvarname(curval = {}):
    if len(curval) == 2:
        return [str(curval[0]), str(curval[1])]
    elif len(curval) == 3:
        res = []
        final = []
        for v in curval[2]:
            res = getvarname(v)
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

def get_types(target_path):
    types = set()
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

def get_types_dict(target_path):
    types_dict = {}
    types = get_types(ros_path)
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


types_dict = get_types_dict(ros_path)

# transform values of dictionary to useful C++ strings representing variables
types_cpp = {}
for key, value in types_dict.items():
    cpp_type = '\t'
    for v in value:
        res = getvarname(v)
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

# for key,value in types_dict.items():
#     print(key + ' -> ' + str(value))

for key,value in types_cpp.items():
    print(key + ' -> ' + str(value))
