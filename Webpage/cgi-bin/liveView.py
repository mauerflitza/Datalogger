#!/usr/bin/python3
import os
import os.path
import cgi, cgitb
import re
import pickle

#own packages
import dbcPattern


def cgi_main(): # NEW except for the call to processInput
	form = cgi.FieldStorage()      # standard cgi script lines to here!
    
    # use format of next two lines with YOUR names and default data
	contents = createHTML()   # process input into a page
	print(contents)
	return -1
	
def createHTML():
	file=open("Part_Live1.txt",'r')
	html_string=file.read()
	file.close()
	#mit pickle wahrscheinlich
	fsignal=open("/home/pi/datalogger/loggerconfigs/signals/signals.txt",'r')
	signale=fsignal.read()
	s_list = signale.split(" ", 1)
	for item in s_list:
		html_string += "{sig_sel:'"+ item +"'},"
	html_string = html_string[:-1]
	fsignal.close()
	file=open("Part2.txt",'r')
	html_string+=file.read()
	file.close
	return html_string
			

#Muss später ins Hauptprogramm kopiert werden
try:   # NEW
	cgitb.enable()
	print("Content-Type: text/html;charset:UTF-8")   # say generating html
	print("\n\n")
	cgi_main()
except:
    cgi.print_exception()  # catch and print errors
	
