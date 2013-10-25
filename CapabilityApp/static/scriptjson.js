console.log('Loaded scriptjson.js');

function handleResponse(ddb){
	console.log("Got from the server: " + ddb);
	$('#processsteps').append(ddb);
	$.ajax('/ajaxjson', {
	    type: "POST",

	});
}

function handleDDBSelect(e){
	var proc_id = $('#proc_id').val();
	console.log('User selected ' + proc_id);
	$('#output').append('<li>' + proc_id + '</li>');
	$.ajax('/ajaxjson', {
	    type: "POST",
	    data:{
	            text: proc_id
	    }, 
	    success: handleResponse
	});
}

$(document).ready(function(){
    $('#process').click(handleClick);
})

function displayDate(e)
{
return "hello"
console.log('Howdy');
}