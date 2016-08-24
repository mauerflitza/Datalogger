ws = new WebSocket("ws:127.0.0.1:8888");
ws.onmessage = function(entry) {
	end = new Date().getTime();
	//console.log('RUNTIME: ', end-start);
	message = entry.data;
	console.log('Message: ',message);

};

ws.onclose = function(entry) { 
	console.log("Connection closed");
}
ws.onopen = function(evt) { 
console.log("Connection open ...");
}
