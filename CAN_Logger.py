import threading 
import queue 
import can 
import time
import subprocess
import pyinotify

q_logs = queue.Queue()
run=True;

#******************************************************
#Thread for controlling the voltage and Shutting down the pi safely
#******************************************************
class shutdown(threading.Thread):
	def __init__(self, end_flag):
		threading.Thread.__init__(self)
		self.ende=end_flag
		self.command = "/usr/bin/sudo /sbin/shutdown now"
		self.process = subprocess.Popen(command.split(),stdout=subprocess.PIPE)
	def run(self): 
		while not self.ende.isSet(): 
			if False: #(hier noch die Bedingung mit Wert des Analogeinganges für Shutdown)
				self.ende.set()
				#Hier noch Unmount der Logfile-Partition
				output = self.process.communicate()[0]
				print(output)





class FileEventHandler(pyinotify.ProcessEvent):
     def process_IN_CLOSE_WRITE(self, event,changeFlag):
        print("Changed" + event.pathname)
            			

#******************************************************
#Thread listening to the CAN-bus and broadcast the messages to the other threads
#******************************************************
class Listener(threading.Thread):
	def __init__(self, end_flag):
		threading.Thread.__init__(self)
		self.ende=end_flag
		self.bus = can.interface.Bus("vcan0", bustype="socketcan_native")
	def run(self): 
		while not self.ende.isSet():
			mesg=self.bus.recv(0)
#			print(mesg)
			q_logs.put(mesg)

#PRINTER MÜSSEN NOCH SO GEÄNDERT WERDEN, DASS SIE DAS SIGNAL-dICT VERARBEITEN; NICHT NUR NAMENSLISTE			
			
#******************************************************
#Thread for writing in basic text-file
#******************************************************
class Printer(threading.Thread):
	def __init__(self,logfile, end_flag):
		threading.Thread.__init__(self)
		self.ende=end_flag
		self.logfile = logfile
		print(logfile)
	def run(self): 
		while not self.ende.isSet():
			while not q_logs.empty():
				mesg=q_logs.get()
#				print(mesg)
				if mesg != None:
					self.logfile.write(str(mesg))
					self.logfile.write("\n")
					

#******************************************************
#Thread for writing in .csv-file
#******************************************************					
class csvPrinter(threading.Thread):
	def __init__(self,logfile,names, end_flag):
		threading.Thread.__init__(self)
		self.ende=end_flag
		self.logfile = logfile
		self.logfile.write(','.join(names) + "\n")
	def run(self): 
		while not self.ende.isSet():
			while not q_logs.empty():
				msg=q_logs.get()
#				print(mesg)
				if msg != None:
					arg_list = [msg.timestamp, msg.arbitration_id, msg.dlc, msg.data]
					print (msg.data)
					row = ','.join(map(str,([msg.timestamp,
                		        msg.arbitration_id,
		                        msg.dlc,
		                        msg.data[0],
								msg.data[1] ])))
					self.logfile.write(row + "\n")
			

def ctrl_c_handler(signal, frame):
	global run
	#LRM30_request(vcPort,'measure','Idle')
	time.sleep(1)
	print 'Goodbye, cruel world!!!'
	run=False	
			
#******************************************************
#Main for Testing (Comment it out when not used)
#******************************************************
if __name__ == '__main__':
	end_Flag = threading.Event()
	logs = open('test.csv', 'w')
	names = ["acc", "temp", "gyro"]
	signal.signal(signal.SIGINT, ctrl_c_handler)
	
	wm = pyinotify.WatchManager()  # Watch Manager
	mask = pyinotify.IN_CLOSE_WRITE  # watched events
	notifier = pyinotify.ThreadedNotifier(wm, FileEventHandler(changeFlag=changeEvent))
	notifier.start()
	wdd = wm.add_watch('/home/pi/datalogger/loggerconfigs/', mask, rec=False)
	
	Listen_Thread = Listener(end_Flag)
	Print_Thread = csvPrinter(logs, names, end_Flag)
	
	Listen_Thread.start()
	Print_Thread.start()
	
	while run:
		pass
	end_Flag.set()	
	notifier.stop()
	Print_Thread.join()
	logs.close()
