#!/usr/bin/python3
import os
import os.path
import cgi, cgitb
import re
import pickle

#own packages
import dbcPattern


def dbc_main(): # NEW except for the call to processInput
	form = cgi.FieldStorage()      # standard cgi script lines to here!
    
    # use format of next two lines with YOUR names and default data
	filedata = form['upload']
	if filedata.file:
		contents, msg_list = processInput(filedata.file)   # process input into a page
		print(contents)
		return msg_list
	return -1
def processInput(file):  
	sig_num=0
	sig_list=[]
	'''Process input parameters and return the final page as a string.'''
	if file: #field really is an upload
		
		#msg_list=[{mesg1}{mesg2}{mesg3}{...}]
		#Messages  has numbered dicts signals in them
		msg_list = dbcPattern.dbcDataReader(file)
		for message in msg_list:
			for j in range(message['sig_count']):
				sig_num=sig_num+1
				sig_list.append(message[j]['sig_name'])
	return createHTML(sig_num, sig_list),msg_list
	
def createHTML(sig_num, sig_list):
	signale=""
	i=0
	file=open("Part1_ajax.txt")
	html_string = file.read()
	file.close()
	for sig_name in sorted(sig_list, key=str.lower):
		signale+="{ sig_sel: '%s'}," %(sig_name) 
#		print(sig_name)
	html_string+=signale[:-1]
#	print(html_string)
	file2=open("Part2.txt")
	html_string+=file2.read()
	file2.close()
#	file=open("htmltext.html",'w')
#	file.write(html_string)
#	file.close()
	return html_string
			

#Muss später ins Hauptprogramm kopiert werden
try:   # NEW
	cgitb.enable()
	print("Content-Type: text/html;charset:UTF-8")   # say generating html
	print("\n\n")
	msg_list=dbc_main()
	filename=os.path.join('/home/pi/datalogger/loggerconfigs/','testdump.txt')
	with open(filename, 'wb') as file:
		pickle.dump(msg_list, file)
except:
    cgi.print_exception()  # catch and print errors
	
