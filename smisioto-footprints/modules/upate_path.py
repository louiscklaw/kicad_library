# /usr/bin/env python

import os, sys
from pprint import pprint

def openFileReadContent(file_path):
    contents = ''
    with open(file_path, 'r+') as f:
        contents = f.readlines()

    return contents

def writeFileContent(str_list, file_path):
    with open(file_path, 'r+') as f:
        f.writelines(str_list)

CWD = os.path.abspath(__file__)

for rootdir, subdirs, files in os.walk('.'):
    for name in files:
        curr_dir = os.path.join(rootdir, name)
        print('working on %s' % curr_dir)
        if curr_dir.find('.kicad_mod') > 0:
            file_contents = openFileReadContent(curr_dir)
            for i in range(0,len(file_contents)):
                line = file_contents[i]
                if line.find('model walter') > 0:
                    new_line = line.replace('model walter', 'model ${HOME}/_workspace/kicad/kicad_library/smisioto-footprints/modules/packages3d/walter')
                    print('findme')
                    pprint(new_line)
                    file_contents[i] = new_line
            writeFileContent(file_contents, curr_dir)
