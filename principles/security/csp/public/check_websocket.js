function doWebsocket(addr, data, div_id) {
	var socket = io.connect(addr);

	socket.on('connect', function() {
	  socket.emit('msg', {
	    data: data
	  })
	});

	socket.on('reply', function(msg) {
		window.document.getElementById(div_id).textContent = msg;
	});
}

doWebsocket('http://127.0.0.1:9050/wstest', 'message to main server', 'websocket9050');
doWebsocket('http://127.0.0.1:9051/wstest', 'message to evil server', 'websocket9051');
