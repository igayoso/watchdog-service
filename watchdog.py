import pyinotify
import datetime
import re
import sys

class TrackCreation(pyinotify.ProcessEvent):
   def process_IN_CREATE(self, event):
       filename = event.pathname
       # Only add entry to log if filename start with _
       regexp = re.compile(r'_.*')
       if regexp.search(filename) is not None:
            # Using better datetime format for help when make operations with datetimes
            fo.write("%s %s" % (datetime.datetime.now().strftime("%Y%m%d%H%M%S"), filename))
            fo.flush()

fo = file('/var/log/newfiles.log', 'a')
try:
    wm = pyinotify.WatchManager()
    handler = TrackCreation(fileobj=fo)
    notifier = pyinotify.Notifier(wm, default_proc_fun=handler)
    # Only watch for create files, ignore rest of operations
    wm.add_watch('/home', pyinotify.IN_CREATE)
    # Daemonize for start with init.d script
    notifier.loop(daemonize=True, pid_file='/var/run/watchdog.pid')
except pyinotify.NotifierError, err:
    print >> sys.stderr, err
