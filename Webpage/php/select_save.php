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
	$selection = fopen('/home/pi/datalogger/loggerconfigs/selection.txt','w');
	fwrite($selection,"{");
	$samplerates=$_POST['samplerates'];
	$start=$_POST['start'];
	foreach ($_POST['NameArray'] as $key=>$element) {
	  fwrite($selection,'"' . $element .'"' . ":[" . $samplerates[$key] . "," . $start[$key] . "],");
	}
	fwrite($selection,"}" . "\n");
	foreach ($_POST['start'] as $element) {
	if(strlen($element)>0)  {
	fwrite($selection,$element); }
	}
	fclose($selection);
	$namelist=fopen('/home/pi/datalogger/loggerconfigs/signals/signals.txt','w');
	foreach ($_POST['NameArray'] as $element) {
	fwrite($namelist, $element . " "); }
	fclose($namelist);
	//show a message of success and provide a true success variable
	$data['success'] = true;
	$data['message'] = 'Success!';
	$data['data'] = $_POST;
	//return all your data to an AJAX call
	echo json_encode($data);
?>
