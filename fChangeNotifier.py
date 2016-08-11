import pyinotify
import time

wm = pyinotify.WatchManager()  # Watch Manager
mask = pyinotify.IN_CLOSE_WRITE  # watched events

class FileEventHandler(pyinotify.ProcessEvent):
     def process_IN_CLOSE_WRITE(self, event):
        print("Changed" + event.pathname)


#******************************************************
#Thread listening to the CAN-bus and broadcast the messages to the other threads
#******************************************************

notifier = pyinotify.ThreadedNotifier(wm, FileEventHandler())
notifier.start()
wdd = wm.add_watch('/home/pi/datalogger/loggerconfigs/', mask, rec=False)
time.sleep(10)
notifier.stop()
