from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import datetime
import json
import os
import re

class MyHandler(BaseHTTPRequestHandler):
    def get_json(self, seconds):
        """
        This function return final json that will show webserver. Function
        get seconds that put in path request, access log file creation and
        get files
        """
        files = [] 
        filenames_lenght = []
        json_file = [] 
        creations_file = open('/var/log/newfiles.log', 'r')
        now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        date_before = int(now) - int(seconds)
        # Loop in file to get all lines 
        for line in creations_file:
            (key, val) = line.split()
            check_date_time = int(key)
            # Check between two datatimes because could be posibility of
            # new files creation after request
            if date_before <= check_date_time <= now:
                path = os.path.basename(val)
                lenght = len(path)
                files.append(path)
                filenames_lenght.append(lenght)
        # It's only for return json empty data and not get an error
        if files:
            median = self.get_median(filenames_lenght)
        else:
            median = ''
        json_file.append({'files': files, 'median_lenght': median})
        return(json.dumps(json_file))

    def get_median(self, data_list):
        """
        If using python3 I could use median function but in python 2.7 it's
        not available, so I toke this median function from github:
        https://github.com/bycoffe/python-math/blob/master/calculate/median.py
        """
        data_list = map(float, data_list)
        n = len(data_list)
        data_list.sort()
        # Test whether the n is odd
        if n & 1:
          # If is is, get the index simply by dividing it in half
          index = n / 2 
          return data_list[index]
        else:
          # If the n is even, average the two values at the center
          low_index = n / 2 - 1
          high_index = n / 2
          average = (data_list[low_index] + data_list[high_index]) / 2
          return average

    def do_GET(self):
        # Only continue if there is only one path after URL
        regexp = re.compile('^\/(\d+)$')
        match = regexp.match(self.path)
        if match:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            seconds = match.group(1)
            self.wfile.write("%s" % self.get_json(seconds))
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write("{ 'error': 'You must specify seconds on url path' }")
        return

def write_pidfile():
    pid_file = '/var/run/http_service.pid'
    if os.path.exists(pid_file):
        print("Cannot daemonize: pid file %s already exists." % pid_file)
        raise SystemExit(1)
    pid = str(os.getpid())
    f = open(pid_file, 'w')
    f.write(pid)
    f.close()

try:
    write_pidfile()
    server = HTTPServer(('localhost', 8888), MyHandler)
    # FIX: send this messages to external log
    print('Started http server')
    server.serve_forever()
except KeyboardInterrupt:
    print('^C received, shutting down server')
    server.socket.close()
