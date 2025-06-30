JAVA_HOMES = {}
BASE_SOURCES = "~/Krista/sources"
BASE_COMPILE = "/var/lib/jboss"
MVN = "~/Apps/mvn/current/bin/mvn"
JAVA_HOMES[8] = "~/Apps/java/jdk8"
JAVA_HOMES[11] = "~/Apps/java/jdk11"
JAVA_HOME = JAVA_HOMES[min(JAVA_HOMES.keys())]
PG_PASS = "~/.pgpass"
PSQL = 'psql'
ASYNC_PROFILER = "profiler.sh"


def update_java_home(java_version):
    import os
    if java_version in JAVA_HOMES:
        os.environ["JAVA_HOME"] = os.path.expanduser(JAVA_HOMES[java_version])