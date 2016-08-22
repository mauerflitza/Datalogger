<?php
$data		= array();	//array to pass data back

	//Saves the Webpage with all necassery data to a file
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
