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
	pagedata = form.getvalue('webpage')
	SRate = form.getvalue('SampleRates')
	print(SRate)
	StartVal = form.getvalue('StartVal')
	contents = processInput(pagedata, SRate, StartVal)   # process input into a page
	print(contents)
	return -1
def processInput(pagedata, SRate, StartVal):
	i=0 
	filename=os.path.join("/home/pi/datalogger/loggerconfigs/","saved.txt")
	file=open(filename, "w")
	file.write(pagedata)
	if SRate:
		SRates_list=SRate.split(',')
	if StartVal:
		StartVal_list=StartVal.split(',')	
	file.write("\nEndeHTML")
	for rate in SRates_list:
		file.write('SampleRate '+str(i)+": "+rate)
		i=i+1
	file.write("\nEndeRates")
	i=0
	for values in StartVal_list:
		file.write('StartValue '+str(i)+": "+rate)	
		i=i+1
	file.write("\nEndeValues")
	file.close()
	return createHTML()
	
def createHTML():
	file=open("Header_Saved.html")
	html_string = file.read()
	file.close()
	filename=os.path.join("/home/pi/datalogger/loggerconfigs/","saved.txt")
	savings=open(filename)
	for line in savings:
		if re.match("EndeHTML",line):
			break
		else:
			html_string+=line
	savings.close()
	return html_string
			

#Muss später ins Hauptprogramm kopiert werden
try:   # NEW
	cgitb.enable()
	print("Content-Type: text/html;charset:UTF-8")   # say generating html
	print("\n\n")
	print("test")
	print("test2")
	dbc_main()
except:
    cgi.print_exception()  # catch and print errors
	
