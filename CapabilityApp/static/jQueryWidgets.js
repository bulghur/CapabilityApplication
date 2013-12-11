
$(function() {
$( "#tabs" ).tabs({active: 3});
});


/*
   	<!<script>
			$(document).ready(function() {
				//When page loads...
				$(".tab_content").hide(); //Hide all content
				$("ul.tabs li:first").addClass("active").show(); //Activate first tab
				$(".tab_content:first").show(); //Show first tab content
				//On Click Event
				$("ul.tabs li").click(function() {
					$("ul.tabs li").removeClass("active"); //Remove any "active" class
					$(this).addClass("active"); //Add "active" class to selected tab
					$(".tab_content").hide(); //Hide all tab content
					var activeTab = $(this).find("a").attr("href"); //Find the href attribute value to identify the active tab + content
					$(activeTab).fadeIn(); //Fade in the active ID content
					return false;
				});
			});
	</script>
 */

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