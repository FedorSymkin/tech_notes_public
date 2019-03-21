function doAjax(addr, method, result_div_id) {
	var xhr = new XMLHttpRequest();
	xhr.open(method, addr);
	xhr.onload = function() {
	    if (xhr.status === 200) {
			window.document.getElementById(result_div_id).textContent = xhr.responseText;
	    }
	    else {
	        console.log('Request to ' + addr + ' failed. Returned status of ' + xhr.status);
	    }
	};
	xhr.send();
}

doAjax('/some_dynamic_resource/some_data_from_client_to_main', 'GET', 'ajax9050');
doAjax('/some_dynamic_resource/some_data_from_client_to_main_post', 'POST', 'ajaxPost9050');
doAjax('http://127.0.0.1:9051/some_dynamic_resource/some_data_from_client_to_evil', 'GET', 'ajax9051');
doAjax('http://127.0.0.1:9051/some_dynamic_resource/some_data_from_client_to_evil_post', 'POST', 'ajaxPost9051');
