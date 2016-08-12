import re
import time



#*************************************************
#function to read a dbc file and return list with all message informations
#returns a list with dictionaries of the messages with all the signals
#*************************************************
def dbcDataReader(dbcFile):
	testline="BO_ 37 engine: 2 Motor"
	testline2=' SG_ e_temp : 0|8@1- (1,3) [2|4] "temp"  Reciever'
	liste_msg = ['ID','msg_name','DLC']
	liste_signals=['sig_name','Startbit','Length','Sign','factor','offset','min','max','unit']
	diction = {}
	flag=0
	sig_count=0
	return_list=[]
	
	
	for line_b in dbcFile:
		#ISO-8859-1, da auch deutsche Dateien gelesen werden muessen (Umlaute)
		line=line_b.decode("ISO-8859-1")
		#Regular expressions to find all the important information in the dbc file		
		match=re.match('BO_ (?P<ID>\d+) (?P<msg_name>\w+): (?P<DLC>[0-8]) \w+', line)
		match2= re.match('\s*SG_ (?P<sig_name>\w+)\s*:'
						 '\s*(?P<Startbit>\d+)\|(?P<Length>[0-8]+)@\d(?P<Sign>[+-])'
						 '\s*\((?P<factor>[-+]?[0-9]*\.[0-9]+|[0-9]+),(?P<offset>-?[0-9]*[\.[0-9]+|[0-9]+)]?\)'
						 '\s*\[(?P<min>-?[0-9]*[\.[0-9]+|[0-9]+)\|(?P<max>-?[0-9]*[\.[0-9]+|[0-9]+)]?\]'
						 '\s*"(?P<unit>.*)"\s*\w*',line)
		#Message-Dict wird erstellt mti allen zugehoerigen signalen
		
		if match:		#Match is true when a group is found		
			for item in liste_msg:
				diction[item]=match.group(item)
			flag=0
		elif match2:
			#sig count fuer das durchzaehlen der signale
			diction[sig_count] = {}
			for item in liste_signals:
				diction[sig_count][item]=match2.group(item)
			flag=1
			sig_count=sig_count+1
		elif not (match2 or match):
			if flag==1:
				diction['sig_count'] = sig_count
				sig_count=0
				return_list.append(diction)
				#print (return_list)
			flag=2
			print diction
			diction={}
	return return_list	

	
#file=open("Kupplungssteller.dbc","r")
#dbcDataReader(file)
#file.close()



