import subprocess
import sys
import os
import glob
from functools import partial


def execfile(filepath, globals=None, locals=None):
    # if globals is None:
    #     globals = {}
    # globals.update({
    #     "__file__": filepath,
    #     "__name__": "__main__",
    # })
    # with open(filepath, 'rb') as file:
    #     exec(compile(file.read(), filepath, 'exec'), globals, locals)

    subprocess.Popen(["python", filepath])


def script_path(script_name):
    return sys.path.join(__path__, script_name)


class scripts(object):
    ...


def _run_script(path, *args):
    return subprocess.Popen(['python', path, *args], stderr=subprocess.PIPE)


scripts = scripts()

# print((glob.glob(os.path.join(__path__[0], '*.py'))))
for path in glob.iglob(os.path.join(__path__[0], '*.py')):
    # print(path)
    script_name = os.path.splitext(os.path.basename(path))[0]
    # setattr(scripts, script_name,
    #         partial(exec,
    #                 compile(open(path, "rb").read(), path, 'exec'),
    #                 {"__file__": path, "__name__": "__main__"},
    #                 None))
    setattr(scripts,
            script_name,
            partial(_run_script, path))
