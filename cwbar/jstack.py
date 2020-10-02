import sys


def is_runable(stack_trace_lines):
    return len(stack_trace_lines) > 1 and "RUNNABLE" in stack_trace_lines[1]


def is_blocked(stack_trace_lines):
    return len(stack_trace_lines) > 1 and "BLOCKED" in stack_trace_lines[1]


def size_greater(stack_trace_lines, value):
    return len(stack_trace_lines) > value


def line_contains(stack_trace_lines, value):
    return any(value in i for i in stack_trace_lines)


with open(sys.argv[1]) as f:
    data = f.read()
    stack_traces = data.split("\n\n")
    for stack_trace in stack_traces:
        lines = stack_trace.split("\n")

        if not size_greater(lines, 20):
            continue

        if line_contains(lines, ".RightInfoProviderImpl.getPermissionCollection"):
            continue

        if line_contains(lines, "DataBaseMultiLockInfoProvider"):
            continue

        if line_contains(lines, "refreshUser"):
            continue

        if line_contains(lines, "writeStats"):
            continue

        if line_contains(lines, "SemaphoreArrayListManagedConnectionPool"):
            continue

        if line_contains(lines, "getPasswordState"):
            continue

        print(stack_trace)
        print("\n")
