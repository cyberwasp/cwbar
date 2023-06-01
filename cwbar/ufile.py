import gzip
import subprocess


class UFile:

    def __init__(self, file_name):
        self.file_name = file_name

    def read(self):
        if self.file_name.startswith("scp://"):
            first_separator_idx = self.file_name.index("/", 6)
            server_name = self.file_name[6:first_separator_idx]
            local_file_name = self.file_name[first_separator_idx:]
            cat = "zcat" if local_file_name.endswith("gz") else "cat"
            return subprocess.check_output(['ssh', server_name, cat, local_file_name], encoding="utf-8")
        else:
            l_open = gzip.open if self.file_name.endswith("gz") else open
            with l_open(self.file_name, encoding="utf-8", mode="rt") as f:
                return f.read()
