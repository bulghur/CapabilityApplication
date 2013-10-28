// Associated with /jQueryJSON 
console.log('Loaded jQueryScript.js'); //make sure this ref in the html

var  theData; //the Model :: Model View Controller

function showData(data){
	console.log(data); 
	theData = data;	
	$('#output').append('<li>' + data + '</li>'); //writes/appends to html
	
}
	
function handleClick(e) 
	$.ajax('/jQueryJSON',{ // this makes the Ajax handler call
		type: "GET", // set get or post
		data: {
			fmt: 'json' // format of the request
		}, 
		success: showData // goes up to showData function
	});

$(document).ready(function(){
	$('#getitButton').on('click', handleClick); // from page controller to call function
	console.log('Button clicked');
	
});