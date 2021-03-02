def parse(data):
    result = {}
    prev_line = ""
    for line in data.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue
        if line.endswith("\\"):
            prev_line += line[:-1]
            continue
        if prev_line:
            line = prev_line + line
            prev_line = ""
        p = line.index("=")
        if p > 0:
            result[line[:p].strip()] = line[p + 1:].strip()
    return result


def parse_file(file_name):
    with open(file_name, encoding="utf-8") as f:
        return parse(f.read())


