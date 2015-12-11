import requests
import time
from StringIO import StringIO
import json
import threading
import re
from subprocess import Popen, PIPE

output_dir = 'out/'

class Server(object):

    def __init__(self, ip, ssh_name, filename):
        self.ip = ip
        self.ssh_name = ssh_name
        self.filename = filename

    def get_cpu_log_filename(self):
        return output_dir + "cpu_" + self.filename

    def get_rps_log_filename(self):
        return output_dir + "rps_" + self.filename


class Monitor(object):
    back51 = Server("95.213.191.51", "back51", "back51")
    back131 = Server("95.213.200.131", "back131", "back131")
    back142 = Server("95.213.200.142", "back142", "back142")

    def scan(self, server, port):
        dt = 1
        time_cur = 0

        f = open(server.get_rps_log_filename(), 'w')
        while True:
            response = requests.get('http://' + server.ip + ':' + str(port) + '/db/api/service/stats/')
            response = json.load(StringIO(str(response.content)))
            # print time_cur, response.get('rps') , response.get('memory_free')
            time_cur += dt
            f.write(str(time_cur) + ' ' + str(response.get('rps')) +
                    ' ' + str(response.get('memory_free')) +
                    ' ' + str(response.get('cpuUs')) +
                    '\n')
            f.flush()
            time.sleep(1)
        f.close()

    def monitor_rps(self):
        port = 80
        t1 = threading.Thread(target=self.scan, args=(self.back51, port))
        t2 = threading.Thread(target=self.scan, args=(self.back131, port))
        t3 = threading.Thread(target=self.scan, args=(self.back142, port))
        t1.start()
        t2.start()
        t3.start()

    def get_cpu(self, server):
        f = open(server.get_cpu_log_filename(), 'w')
        print(server.ssh_name)
        cur_time = 0
        dt = 1
        while True:
            cmd = "ssh " + server.ssh_name + " 'vmstat 1 2'"
            p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()
            result = out.rstrip().split('\n')[3]
            result = re.split(" +", result)
            cpu1 = result[len(result) - 5]
            cpu2 = result[len(result) - 4]
            f.write(str(cur_time) + ' ' + str(cpu1) + ' ' + str(cpu2) + ' ' + str(cpu1 + cpu2) + '\n')
            f.flush()
            cur_time += dt
        f.close()

    def monitor_cpu(self):
        t1 = threading.Thread(target=self.get_cpu, args=(self.back51, ))
        t2 = threading.Thread(target=self.get_cpu, args=(self.back131, ))
        t3 = threading.Thread(target=self.get_cpu, args=(self.back142, ))
        t1.start()
        t2.start()
        t3.start()

test = Monitor()
# test.monitor_cpu()
test.monitor_rps()