import os
import re

import cwbar.java.jcmd
import cwbar.ufile

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
        # предметные теги
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
        if self.contains_any("GridServlet"):
            tags.append("grid")
        if self.contains_any("GridServlet.processLoad"):
            tags.append("grid-load")
        if self.contains_any("JsonInterfaceServlet"):
            tags.append("form-open")
        if self.contains_any("Hashtable.get"):
            tags.append("hashtable-get")
        if self.contains_any("QueryExecutorImpl.execute"):
            tags.append("exec-sql")
        if self.contains_any("CheckValidConnectionSQL.isValidConnection"):
            tags.append("db-connection-check")
        if self.contains_any("mcp.Semaphore.tryAcquire"):
            tags.append("db-connection-waiting")
        if not tags:
            tags.append("unknown")

        # системные теги
        if len(self.lines) > 1 and "RUNNABLE" in self.lines[1]:
            tags.append("runnable")
        if len(self.lines) > 1 and "BLOCKED" in self.lines[1]:
            tags.append("blocked")
        if self.contains_any("at ru.krista"):
            tags.append("krista")
        if self.contains_any(".ejb3.", ".callTimeout"):
            tags.append("ejb")

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
            stack_traces_lines = cwbar.ufile.UFile(file_name).read().split("\n\n")[1:-2]
        else:
            stack_traces_lines = cwbar.java.jcmd.thread_print(pid).split("\n\n")[1:-2]
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
