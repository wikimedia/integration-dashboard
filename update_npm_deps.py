#!/usr/bin/env python3

from collections import OrderedDict
import glob
import json
import os
import os.path
import subprocess

import lib
argv = lib.cli_config()

if len(argv) > 1:
    extension = argv[1]
else:
    extension = None


def update(package_json):
    os.chdir(os.path.dirname(package_json))
    print(package_json.split('/')[-2])
    updating = []
    out = subprocess.check_output(['git', 'diff', '--name-only']).decode()
    if 'package.json' in out:
        print('WARNING: package.json has local changes')
        return
    with open(package_json, 'r') as f:
        j = json.load(f, object_pairs_hook=OrderedDict)
        for package, version in j['devDependencies'].items():
            if lib.get_npm_version(package) != version:
                i = (package, version, lib.get_npm_version(package))
                print('Updating %s: %s --> %s' % i)
                updating.append(i)
                j['devDependencies'][package] = lib.get_npm_version(package)
    if not updating:
        print('Nothing to update')
        return
    with open(package_json, 'w') as f:
        out = json.dumps(j, indent='  ')
        f.write(out + '\n')
    subprocess.call(['npm', 'install'])
    try:
        subprocess.check_call(['npm', 'test'])
    except subprocess.CalledProcessError:
        print('Error updating %s' % package_json)
        return
    msg = 'build: Updating development dependencies\n\n'
    for tup in updating:
        msg += '* %s: %s → %s\n' % tup
    print(msg)
    lib.commit_and_push(files=['package.json'], msg=msg, branch='master',
                        topic='bump-dev-deps')

if extension == 'mediawiki':
    packages = [os.path.join(lib.MEDIAWIKI_DIR, 'package.json')]
else:
    packages = glob.glob(os.path.join(lib.EXTENSIONS_DIR, '*/package.json'))
for package in sorted(packages):
    ext_name = package.split('/')[-2]
    if extension and extension != ext_name:
        continue
    update(package)
