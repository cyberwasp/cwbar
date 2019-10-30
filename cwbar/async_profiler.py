import cwbar.cmd
import cwbar.settings


class AsyncProfiler:
    def __init__(self, pid):
        self.pid = pid
        self.check_restriction()

    def check_restriction(self):
        v1 = cwbar.cmd.execute_with_output("cat /proc/sys/kernel/kptr_restrict", verbose=False)[0]
        v2 = cwbar.cmd.execute_with_output("cat /proc/sys/kernel/perf_event_paranoid", verbose=False)[0]
        if v1 != "0" or v2 != "1":
            print("Перед профилированием необходимо снять ограничения: ")
            print("echo 0 > /proc/sys/kernel/kptr_restrict")
            print("echo 1 > /proc/sys/kernel/perf_event_paranoid")
            raise Exception("Прервано!!")

    def profile(self, duration, output_file_name):
        profiler = cwbar.settings.ASYNC_PROFILER
        cwbar.cmd.execute(profiler + " -d " + str(duration) + " -f " + output_file_name + " " + self.pid)
