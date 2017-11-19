import os
import subprocess
import types

from naga import decorator, compose


class NamespacedMeta(type):
    def __init__(cls, o: object, bases, ns):
        super().__init__(o)

        for f, n in cls.__dict__.items():
            if isinstance(f, types.MethodType):
                setattr(cls, n, decorator(staticmethod)(f))


class Namespaced(metaclass=NamespacedMeta):
    """Inheriting from this will make all methods of the class static methods."""
    pass


def relative_url(path):
    def check_in_path(path, fname):
        # { find . > files_and_folders 2> >(grep -v 'Permission denied' >&2); }
        cmd = '{{ find {} 3>&2 2>&1 1>&3 | grep -v \'Permission denied\' >&3; }} 3>&2 2>&1 | egrep "{}$"'
        _path = compose([
            lambda s: s.replace(r'/', r'[/]'),
            lambda s: s.replace(r'.', r'[.]')],
            fname)
        try:
            cmd_format = cmd.format(path, _path)
            p = subprocess.Popen(cmd_format, shell=True, stdout=subprocess.PIPE)
            c, e = p.communicate()
            if len(c) > 0:
                return c.decode('utf-8').split('\n')[0].strip()
            else:
                return False
        except StopIteration as e:
            return False

    fname = path
    path = os.getcwd()
    while path:
        res = check_in_path(path, fname)
        if res:
            return res
        path = os.path.split(path)[0]
    return False


@decorator
def dapply(f):
    return lambda d: f(**dict(d))
