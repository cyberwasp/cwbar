import datetime
import re
import sys


def parse_log(file_name, filter):
    for line in open(file_name):
        if filter(line):
            yield line


def main(file_name):
    r = re.compile(r'(\d+\.\d+\.\d+\.\d+) - - \[(.*?)\] "GET '
                   r'/application/rest/messageController/getMessage\?subscriber=([\w+.%]+)&sessionId=([\w,-]+) .*?.*"')
    result = {}
    for line in parse_log(file_name, lambda l: "getMessage" in l):
        m = r.match(line)
        if not m:
            # print("Какая то левая линия! " + line)
            continue
        ip = m.group(1)
        date = m.group(2)
        user = m.group(3)
        session_id = m.group(4)
        key = ip + " " + user + " " + session_id
        dates = result[key] if key in result else list()
        dates.append(datetime.datetime.strptime(date, '%d/%b/%Y:%H:%M:%S %z'))
        result[key] = dates

    total_rate = 0
    for key in result:
        dates = result[key]
        if len(dates) == 1:
            continue
        dt = dates[-1] - dates[0]
        current_rate = len(dates) / dt.seconds if dt.seconds > 0 else len(dates) / 1.0
        total_rate += current_rate
        if current_rate > 0.5:
            print(key)
            print("%.3f" % current_rate)
            print("")
    print("-" * 20)
    print(total_rate)


if __name__ == "__main__":
    main(sys.argv[1])
