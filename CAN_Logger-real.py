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

import socket
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
from tornado.ioloop import PeriodicCallback
import tornado.web
import json

#Queue for transporting the new signal setup to the Logfile-Writer
q_select = queue.Queue()
#Queue for the raw data
q_data = queue.Queue()
#Queue for the logging data
q_logs = queue.Queue()
#Queue for the LiveView
q_live = queue.Queue()
#Queue for the selected Names
q_name = queue.Queue()
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
# Klasse des Websockets
# Periodischer Callback wird erstellt, der die Werte aus der Queue zurueck gibt	
#******************************************************
class WSHandler(tornado.websocket.WebSocketHandler):
	def check_origin(self, origin):
		return True
    
	def open(self):
		with q_live.mutex:
			q_live.queue.clear()
		self.callback = PeriodicCallback(self.send_werte, 1)
		self.callback.start()
		print ('Connection open')	
	def send_werte(self):
		if not q_live.empty():
			signals, values = q_live.get()
			senden = dict(zip(signals,values))
			print(senden)
			json_send = json.dumps(senden)
			self.write_message(json_send)
			print(q_live.qsize())
			if q_live.qsize() >15:
				with q_live.mutex:
					q_live.queue.clear()
	def on_message(self, empf):
		  print('Daten recievied: ')

	def on_close(self):
		print('Connection closed!')
		self.callback.stop()
		
		
def start_Tornado():
  application = tornado.web.Application([(r'/', WSHandler),])
  http_server = tornado.httpserver.HTTPServer(application)
  http_server.listen(8888)
  tornado.ioloop.IOLoop.instance().start()

# Websocket wird wieder geschlossen
def stop_tornado():
    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.add_callback(ioloop.stop)
    print("Asked Tornado to exit")
				
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
		self.bus = can.interface.Bus("can0", bustype="socketcan_native")
	def run(self): 
		while not self.ende.isSet():
			mesg=self.bus.recv(0)
#			print(mesg)
			if mesg != None:
				q_data.put(mesg)
			
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
	def __init__(self,end_flag, new_log_Flag):	
		threading.Thread.__init__(self)
		self.ende=end_flag
		#Hier noch Logfile-Name mit Datum hin
		filename=os.path.join("/home/pi/datalogger/logfiles",time.strftime("%Y%m%d-%H%M%S")+".csv")
		self.logfile=open(filename, "w")
		self.new_log_Flag=new_log_Flag
		self.names=[]
		self.row=[]
		if not q_name.empty():
			self.names, titles=q_name.get()
			#Unit hinzufuegen noch wenn eine vorhanden ist
			self.logfile.write(','.join(titles) + "\n")
			for i in range(len(self.names)):
				self.row.append(' ')
	def run(self): 
		csv_writer=csv.writer(self.logfile)
		while not self.ende.isSet():
			if not q_logs.empty():
				signals, log_vals = q_logs.get()
				for signal, value in zip(signals,log_vals):
					if signal in self.names:
						self.row[self.names.index(signal)]=value
				csv_writer.writerow(self.row)
			#new Setup deteced--> new Logfile
			if not q_name.empty():
				self.logfile.close()
				filename=os.path.join("/home/pi/datalogger/logfiles",time.strftime("%Y%m%d-%H%M%S")+".csv")
				self.logfile=open(filename, "w")
#				self.logfile=open(os.path.join("/home/pi/datalogger/logfiles","HIER-NOCH-NAMEN-MIT-DATUM.csv"), "w")
				self.names, titles=q_name.get()
				#Unit hinzufuegen noch wenn eine vorhanden ist
				self.logfile.write(','.join(titles) + "\n")
				for i in range(len(self.names)):
					self.row.append(' ')
				csv_writer=csv.writer(self.logfile)
				print("*********************NEW LOGFILE*******************")
				#Clear any possible old data from the Queue
#				with q_logs.mutex:
#					q_logs.queue.clear()
		self.logfile.close()
		
