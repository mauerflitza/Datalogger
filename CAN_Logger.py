import threading 
import queue 
import can 
import time
import subprocess
import signal
import pyinotify
import os
import pickle
import csv

q_select = queue.Queue()
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
def msg_transformer():
	msg_file=os.path.join('/home/pi/datalogger/loggerconfigs/','msg_dict.txt')
	file=open(msg_file,'rb')
	msg_dict=pickle.load(file)
	file.close()
	fsignals=open(os.path.join('/home/pi/datalogger/loggerconfigs/signals','signals.txt'),'r' )
	signals=fsignals.read().split(" ")
	fsignals.close()
	select_dict={}
	for msg in msg_dict:
		for signal in signals:
			for sig in range(msg['sig_count']):
				if (signal == msg[sig]['sig_name']):
					tmp_dict={"ID":msg['ID'], 'DLC':msg['DLC'], 'Signal':msg[sig] }	
					select_dict[signal]=tmp_dict
	return select_dict
#If there is not enough CPU Power maybe this thread should be started temporary if needed on file change
#******************************************************
#Thread to write selected Signals with the corresponding msg to a dict: {SignalName:{DLC, ID ,siginfo} }
#******************************************************
class sig_select_Handler(threading.Thread):
	def __init__(self, end_flag, change_flag, new_log_Flag):
		threading.Thread.__init__(self)
		self.endeF=end_flag
		self.changeF=change_flag
		self.log_Flag=new_log_Flag
	def run(self):
		while not self.endeF.isSet():
			if self.changeF.isSet():
				select_dict=msg_transformer()
				#print(select_dict)
				#Maybe needed to write the dict to a file (pickle preferred
				file=open(os.path.join('/home/pi/datalogger/loggerconfigs/signals','testdump.txt'),'w' )
				file.write(str(select_dict))
				file.close()
				print(select_dict)
				q_select.put(select_dict)
				self.log_Flag.set()
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
			if mesg != None:
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
	def __init__(self,logfile,names, end_flag, new_log_Flag):
		threading.Thread.__init__(self)
		self.ende=end_flag
		self.logfile = logfile
		self.new_log_Flag=new_log_Flag
		self.selection={}
		self.ids=[]
		self.names=[]
		self.row=[]
		if not q_select.empty():
			self.selection=q_select.get()
			self.ids, self.names = self.information_getter(self.selection)
			self.logfile.write(','.join(self.names) + "\n")
			for i in range(len(self.ids)):
				self.row.append(' ')
			
	def run(self): 
		csv_writer=csv.writer(self.logfile)
		while not self.ende.isSet():
			#Runtime for 1 writing loop is around 0.4 ms
			while not q_logs.empty():
				start_time=time.time()
				msg=q_logs.get()
#				print(msg)
#				print(mesg)
				if msg != None:
					if str(msg.arbitration_id) in self.ids:
							self.row[self.ids.index(str(msg.arbitration_id))]=msg.data
#							row = '.'.join(map(str,(self.row)))
							csv_writer.writerow(self.row)
				print("RUNTIME: "+str(time.time()-start_time))
			if self.new_log_Flag.isSet():
				self.logfile.close()
				self.logfile=open("test.csv", "w")
#				self.logfile=open(os.path.join("/home/pi/datalogger/logfiles","HIER-NOCH-NAMEN-MIT-DATUM.csv"), "w")
				if not q_select.empty():
					self.selection = q_select.get()
					self.id, self.names = self.information_getter(self.selection)
				self.logfile.write(','.join(self.names) + "\n")
				for i in range(len(self.ids)):
					self.row.append(' ')
				csv_writer=csv.writer(self.logfile)
				print("*********************NEW LOGFILE*******************")
				self.new_log_Flag.clear()
		self.logfile.close()
	def information_getter(self, selection):
		ID=[]
		names=[]
		for signal in selection.keys():
			ID.append(selection[signal]['ID'])
			names.append(signal)
		print(names)
		return ID,names					
			

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
	new_log_Flag = threading.Event()
	logs = open('test.csv', 'w')
	names = ["acc", "temp", "gyro"]
	q_select.put(msg_transformer())
	signal.signal(signal.SIGINT, ctrl_c_handler)
	
	wm = pyinotify.WatchManager()  # Watch Manager
	mask = pyinotify.IN_MODIFY  # watched events
	notifier = pyinotify.ThreadedNotifier(wm, FileEventHandler(changeFlag=change_Flag))
	notifier.start()
	wdd = wm.add_watch('/home/pi/datalogger/loggerconfigs/', mask, rec=False)
	
	Listen_Thread = Listener(end_Flag)
	Print_Thread = csvPrinter(logs, names, end_Flag, new_log_Flag)
	sig_select_Handler = sig_select_Handler(end_Flag, change_Flag, new_log_Flag)
	
	Listen_Thread.start()
	Print_Thread.start()
	sig_select_Handler.start()
	
	time.sleep(30)
	end_Flag.set()	
	notifier.stop()
	Print_Thread.join()
	logs.close()
