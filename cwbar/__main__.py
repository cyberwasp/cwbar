import os
import sys

import cwbar.settings
import cwbar.server

os.environ["JAVA_HOME"] = cwbar.settings.JAVA_HOME

if len(sys.argv) > 1:
    if sys.argv[1]:
        server_name = os.path.basename(sys.argv[0])
        server = cwbar.server.Server(server_name)
        op = getattr(server, sys.argv[1].replace("-", "_"))
        args = sys.argv[2:] if len(sys.argv) > 2 else None
        if args:
            op(*args)
        else:
            op()
