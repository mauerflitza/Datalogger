import pyinotify

class FileEventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        print "Creating:", event.pathname

    def process_IN_CLOSE_WRITE(self, event):
        print "Removing:", event.pathname


#******************************************************
#Thread listening to the CAN-bus and broadcast the messages to the other threads
#******************************************************
filewm = pyinotify.WatchManager()  # Watch Manager
mask = pyinotify.IN_CLOSE_WRITE  # watched events

notifier = pyinotify.ThreadedNotifier(filewm, FileEventHandler())
notifier.start()
wdd = filewm.add_watch('/home/pi/datalogger/loggerconfigs/', mask, rec=False)
time.sleep(10)
notifier.stop()
