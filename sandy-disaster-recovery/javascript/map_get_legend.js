$(function() {
  // TODO
  // get inc def query
  // get phase_number from URL, none set to 0
  // create legend in html, and add to proper div
  
  $.getJSON( "/api/get_incident_definition", function( data ) {
    
    var phase_number = GetUrlValue("phase_number");
    
    if(typeof phase_number == 'undefined'){
      phase_number = 0;
    }
    
    var current_form = data[phase_number];
    var work_type_object;
    var keys_array = [];
    
    for (var i = 0; i < current_form.length; i++) {
      if (current_form[i]._id == "work_type") {
	work_type_object = current_form[i];
	for (var key in work_type_object) {
	  if (key.indexOf("select_option") != -1) {
	   keys_array.push(work_type_object[key]); 
	    
	  }
	}
      }
    }    
    
    var html_string = "";
    var filter_string = 'Open: <input type="checkbox" name="filter" id="open"><br>Closed: <input type="checkbox" name="filter" id="closed"><br>Claimed: <input type="checkbox" name="filter" id="claimed"><br>Unclaimed: <input type="checkbox" name="filter" id="unclaimed"><br>';
    for (var j = 0; j < keys_array.length; j++) {
      var new_string = keys_array[j] + '<img src="/icons/' + keys_array[j] + '_green.png"/>';
      html_string = html_string + new_string;
      
      var new_filter = keys_array[j] + ': <input type="checkbox" name="filter" id="' + keys_array[j] + '"><br>';
      filter_string = filter_string + new_filter;
    }
    $("#legend_div").append(html_string);
    $("#filters_div").append(filter_string);

    

    
  });
  
});


function GetUrlValue(VarSearch){
    var SearchString = window.location.search.substring(1);
    var VariableArray = SearchString.split('&');
    for(var i = 0; i < VariableArray.length; i++){
        var KeyValuePair = VariableArray[i].split('=');
        if(KeyValuePair[0] == VarSearch){
            return KeyValuePair[1];
        }
    }
}