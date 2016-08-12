import threading 
import queue 
import can 
import time
import subprocess
import signal
import pyinotify
import os
import pickle

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


#If there is not enough CPU Power maybe this thread should be started temporary if needed on file change
#******************************************************
#Thread to write selected Signals with the corresponding msg to a dict: {msg : [signal1, signal2], msg2 : [signal12, signal13] }
#******************************************************
class sig_select_Handler(threading.Thread):
	def __init__(self, end_flag, change_flag):
		threading.Thread.__init__(self)
		self.endeF=end_flag
		self.changeF=change_flag
		self.msg_file=os.path.join('/home/pi/datalogger/loggerconfigs/','msg_dict.txt')
	def run(self):
		while not self.endeF.isSet():
			if self.changeF.isSet():
				file=open(self.msg_file,'rb')
				msg_dict=pickle.load(file)
				file.close()
				fsignals=open(os.path.join('/home/pi/datalogger/loggerconfigs/signals','signals.txt'),'r' )
				signals=fsignals.read().split(" ")
				fsignals.close()
				select_dict={}
#				print(signals)
				for msg in msg_dict:
					sig_selected=[]
					for signal in signals:
						for sig in range(msg['sig_count']):
							if (signal == msg[sig]['sig_name']):
								sig_selected.append(signal)
#								print(sig_selected)
						if sig_selected:
							select_dict[msg['msg_name']]=sig_selected
				#Maybe needed to write the dict to a file (pickle preferred
#				file=open(os.path.join('/home/pi/datalogger/loggerconfigs/signals','testdump.txt'),'w' )
#				file.write(str(select_dict))
#				file.close()
				self.changeF.clear()

				

# SOURCE: https://www.kernel.org/pub/linux/kernel/people/rml/inotify/headers/inotify.h
# SOURCE: https://github.com/seb-m/pyinotify
class FileEventHandler(pyinotify.ProcessEvent):
	def my_init(self, changeFlag):
		self.changeFlag=changeFlag
	def process_IN_MODIFY(self, event):
		print("Changed" + event.pathname)
		self.changeFlag.set()
            			

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
	print('Goodbye, cruel world!!!')
	run=False	
			
#******************************************************
#Main for Testing (Comment it out when not used)
#******************************************************
if __name__ == '__main__':
	end_Flag = threading.Event()
	change_Flag = threading.Event()
	logs = open('test.csv', 'w')
	names = ["acc", "temp", "gyro"]
	signal.signal(signal.SIGINT, ctrl_c_handler)
	
	wm = pyinotify.WatchManager()  # Watch Manager
	mask = pyinotify.IN_MODIFY  # watched events
	notifier = pyinotify.ThreadedNotifier(wm, FileEventHandler(changeFlag=change_Flag))
	notifier.start()
	wdd = wm.add_watch('/home/pi/datalogger/loggerconfigs/', mask, rec=False)
	
	Listen_Thread = Listener(end_Flag)
	Print_Thread = csvPrinter(logs, names, end_Flag)
	sig_select_Handler = sig_select_Handler(end_Flag, change_Flag)
	
	Listen_Thread.start()
	Print_Thread.start()
	sig_select_Handler.start()
	
	time.sleep(30)
	end_Flag.set()	
	notifier.stop()
	Print_Thread.join()
	logs.close()
