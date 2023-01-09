import os


import cwbar.config
import cwbar.cmd


def _match(part, value):
    return part == value or part == "*"


def lookup_user_pass(host, port, db):
    with open(os.path.expanduser(cwbar.config.PG_PASS)) as f:
        for line in f.read().splitlines():
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
        psql = cwbar.config.PSQL
        return psql + " " + "-h " + self.host + " -U " + self.username + " -p " + self.port + " " + self.db

    def psql(self):
        cwbar.cmd.execute(self.psql_cmd())

    def exec_sql(self, sql):
        cwbar.cmd.execute_with_input(self.psql_cmd(), sql)

    def running_queries(self):
        query = """
SELECT pid, age(clock_timestamp(), query_start), usename, query 
FROM pg_stat_activity 
WHERE query != '<IDLE>' AND query NOT ILIKE '%pg_stat_activity%' 
ORDER BY query_start desc;
"""
        self.exec_sql(query)

