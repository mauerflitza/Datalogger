#!/usr/bin/python3
import os
import os.path
import cgi, cgitb
import re

#own packages
import dbcPattern


def dbc_main(): # NEW except for the call to processInput
	contents = createHTML()   # process input into a page
	print(contents)
	return -1
	
def createHTML():
	file=open("Header_Saved.html")
	html_string = file.read()
	file.close()
	html_string += "<body>"
	filename=os.path.join("/home/pi/datalogger/loggerconfigs/","savings.txt")
	savings=open(filename)
	for line in savings:
		match = re.match("html:(?P<html>.*)",line)
		if match:
			html_string+=match.group("html")
	savings.close()
	file = open("populate.txt")
	html_string+=file.read()
	file.close()
	html_string+="</body>"
	return html_string
			

#Muss später ins Hauptprogramm kopiert werden
try:   # NEW
	cgitb.enable()
	print("Content-Type: text/html;charset:UTF-8")   # say generating html
	print("\n\n")
	dbc_main()
except:
    cgi.print_exception()  # catch and print errors
	
