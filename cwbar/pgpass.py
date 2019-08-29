
try:
    import settings
except:
    import cwbar.settings as settings


def _match(part, value):
    return part == value or part == "*"


def lookup_user_pass(host, port, db):
    for line in open(settings.PG_PASS).read().splitlines():
        line = line.split(":")
        if _match(line[0], host) and _match(line[1], port) and _match(line[2], db):
            return line[3:]
    return None
