import os



try:
    import settings
    import cmd
except:
    import cwbar.settings as settings
    import cwbar.cmd as cmd


def _match(part, value):
    return part == value or part == "*"


def lookup_user_pass(host, port, db):
    for line in open(os.path.expanduser(settings.PG_PASS)).read().splitlines():
        line = line.split(":")
        if _match(line[0], host) and _match(line[1], port) and _match(line[2], db):
            return line[3:]
    return None


class Postgres(object):

    def __init__(self, host, port, db, username):
        self.host = host
        self.port = port
        self.db = db
        self.username = username

    def psql_cmd(self):
        return settings.PSQL + " " + "-h " + self.host + " -U " + self.username + " -p " + self.port + " " + self.db

    def psql(self):
        cmd.execute(self.psql_cmd())

    def exec_sql(self, sql):
        cmd.execute_with_input(self.psql_cmd(), sql)

    def running_queries(self):
        QUERY = """
SELECT pid, age(clock_timestamp(), query_start), usename, query 
FROM pg_stat_activity 
WHERE query != '<IDLE>' AND query NOT ILIKE '%pg_stat_activity%' 
ORDER BY query_start desc;
"""
        self.exec_sql(QUERY)

