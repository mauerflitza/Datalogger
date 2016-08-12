//*************************************************
//Add one row to the signal-specification-list
//*************************************************
var myFuncCalls=0;
function selector(caller){
	var form = document.getElementById('Auflistung');
	var submit = document.getElementById('submit_btn');
	var table = document.getElementById('Sign_table');
	var vorhanden=document.getElementById(caller.innerHTML);
	if (!vorhanden){
		if (myFuncCalls<=0){
			submit.setAttribute('style', 'visibility:visible;');}
		table.style.visibility="visible";
		row = table.insertRow(-1);
		var cell1 = row.insertCell(0);
		var cell2 = row.insertCell(1);
		var cell3 = row.insertCell(2);
		var cell4 = row.insertCell(3);
		var cell5 = row.insertCell(4);
		cell1.innerHTML = '<input readonly name="NameArray[]" type="text" value="'+caller.innerHTML+'">';
		cell2.innerHTML = '<select name="samplerates[]" class="sampleselection">\
		<option value="1">1ms</option><option value="10">10ms</option><option value="100">100ms</option></select>';
		cell2.setAttribute('id',caller.innerHTML);
		cell3.setAttribute('id','test');
		cell3.innerHTML = ' <input type="radio" name="condition" value='+caller.innerHTML+'>';
		cell4.style.visibility='hidden';
		cell4.innerHTML = '<input type="text" name="start[]" class= "startcon">';
		cell5.innerHTML = '<a href=\'#\' onclick=\'deleteRow(this)\'> \
		<img src="../Picture/delete.png" alt="Delete signal" style="width:34px;height:34px;border:0;vertical-align:middle;"></a>';}
	myFuncCalls++;
}
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
StartVal = $("input[type='radio'][name='condition']:checked").closest("td").next().find("input").val();
console.log(StartVal);
$(".sampleselection").each(function() {
    Samplerates=Samplerates.concat($(this).val());
	Samplerates=Samplerates.concat('/');
});
var html_site = ($( 'body' ).html().toString());
//<head muss manuell hinzugefügt werden>
$("#webpage").val(html_site);
$("#SampleRates").val(Samplerates);
$("#selected").val($("input[type='radio'][name='condition']:checked").val());
$("#StartVal").val(StartVal);
}
