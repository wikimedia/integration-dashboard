#!/usr/bin/env python3

from collections import defaultdict
import os
import os.path
import subprocess
import tempfile

import lib
lib.cli_config()


def main():

    cidir = os.path.join(lib.SRC, 'integration-config')
    if not os.path.exists(cidir):
        # Standard layout
        cidir = os.path.join(lib.SRC, 'integration/config')

    if lib.ON_LABS:
        zuul_server = '/data/project/ci/py2-venv2/bin/zuul-server'
        lib.git_pull(cidir)
    else:
        zuul_server = '/home/km/python/bin/zuul-server'
    config = os.path.join(cidir, 'zuul/layout.yaml')

    ZUUL_OUTPUT = os.path.join(cidir, 'zuul/output')  # noqa
    PROJECTS = ('mediawiki/extensions/', 'mediawiki/skins/')

    f = tempfile.NamedTemporaryFile(delete=False)
    subprocess.call([zuul_server, '-t', '-l', config], stderr=f)
    f.close()
    with open(f.name) as rf:
        lines = rf.read().splitlines()

    os.unlink(f.name)
    data = defaultdict(dict)
    project = None
    for line in lines:
        if not line.startswith('INFO:zuul.DependentPipelineManager:'):
            continue
        sp = line.split(':', 3)
        text = sp[2].strip()
        if text.startswith(PROJECTS):
            project = text.replace('/', '-')
            if len(project.split('-')) != 3:
                project = None
        if not project:
            continue
        if text.startswith('<Job'):
            job_name = text.split(' ', 1)[1].split('>', 1)[0]
            voting = not text.endswith('[nonvoting]')
            data[project][job_name] = voting

    return data


if __name__ == '__main__':
    print(main()['mediawiki-skins-CologneBlue'])
