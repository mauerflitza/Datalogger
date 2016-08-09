//*************************************************
//Add one row to the signal-specification-list
//*************************************************
var myFuncCalls=0;
websocketwert=3;
function selector(caller){
	var table = document.getElementById('Disp_table');
	var box=document.getElementById('Disp_table_div');
	var div=document.createElement('div');
	var vorhanden=document.getElementById(caller.innerHTML);
	if (!vorhanden){
		div.style.visibility="visible";
		div.innerHTML = '<p>'+caller.innerHTML+': '+websocketwert+'</p>';
		div.setAttribute('class',"Anzeige");
		div.setAttribute('id',caller.innerHTML);
		box.appendChild(div);
	myFuncCalls++;
}}
//*************************************************
//Delete a row of the signal specification-list
//*************************************************
function deleteRow(r) {
var i = r.parentNode.parentNode.rowIndex;
document.getElementById("Sign_table").deleteRow(i);		
}

//*************************************************
//jQuery-function to set the Start/Stop Input Field
//*************************************************
$(document).ready(function () {
$('#Auflistung').on('change','input:radio', function() {
$('table tbody tr').each(function() {
		$(this).find("td").eq(3).css('visibility', 'hidden');
		$(this).find("td").eq(3).find("input").val('');})
	if ($('input[name=condition]:checked', '#Auflistung')){
		$(this).closest("td").next().css('visibility', 'visible');}

   })
});

function saver(){
//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
//Wichtig für Speichern der Webpage
//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
var Samplerates="";
var StartVal= "";
var sig_namen= "";
$(".startcon").each(function() {
    StartVal=StartVal.concat($(this).val());
	StartVal=StartVal.concat(',');	
});
StartVal = StartVal.substring(0, StartVal.length - 1);
$(".sampleselection").each(function() {
    Samplerates=Samplerates.concat($(this).val());
	Samplerates=Samplerates.concat(',');
});
$(".sig_namen").each(function() {
	sig_namen=sig_namen.concat($(this).text());
	sig_namen=sig_namen.concat(',');
	alert(sig_namen);
});
Samplerates = Samplerates.substring(0, Samplerates.length - 1);
sig_namen = sig_namen.substring(0, sig_namen.length - 1);
var html_site = ($( 'body' ).html().toString());
//<head muss manuell hinzugefügt werden>
$("#webpage").val(html_site);
$("#SampleRates").val(Samplerates);
$("#StartVal").val(StartVal);
alert(sig_namen);
}

function loader(){
	$(".sig_namen").each(function(){
	sig_namen=sig_namen.concat($(this).text());
	sig_namen=sig_namen.concat(',');
	alert(sig_namen);
});
}

