import gzip
import re

PARSE_RE = r"(\d\d\d\d-\d\d-\d\d) (\d\d:\d\d:\d\d,\d\d\d) (\w+)\s+\[(.*?)\] \((.*?)\)(.*)"


class LogFileEntry:
    def __init__(self, date, time, level, source, thread, message):
        self.date = date
        self.time = time
        self.level = level
        self.source = source
        self.thread = thread
        self.message = message

    def size(self):
        return len(" ".join([self.date, self.time, self.level, self.source, self.thread, self.message]))

    def __str__(self):
        return self.date + " " + self.time + " " + self.level + " " + "[" + self.source + \
               "] (" + self.thread + ") " + self.message


def _get_log_file_content(file_name):
    if file_name.endswith(".gz"):
        with gzip.open(file_name) as f:
            return f.read()
    else:
        with open(file_name) as f:
            return f.read()


class LogFile:
    def __init__(self, file_name):
        data = _get_log_file_content(file_name)
        self.entries = []
        row_entries = re.findall(PARSE_RE, data, flags=re.MULTILINE)
        for row_entry in row_entries:
            self.entries.append(LogFileEntry(*row_entry))

    def filter(self, filter_string):
        context = {}
        if filter_string:
            exec("def filter(e): return " + filter_string, context)
            return filter(context.get("filter"), self.entries)
        else:
            return self.entries
