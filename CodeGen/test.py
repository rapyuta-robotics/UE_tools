import os
import sys
import pandas as pd
import re

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
        print('ERROR with ' + str(v))
    return '',''


types = set()
for subdir, dirs, files in os.walk(ros_path):
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

types_dict = {}
for t in types:
    tsplit = t.split('/')
    for subdir, dirs, files in os.walk(ros_path):
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

# for key,value in types_dict.items():
#     print(key + ' -> ' + str(value))

# transform values of dictionary to useful C++ strings representing variables
types_cpp = {}
for key, value in types_dict.items():
    cpp_type = '\t'
    for v in value:
        res = getvarname(v)
        it = iter(res)
        for r in it:
            if '[]' in r:
                r = r.replace('[]','')
                r = 'TArray<' + r + '>'
            elif '[' in r and ']' in r:
                tmp = re.split('\[|\]', r)
                tmp[1] = tmp[1].replace('<=','')
                r = 'TArray<' + tmp[0] + ', TFixedAllocator<' + tmp[1] + '>>'
            cpp_type += r + ' ' + next(it) + ';\n\t'
    types_cpp[key] = cpp_type

for key,value in types_cpp.items():
    print(key + ' -> ' + str(value))
# print('geometry_msgs/Vector3 -> ' + ' from ' + str(types_dict['geometry_msgs/Vector3']) + '\n' + types_cpp['geometry_msgs/Vector3'])
# print('std_msgs/Header -> ' + ' from ' + str(types_dict['std_msgs/Header']) + '\n' + types_cpp['std_msgs/Header'])
# print('nav_msgs/OccupancyGrid -> ' + ' from ' + str(types_dict['nav_msgs/OccupancyGrid']) + '\n' + types_cpp['nav_msgs/OccupancyGrid'])
