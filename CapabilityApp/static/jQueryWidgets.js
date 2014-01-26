





$(function() {
$( "#datepicker" ).datepicker({ dateFormat: "yy-mm-dd" });
});
	

$(document).ready(function(){
	
      $( "#menu" ).menu({  
          select: function( event, ui ) { 
    	  var proc_step_nm = (ui.item.children().attr('proc_step_nm'));
          alert("You have selected " + proc_step_nm  + " to operate.");
          var proc_step_id = ui.item.children().attr('proc_step_id');
          //$('#proc_step_id_value').append('<li>' + proc_step_id + '</li>');
          $('#proc_step_id_value').append('<input type="hidden" name="proc_step_id" id="proc_step_id" value=' + proc_step_id + '>');
          document.getElementById("proc_step_id").innerHTML="proc_step_id";
          console.log ("proc_step_id = " + proc_step_id)
          console.log ("proc_step_nm = " + proc_step_nm)}   
            	
      }); 
}); 