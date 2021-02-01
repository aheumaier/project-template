#!/usr/bin/env python
import subprocess
import errno
try:
    out = subprocess.run(["npx", "commitlint", "-V", "-e"], )
    if out.stderr is not None:
        print(out.stderr)
except OSError as e:
    if e.errno == errno.ENOENT:
        print("ERROR: npx commitlint command not found")
    else:
        # Something else went wrong while trying to run `commitlint`
        raise e
