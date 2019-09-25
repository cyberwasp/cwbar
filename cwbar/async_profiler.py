import cmd
import settings


class AsyncProfiler:
    def __init__(self, pid):
        self.pid = pid
        self.check_restriction()

    def check_restriction(self):
        v1 = cmd.execute_with_output("cat /proc/sys/kernel/kptr_restrict", verbose=False)[0]
        v2 = cmd.execute_with_output("cat /proc/sys/kernel/perf_event_paranoid", verbose=False)[0]
        if v1 != "0" or v2 != "1":
            print("Перед профилированием необходимо снять ограничения: ")
            print("echo 0 > /proc/sys/kernel/kptr_restrict")
            print("echo 1 > /proc/sys/kernel/perf_event_paranoid")
            raise Exception("Прервано!!")

    def profile(self, duration, output_file_name):
        cmd.execute(settings.ASYNC_PROFILER + " -d " + str(duration) + " -f " + output_file_name + " " + self.pid)
