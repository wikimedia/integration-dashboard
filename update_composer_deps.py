#!/usr/bin/env python3

from collections import OrderedDict
import glob
import json
import os
import os.path
import subprocess

import lib
argv = lib.cli_config()


PACKAGES = [
    'jakub-onderka/php-parallel-lint',
    'mediawiki/mediawiki-codesniffer',
]

if len(argv) > 1:
    extension = argv[1]
else:
    extension = None


def update(composer_json):
    os.chdir(os.path.dirname(composer_json))
    print(composer_json.split('/')[-2])
    updating = []
    out = subprocess.check_output(['git', 'diff', '--name-only']).decode()
    if 'composer.json' in out:
        print('WARNING: composer.json has local changes')
        return
    with open(composer_json, 'r') as f:
        j = json.load(f, object_pairs_hook=OrderedDict)
        if 'require-dev' not in j:
            print('No dev deps')
            return
        if not j.get('scripts', {}).get('test'):
            print('No scripts.test command')
            return
        for package, version in j['require-dev'].items():
            if package not in PACKAGES:
                print('Skipping ' + package)
                continue
            if lib.get_packagist_version(package) != version:
                i = (package, version, lib.get_packagist_version(package))
                print('Updating %s: %s --> %s' % i)
                updating.append(i)
                j['require-dev'][package] = lib.get_packagist_version(package)
    if not updating:
        print('Nothing to update')
        return
    with open(composer_json, 'w') as f:
        out = json.dumps(j, indent='\t')
        f.write(out + '\n')
    subprocess.call(['composer', 'update'])
    try:
        subprocess.check_call(['composer', 'test'])
    except subprocess.CalledProcessError:
        print('Tests fail %s!' % composer_json)
    msg = 'build: Updating development dependencies\n\n'
    for tup in updating:
        msg += '* %s: %s → %s\n' % tup
    print(msg)
    lib.commit_and_push(files=['composer.json'], msg=msg,
                        branch='master', topic='bump-dev-deps')

if extension == 'mediawiki':
    packages = [os.path.join(lib.MEDIAWIKI_DIR, 'composer.json')]
else:
    ext_composer_file = os.path.join(lib.SRC, extension, 'composer.json')
    if os.path.exists(ext_composer_file):
        packages = [ext_composer_file]
    else:
        # Fallback to all extensions
        packages = glob.glob(
            os.path.join(lib.EXTENSIONS_DIR, '*/composer.json'))

for package in sorted(packages):
    ext_name = package.split('/')[-2]
    if extension and extension != ext_name:
        continue
    update(package)