class DataManager(threading.Thread):
	def __init__(self, end_flag, new_log_Flag):
		threading.Thread.__init__(self)
		self.ende=end_flag
		self.new_log_Flag=new_log_Flag
		self.selection={}
		self.ids=[]
		self.ID=[]
		self.names=[]
		#First setup on start with the old configuration
		if not q_select.empty():
			self.selection=q_select.get()
			self.ids, self.names, self.ID, titles = self.information_getter(self.selection)
			q_name.put((self.names,titles))	
	def run(self): 
		while not self.ende.isSet():
			#Runtime for 1 writing loop is around 0.4 ms
			#For Runtime measurement uncomment
#			start_time=time.time()
			while not q_data.empty():
				msg=q_data.get()
				if str(msg.arbitration_id) in self.ids:
					databits=0
#					self.row[self.ids.index(str(msg.arbitration_id))]=msg.data
					#Reversed order is maybe needed, just uncomment it
#					for byte in reversed(msg.data):
					for byte in msg.data:
						databits=(databits<<8) | byte
					signals,log_vals = self.data_converter(databits, str(msg.arbitration_id))
					q_logs.put((signals,log_vals))
					q_live.put((signals,log_vals))
				if self.new_log_Flag.isSet():
					if not q_select.empty():
						self.selection = q_select.get()
						self.id, self.names, self.ID, titles = self.information_getter(self.selection)
						q_name.put((self.names, titles))
					#Clear any possible old data from the Queue
					with q_logs.mutex:
						q_logs.queue.clear()
					self.new_log_Flag.clear()
			#For Runtime measurement uncomment
#			print(time.time()-start_time)

	def information_getter(self, selection):
		ids=[]
		for signal in selection.keys():
			ids.append(selection[signal]['ID'])
		ID={ID: [] for ID in ids}
		names=[]
		titles=[]
		for signal in selection.keys():
			ID[selection[signal]['ID']].append(signal)
			names.append(signal)
			if selection[signal]['Signal']['unit'] and selection[signal]['Signal']['unit']!=" ":
				titles.append(signal + "[" + selection[signal]['Signal']['unit'] + "]")
			else:
				titles.append(signal)
		return ids,names, ID, titles			
	#Transform the byte data in Float values with factor and offset (returns list with all neccessary data
	def data_converter(self,databits, id):
		values=[]
		for signal in self.ID[id]:
			value= (databits >> int(self.selection[signal]['Signal']['Startbit']) ) & 2**int(self.selection[signal]['Signal']['Length'])-1
			if self.selection[signal]['Signal']['factor'] and self.selection[signal]['Signal']['factor']!=" ":
				if self.selection[signal]['Signal']['offset'] and self.selection[signal]['Signal']['offset']!=" " :
					real_val=float(self.selection[signal]['Signal']['factor']) * value + float(self.selection[signal]['Signal']['offset'])
				else:
					real_val=float(self.selection[signal]['Signal']['factor']) * value  
			elif self.selection[signal]['Signal']['offset'] and self.selection[signal]['Signal']['offset']!=" ":
				real_val=value + float(self.selection[signal]['Signal']['offset'])	
#			print(real_val)
			values.append(real_val)
		return self.ID[id], values
		
			
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
	print("Initializing...")
	Listen_Thread = Listener(end_Flag)
	Manager_Thread = DataManager(end_Flag, new_log_Flag)
	Print_Thread = csvPrinter(end_Flag, new_log_Flag)
	sig_select_Handler = sig_select_Handler(end_Flag, change_Flag, new_log_Flag)
	#http://stackoverflow.com/questions/5375220/how-do-i-stop-tornado-web-server
	#Notwendig zum Beenden von Tornado
	t_websocket = threading.Thread(target=start_Tornado)
	print("finished initialized")
	print("starting Threads ...")
	t_websocket.start()

	#Starting Threads
	Listen_Thread.start()
	Manager_Thread.start()
	Print_Thread.start()
	sig_select_Handler.start()
	
	#30 seconds runtime and after that the end procedure
	time.sleep(30)
	end_Flag.set()	
	notifier.stop()
	Print_Thread.join()
	stop_tornado()
	print("LOGS:")
	print(q_logs.qsize())
	t_websocket.join()
