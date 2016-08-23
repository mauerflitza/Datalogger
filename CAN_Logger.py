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

#Queue for transporting the new signal setup to the Logfile-Writer
q_select = queue.Queue()
#Queue for the logging data
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
#******************************************************
#Reads the important information about all the selected signals and gives them back as dict
#******************************************************
def msg_transformer():
	#File with the dict for all aviable messages (binary pickle file)
	msg_file=os.path.join('/home/pi/datalogger/loggerconfigs/','msg_dict.txt')
	file=open(msg_file,'rb')
	msg_dict=pickle.load(file)
	file.close()
	#file with the selected signals
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
#******************************************************
#Thread for controlling changes on the setting files--> new Logger-Setup
#******************************************************
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
		self.ID=[]
		self.names=[]
		self.row=[]
		#First setup on start with the old configuration
		if not q_select.empty():
			self.selection=q_select.get()
			self.ids, self.names, self.ID = self.information_getter(self.selection)
			#Unit hinzufuegen noch wenn eine vorhanden ist
			self.logfile.write(','.join(self.names) + "\n")
			for i in range(len(self.ids)):
				self.row.append(' ')			
	def run(self): 
		csv_writer=csv.writer(self.logfile)
		while not self.ende.isSet():
			#Runtime for 1 writing loop is around 0.4 ms
			print("outside")
			while not q_logs.empty():
				print("inside")
				print(q_logs.qsize())
				print(q_logs.qsize())
				msg=q_logs.get()
				if str(msg.arbitration_id) in self.ids:
						databits=0
						self.row[self.ids.index(str(msg.arbitration_id))]=msg.data
						#Reversed order is maybe needed, just uncomment it
#								for byte in reversed(msg.data):
						for byte in msg.data:
							databits=(databits<<8) | byte
						#print(bin(databits))
						self.data_converter(databits, str(msg.arbitration_id))
						#self.data_converter(msg.data)
#							row = '.'.join(map(str,(self.row)))
						csv_writer.writerow(self.row)
			#new Setup deteced--> new Logfile
			if self.new_log_Flag.isSet():
				self.logfile.close()
				self.logfile=open("test.csv", "w")
#				self.logfile=open(os.path.join("/home/pi/datalogger/logfiles","HIER-NOCH-NAMEN-MIT-DATUM.csv"), "w")
				if not q_select.empty():
					self.selection = q_select.get()
					self.id, self.names, self.ID = self.information_getter(self.selection)
				#Unit hinzufuegen noch wenn eine vorhanden ist
				self.logfile.write(','.join(self.names) + "\n")
				for i in range(len(self.ids)):
					self.row.append(' ')
				csv_writer=csv.writer(self.logfile)
				print("*********************NEW LOGFILE*******************")
				self.new_log_Flag.clear()
		self.logfile.close()
	def information_getter(self, selection):
		ids=[]
		for signal in selection.keys():
			ids.append(selection[signal]['ID'])
		ID={ID: [] for ID in ids}
		names=[]
		for signal in selection.keys():
			ID[selection[signal]['ID']].append(signal)
			names.append(signal)
		return ids,names, ID			

	def data_converter(self,databits, id):
		for signal in self.ID[id]:
			value= (databits >> int(self.selection[signal]['Signal']['Startbit']) ) & int(self.selection[signal]['Signal']['Length'])
			if self.selection[signal]['Signal']['factor']:
				if self.selection[signal]['Signal']['offset']:
					real_val=int(self.selection[signal]['Signal']['factor']) * value + int(self.selection[signal]['Signal']['offset'])
				else:
					real_val=int(self.selection[signal]['Signal']['factor']) * value  
			elif self.selection[signal]['Signal']['offset']:
				real_val=value + int(self.selection[signal]['Signal']['offset'])	
			#print(value)
			#print(bin(value))
			
#******************************************************
#Handler for manual interrupt (not yet fully implemented)
#******************************************************	
def ctrl_c_handler(signal, frame):
	end_Flag.set()
	#LRM30_request(vcPort,'measure','Idle')
	time.sleep(1)
	print('Goodbye, cruel world!!!')
	run=False	
			
#******************************************************
#Main for Testing (Comment it out when not used)
#******************************************************
if __name__ == '__main__':
	#Initialising all Setups and Flags
	end_Flag = threading.Event()
	change_Flag = threading.Event()
	new_log_Flag = threading.Event()
	names=[]
	logs = open('test.csv', 'w')
	q_select.put(msg_transformer())
	signal.signal(signal.SIGINT, ctrl_c_handler)
	
	#File-Watcher on the Setting-Files
	wm = pyinotify.WatchManager()  # Watch Manager
	mask = pyinotify.IN_MODIFY  # watched events
	notifier = pyinotify.ThreadedNotifier(wm, FileEventHandler(changeFlag=change_Flag))
	notifier.start()
	wdd = wm.add_watch('/home/pi/datalogger/loggerconfigs/', mask, rec=False)
	
	#Initializing Threads
	Listen_Thread = Listener(end_Flag)
	Print_Thread = csvPrinter(logs, names, end_Flag, new_log_Flag)
	sig_select_Handler = sig_select_Handler(end_Flag, change_Flag, new_log_Flag)
	
	#Starting Threads
	Listen_Thread.start()
	Print_Thread.start()
	sig_select_Handler.start()
	
	#30 seconds runtime and after that the end procedure
	time.sleep(30)
	end_Flag.set()	
	notifier.stop()
	Print_Thread.join()
	logs.close()
