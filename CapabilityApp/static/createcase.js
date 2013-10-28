// creates case
console.log('Loaded window');

function showData(data){
	console.log(data.name); 
}
	
function createCase(e){
	  var proc_step_id = $('#proc_step_id').val();
	  console.log("User selected :" + proc_step_id);
	  var fname=prompt("Please enter a case name:","case name"); // sources the input from the box
	  document.getElementById("msg").innerHTML = "Case Namey: " + fname; // this writes a message 
	  console.log('Case = : ' + fname); //echos the contents from the box
		};
