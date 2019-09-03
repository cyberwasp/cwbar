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


class LogFile:
    def __init__(self, data):
        self.entries = []
        row_entries = re.findall(PARSE_RE, data, flags=re.MULTILINE)
        for row_entry in row_entries:
            self.entries.append(LogFileEntry(*row_entry))
