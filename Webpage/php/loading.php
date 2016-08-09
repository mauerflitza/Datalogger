<?php
// ajax load.php
$errors		= array();	//array to hold validation errors
$data		= array();	//array to pass data back
$values		= array();
// validate the variables ========================================
	// if any of these variables don't exist, add an error to our $errors array
	//+++++++++++++++++++++++++++++++++++++++++
// return a response ==============================================
	// if there are any errors aray, return a success boolean of false
	// DO ALL YOUR FORM PROCESSING HERE
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
