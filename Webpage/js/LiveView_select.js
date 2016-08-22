//*************************************************
//Add one row to the Live-View-List
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
//Delete a signal from the LiveView
//*************************************************
function deleteRow(r) {
var i = r.parentNode.parentNode.rowIndex;
document.getElementById("Sign_table").deleteRow(i);		
}

//function loader(){
//	$(".sig_namen").each(function(){
//	sig_namen=sig_namen.concat($(this).text());
//	sig_namen=sig_namen.concat(',');
//	alert(sig_namen);
//});
//}

