/* This file contains all customised scripts as the single point of organising scripts 
 * and getting them out of the html docs. 
 */
var selectedCase = null;
//var proc_step_id = null;




//Generic jQuery date picker
$(function() {
$( "#datepicker" ).datepicker({ dateFormat: "yy-mm-dd" });
});

//Grab the Instance Key to get the selected Instance Key and use it to submit the form CaseReview
function getInstanceKey(lnk){
	var instance_key = lnk.getAttribute('value');
	console.log ("Instance Key is: " + instance_key);
	document.getElementById("inputTextHackThatNeedsToBeCodedMoreBeautifully").innerHTML = "<input type='text' name='instance_key' id='instance_key' value=" + instance_key +">";
	document.getElementById("EditInstance").submit();
	}

//Populate selectedCase for CreateInstance Submission.
function caseConfirmMessage(){
	var case_idraw = document.getElementById("case_id");
	var case_id = case_idraw.options[case_idraw.selectedIndex];
	selectedCase = case_id.innerHTML;
	//alert("You've selected: " + selectedCase)
	}


// This menu function is used for providing menu items for choosing processes
$(document).ready(function(){
	
      $( "#menu" ).menu({
    	  
          select: function( event, ui ) { 
	    	  var proc_step_nm = (ui.item.children().attr('proc_step_nm'));
	          var proc_step_id = ui.item.children().attr('proc_step_id');
	          
	          $('#proc_step_id_value').append('<input type="hidden" name="proc_step_id" id="proc_step_id" value=' + proc_step_id + '>');
	          document.getElementById("proc_step_id").innerHTML="proc_step_id";
	          var holdhere = proc_step_id;
	          console.log ("holdhere = " + holdhere);
	          console.log ("proc_step_nm = " + proc_step_nm);
	          console.log ("case_id = " + selectedCase);
	          if (proc_step_id == null || (selectedCase == null || selectedCase == "Select a Case" )){
	        	  alert("You failed to select a Case and/or a Process Step.  Please try again.");
	          }
	          else{
	        	  if (confirm("You have selected Process Step: " + proc_step_nm  + "... and Case: " 
	        		  + selectedCase + ".")) {
	        		  proc_step_id = holdhere;
	        		  document.getElementById("CreateInstance").submit();
	    	          console.log ("proc_step_id = " + proc_step_id);
	    	          console.log ("proc_step_nm = " + proc_step_nm);
	    	          console.log ("case_id = " + selectedCase);
	        		  }
        		  else{
        			  
        			  
        		  };
        		  
	        	  
	        	  }
	          
	          
          } 
            	
      }); 
});


//Checkbox functionality
	var CheckboxHandler = new Object();
	function testCheckbox(oCheckbox)
	{
	    var checkbox_val = oCheckbox.value;
	    if (oCheckbox.checked == true)
	    {
	        alert("Checkbox with name = " + oCheckbox.name + " and value =" +
	                checkbox_val + " is checked");
	    }
	    else
	    {
	        alert("Checkbox with name = " + oCheckbox.name + " and value =" +
	              checkbox_val + " is not checked");
	    }
	}



		
//A collection of undefined scripts

//from operateprocess.html

