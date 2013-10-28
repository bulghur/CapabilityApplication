console.log('Loaded scriptjson.js');
//Associated with /ajaxjson

function handleResponse(data){
	console.log("scriptjson: Got from the server: " + data);
}

function handleDDBSelect(e){
	var proc_id = $('#proc_id').val();
	console.log('scriptjson:User selected ' + proc_id);
	$('#output').append('<li>' + proc_id + '</li>');
	$.ajax('/ajaxjson', {
	    type: "POST",
	    data:{
	            text: proc_id
	    }, 
	    success: handleResponse
	    // error:
	});
}

$(document).ready(function(){
    $('#process').click(handleClick);
})
