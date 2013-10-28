console.log('Loaded script.js');

function handleResponse(data){
	console.log('Got from server: ' + data);
}

function handleDDBSelect(e){
	var text = $('#proc_id').val();
	console.log('script.js: user typed ' + text);
	$('#output').append('<li>' + text + '</li>');
	$.ajax('/', { 
		type: 'POST',
		data: 
		{
			text: text
		},
		success: handleResponse	
	});
}

$(document).ready(function(){
	$('#process').click(handleClick);
})