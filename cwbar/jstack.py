import os
import re
from datetime import datetime

from cwbar import cmd, jcmd
from cwbar.ufile import UFile

TID_PATTERN = re.compile("tid=(\\w+)")
NAME_PATTERN = re.compile('^"(.*?)"')


def get_tid(line):
    r = TID_PATTERN.search(line)
    if r:
        return r.group(1)
    else:
        raise Exception("Не найден tid в строке" + line)


def get_name(line):
    r = NAME_PATTERN.search(line)
    if r:
        return r.group(1)
    else:
        raise Exception("Не найдено name")


def build_filter_lambda(filter_string):
    context = {}
    exec("def filter(s): return " + (filter_string if filter_string else "True"), context)
    return context.get("filter")


class StackTrace:
    def __init__(self, lines):
        self.lines = lines
        self.tid = get_tid(lines[0])
        self.name = get_name(lines[0])
        self.tags = self.tags()

    def tags(self):
        tags = []
        if len(self.lines) > 1 and "RUNNABLE" in self.lines[1]:
            tags.append("runnable")
        if len(self.lines) > 1 and "BLOCKED" in self.lines[1]:
            tags.append("blocked")
        if self.contains_any("at ru.krista"):
            tags.append("krista")
        if self.contains_any(".ejb3.", ".callTimeout"):
            tags.append("ejb")
        if self.contains_any('CrossDocumentControl'):
            tags.append("cross-control")
        if self.contains_any('SimpleDocumentControl'):
            tags.append("simple-control")
        if self.contains_any("NakedJavaScriptEngine"):
            tags.append("js")
        if self.contains_any("getSettings"):
            tags.append("settings")
        if self.contains_any('-default-'):
            tags.append("reports-in-default")
        if self.contains_any("getPermissionCollection"):
            tags.append("permissions")
        if self.contains_any("executeScenarios"):
            tags.append("scenario")
        if self.contains_any("DataSessionCacheImpl$CacheNode.filter"):
            tags.append("data-session-cache-filter")
        if self.contains_any("SignatureController"):
            tags.append("sign")
        if self.contains_any("socketRead0"):
            tags.append("socket-read")
        if self.contains_any("ExecOperationLoggerDataSession"):
            tags.append("operation-log-write-db")
        if self.contains_any("updatePresetById"):
            tags.append("preset-write-db")
        if self.contains_any("marshalling"):
            tags.append("marshalling")
        return tags

    def size(self):
        return len(self.lines)

    def contains_any(self, *values):
        for value in values:
            if any(value in i for i in self.lines):
                return True
        return False

    def any_tags(self, *values):
        return len(set(self.tags).intersection(set(values))) > 0

    def all_tags(self, *values):
        return len(set(self.tags).intersection(set(values))) == len(values)

    def __str__(self) -> str:
        return "TAGS: " + ", ".join(self.tags) + "\n" + "\n".join(self.lines)


class JStack:
    def __init__(self, file_name, pid=None, filter_string=None):
        self.stack_traces = []
        self.stack_traces_dict = {}
        if file_name:
            stack_traces_lines = UFile(file_name).read().split("\n\n")[1:-2]
        else:
            stack_traces_lines = jcmd.thread_print(pid).split("\n\n")[1:-2]
        filter_lambda = build_filter_lambda(filter_string)
        for stack_trace_lines in stack_traces_lines:
            stack_trace = StackTrace(stack_trace_lines.split("\n"))
            if filter_lambda(stack_trace):
                self.stack_traces_dict[stack_trace.tid] = stack_trace
                self.stack_traces.append(stack_trace)

    def get_tags_map(self):
        tags_map = {}
        for stack_trace in self.stack_traces:
            for tag in stack_trace.tags:
                tag_stack_traces = tags_map.get(tag)
                if not tag_stack_traces:
                    tag_stack_traces = []
                    tags_map[tag] = tag_stack_traces
                tag_stack_traces.append(stack_trace)
        return tags_map

    def compare(self, j_stack, same_root=0):
        for stack_trace in self.stack_traces:
            stack_trace_other = j_stack.stack_traces_dict.get(stack_trace.tid)
            if stack_trace_other:
                if same_root:
                    suffix = stack_trace.lines[-same_root: -1]
                    suffix_other = stack_trace_other.lines[-same_root: -1]
                    if suffix == suffix_other and stack_trace.name == stack_trace_other.name:
                        yield [stack_trace, stack_trace_other]
                else:
                    yield [stack_trace, stack_trace_other]


def find_long_operations(dir_name, start_time, end_time):
    file_names = []
    with os.scandir(dir_name) as it:
        for entry in it:
            if entry.is_file():
                mtime = datetime.fromtimestamp(entry.stat().st_mtime)
                if start_time <= mtime <= end_time:
                    file_names.append(os.path.join(dir_name, entry.name))

        jstack_list = sorted(map(lambda x: JStack(x), file_names), key=lambda x: x.date)

        linked = dict()
        for i in range(1, len(jstack_list)):
            j_stack1 = jstack_list[0]
            j_stack2 = jstack_list[1]
            for s1, s2 in j_stack1.compare(j_stack2, 20, "s.contains_any('at ru.krista')"):
                old = linked.get(s1.tid)
                if old:
                    s1_old, s2_old = old
                    d_old = s2_old.time - s2_old.time
                    d = s2.time - s1.time

                    linked[s1.tid] = s1_old, s2
