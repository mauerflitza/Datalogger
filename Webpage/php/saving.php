<?php
// ajax save.php
$errors		= array();	//array to hold validation errors
$data		= array();	//array to pass data back
// validate the variables ========================================
	// if any of these variables don't exist, add an error to our $errors array
	//+++++++++++++++++++++++++++++++++++++++++
// return a response ==============================================
	// if there are any errors aray, return a success boolean of false
	// DO ALL YOUR FORM PROCESSING HERE
	$savings = fopen('/home/pi/datalogger/loggerconfigs/savings.txt','w');
	fwrite($savings,"StartValues:");
	fwrite($savings,$_POST['StartVal'] . "/" . $_POST['selected'] . "/" . "\n");
	fwrite($savings,"SampleRates:");
	fwrite($savings,$_POST['SampleRates'] . "\n");
	fwrite($savings,"html:");
	fwrite($savings,$_POST['webpage'] . "\n");

	fclose($savings);
	//show a message of success and provide a true success variable
	$data['success'] = true;
	$data['message'] = 'Success!';
	$data['data'] = $_POST;
	//return all your data to an AJAX call
	echo json_encode($data);
?>
