<?php
// Writes the Saved data into a textfile
//Data is the html-code, Start/Stop Value and Sample Rates
$data		= array();	//array to pass data back
$values		= array();
	$savings = fopen('/home/pi/datalogger/loggerconfigs/savings.txt','r');
	if($savings) {
	while (($line = fgets($savings)) !== false) {
		if($pos = strpos($line,"StartValues:") !== false) {
		$values['Start'] = substr($line,strlen("StartValues:"));}
		elseif($pos = strpos($line,"SampleRates:") !== false) {
		$values['Rates'] = substr($line,strlen("SampleRates:"));}
	}


	//show a message of success and provide a true success variable
	$data['success'] = true;
	$data['message'] = 'Success!';
	$data['data'] = $values;
	//return all your data to an AJAX call
	echo json_encode($data);
	}
?>
