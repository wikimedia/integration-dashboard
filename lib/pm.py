from collections import defaultdict
import lib
import os.path


class PackageManager(object):
    """Base class to represent a package manager"""

    file_name = None
    dev_section = None

    def __init__(self, dev_deps):
        self.dev_deps = dev_deps

    def dev_versions(self, path):
        if not path.endswith(self.file_name):
            path = os.path.join(path, self.file_name)

        info = lib.json_load(path)
        ret = defaultdict(dict)
        if self.dev_section in info:
            for pkg in self.dev_deps:
                version = info[self.dev_section].get(pkg)
                if version:
                    ret[pkg]['version'] = version
        return ret


class Composer(PackageManager):
    """Composer PHP package manager"""

    file_name = 'composer.json'
    dev_section = 'require-dev'


class Npm(PackageManager):
    """Npm JavaScript package manager"""

    file_name = 'package.json'
    dev_section = 'devDependencies'
