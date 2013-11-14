$(function() {  
  // set up the page by hiding appropriate divs
  hide_divs();
  hide_tabs();
//   hide_sidebar_form_creator();
//   hide_phases_list();
//     
 

  // name appropriate variables, that will be used throughout
  
  // when adding options to a select
  var select_options_array = [];
  
  // when adding options to a radio
  var radio_options_array = [];

  // where the cumulative json for the individual form will be kept
  var form_json_array = [];
  
  // where the json for all the arrays will be kept. This will go into our select
  var phases_json_array = [];
  
  
  var incident_short_name = GetUrlValue("incident_short_name");
  var phase_id = GetUrlValue("phase_id");
  get_form_json(phase_id, incident_short_name, form_json_array);

  
  $("#click_to_load").click(function() {
  });
  
  $("#click_to_read").click(function() {
//     console.log(form_json_array);
  });
  // ----------- FORM LABEL FUNCTIONS ----------------
  $("#add_label").click(function() {
	hide_divs();	
	$("#label_div").show();
  });
  
  
  $("#add_label_to_form").click(function() {
	hide_divs();
	add_label_input(form_json_array);
	$("#label_form").trigger('reset');
	add_to_form(form_json_array);
  });
  
  function add_label_input(form_json_array) {
    var label_value = $("#label_name").val();
    order_number = form_json_array.length;
    var label_json = {
      "type": "label",
      "label": label_value,
      "order_number": order_number,

    }
    form_json_array.push(label_json);
  }
  
  // ----------- FORM PARAGRAPH FUNCTIONS ----------------
  
  $("#add_paragraph").click(function() {
	hide_divs();
	$("#paragraph_div").show();
  });
  
  $("#add_paragraph_to_form").click(function() {
	hide_divs();
	add_paragraph_input(form_json_array);
	$("#paragraph_form").trigger('reset');
	add_to_form(form_json_array); 
  });
  
  function add_paragraph_input(form_json_array) {
    var paragraph_value = $("#paragraph").val();
    order_number = form_json_array.length;
    
    var paragraph_json = {
      "type": "paragraph",
      "paragraph": paragraph_value,
      "order_number": order_number,

    }
    form_json_array.push(paragraph_json);
  }
  
  // ----------- FORM HEADER FUNCTIONS ----------------
  $( "#add_header" ).click(function() {
	hide_divs();
	$("#header_div").show();
  });
    
  $( "#add_header_to_form" ).click(function() {
	hide_divs();
	add_header_input(form_json_array);
	$("#header_form").trigger('reset');
	
	add_to_form(form_json_array);
  });
  
  function add_header_input(form_json_array){
    var header_value = $("#header_label").val();
    order_number = form_json_array.length;

    var header_json = {
      "type": "header",
      "header": header_value,
      order_number: order_number,

    }
    form_json_array.push(header_json);
  }

  // ----------- FORM SUBHEADER FUNCTIONS ----------------
  $( "#add_subheader" ).click(function() {
	hide_divs();
	$("#subheader_div").show();
  });
    
  $( "#add_subheader_to_form" ).click(function() {
	hide_divs();
	add_subheader_input(form_json_array);
	$("#subheader_form").trigger('reset');
	add_to_form(form_json_array);
  });
  
  function add_subheader_input(form_json_array){
    var subheader_value = $("#subheader_label").val();
    order_number = form_json_array.length;

    var header_json = {
      "type": "subheader",
      "subheader": subheader_value,
      "order_number": order_number,
    }
    form_json_array.push(header_json);
  }
  
  // ----------- TEXT FIELD FUNCTIONS ----------------
  
  
  // Show the form that is responsible for adding a text field
  $( "#add_text" ).click(function() {
	hide_divs();
	$("#text_div").show();
  });
  
  // read the form click, and send to proper function
  $( "#add_text_to_form" ).click(function() {
      hide_divs();

      add_text_input(form_json_array);
      $("#tabs-2").empty();
      $("#text_form").trigger('reset');  
      add_to_form(form_json_array);
  });
  
  
  // add form input to form_json_array
  function add_text_input(form_json_array) {
    var text_label = $("#text_label").val();
    var text_required = $('#text_required').prop('checked')
    var text_sensitive = $('#text_sensitive').val();
    var text_id = $("#text_id").val();
    var validations = $("#text_validations").val();
    order_number = form_json_array.length;

    var text_json = {
      type: "text",
      label: text_label,
      required: text_required,
      sensitive: text_sensitive,
      _id: text_id,
      order_number: order_number,
      validations: validations

    }    
    form_json_array.push(text_json);
      var jString = JSON.stringify(form_json_array);
      console.log(jString);
      console.log("#@#")

  }
  
  
  // ----------- TEXTAREA FUNCTIONS ----------------
  
  // show the textarea form
  $("#add_textarea").click(function() {
      hide_divs();
      $("#textarea_div").show();
  });
    
  
  // read the form click, and send to proper function
  $( "#add_textarea_to_form" ).click(function() {
	hide_divs();
	add_textarea_input(form_json_array);
	$("#textarea_form").trigger('reset');
	
	add_to_form(form_json_array);
  });
  
  // add form input to form_json_array
  function add_textarea_input(form_json_array) {
    var textarea_label = $("#textarea_label").val();
    var textarea_id = $("#textarea_id").val();
    var textarea_validations = $("#textarea_validations").val();
    order_number = form_json_array.length;

    var header_json = {
      "type": "textarea",
      "label": textarea_label,
      "_id": textarea_id,
      "order_number": order_number,
      "validations": textarea_validations
    }
    form_json_array.push(header_json);
  }
  
  // ----------- CHECKBOX FUNCTIONS ----------------
  $( "#add_checkbox" ).click(function() {
	hide_divs();
	$("#checkbox_div").show();
  });
  
  $( "#add_checkbox_to_form" ).click(function() {
    hide_divs();
    add_checkbox_input(form_json_array);
    $("#tabs-2").empty();
    $("#checkbox_form").trigger('reset');

    add_to_form(form_json_array);
  }); 
  
  function add_checkbox_input(form_json_array) {
    var checkbox_label = $("#checkbox_label").val();
    var checkbox_default = $("#checkbox_default").val();
//     var checkbox_required = $("#checkbox_required").prop('checked');
    var checkbox_sensitive = $("#checkbox_sensitive").val();
    var checkbox_id = $("#checkbox_id").val();
    var checkbox_validations = $("#checkbox_validations");

    order_number = form_json_array.length;
    
    var checkbox_json = {
      type: "checkbox",
      label: checkbox_label,
      _default: checkbox_default,
//       required: checkbox_required,
      sensitive: checkbox_sensitive,
      _id: checkbox_id,
      order_number: order_number,
    }
    form_json_array.push(checkbox_json);
  }
    
    
  // ----------- SELECT FUNCTIONS ----------------

  $( "#add_select" ).click(function() {
	hide_divs();
	$("#select_div").show();
  });  
  
  $( "#add_select_to_form" ).click(function() {
    hide_divs();
    add_select_input(form_json_array, select_options_array);
    $("#tabs-2").empty();
    $("#select_form").trigger('reset');
    clear_select_options(select_options_array);
    // only below clears array
    select_options_array = [];
    
    add_to_form(form_json_array);
  }); 
  
  function add_select_input(form_json_array, select_options_array) {
    var select_label = $("#select_label").val();
    var select_option_1 = $("#select_option_1").val();
    var select_default = $("#select_default").val();
    var select_required = $("#select_required").prop('checked');
    var select_sensitive = $("#select_sensitive").val();
    var select_id = $("#select_id").val();
    var order_number = form_json_array.length;
	
    var select_json = {
      type: "select",
      label: select_label,
      select_option_1: select_option_1,
      required: select_required,
      sensitive: select_sensitive,
      _id: select_id,
      order_number: order_number,
    }
    
    for (var i = 0; i < select_options_array.length; i++) {
      var element = '#' + select_options_array[i];
      select_json[select_options_array[i]] = $('#' + select_options_array[i] +'').val();
    }
      
    form_json_array.push(select_json);
    select_options_array = [];
  }

  function add_select_option(select_options_array) {
    var array_length = select_options_array.length;
    var new_length = array_length + 2;
    var new_options_string = "select_option_" + new_length;
    select_options_array.push(new_options_string);
    return select_options_array;
  }  
  
  $( "#add_select_option" ).click(function() {
    add_select_option(select_options_array);
    var i = select_options_array.length - 1;
    var option_number = i + 2;
    var new_line = 'Option ' + option_number + ':  <input type="text" id="'+ select_options_array[i] + '" name="'+ select_options_array[i] + '"><br>';
    var new_option = '<option value="' + select_options_array[i] + '">Option '+ option_number + '</option>';
    $("#add_options_to_select").append(new_line);
  });
  
  $("#clear_select_options").click(function() {
    select_options_array = [];
    var new_option = 'Option 1:  <input type="text" id="select_option_1" name="select_option_1"><br>';
    var new_select = '<option value="select_option_1">Option 1</option>';
    $("#add_options_to_select").empty();
    $("#add_options_to_select").append(new_option);
  });
  
  // ----------- RADIO FUNCTIONS ----------------
  
  $( "#add_radio" ).click(function() {
	hide_divs();
	$("#radio_div").show();
  });

  $( "#add_radio_to_form" ).click(function() {
	hide_divs();
	add_radio_input(form_json_array, radio_options_array);
	// only below clears array
	radio_options_array = [];
	$("#tabs-2").empty();
	$("#radio_form").trigger('reset');
	clear_radio_options();
	add_to_form(form_json_array);
  });     
  
  function add_radio_input(form_json_array, radio_options_array) {
    var radio_label = $("#radio_label").val();
    var radio_option_1 = $("#radio_option_1").val();
    var radio_required = $("#radio_required").prop('checked');
    var radio_sensitive = $("#radio_sensitive").val();
    var radio_id = $("#radio_id").val();
    var radio_low_hint = $("#radio_low_hint").val();
    var radio_high_hint = $("#radio_high_hint").val();

    var order_number = form_json_array.length
      
    var radio_json = {
      type: "radio",
      label: radio_label,
      radio_option_1: radio_option_1,
      required: radio_required,
      sensitive: radio_sensitive,
      _id: radio_id,
      low_hint: radio_low_hint,
      high_hint: radio_high_hint,
      order_number: order_number,
    }
    
    for (var i = 0; i < radio_options_array.length; i++) {
      var element = '#' + radio_options_array[i];
      radio_json[radio_options_array[i]] = $('#' + radio_options_array[i] +'').val();
    } 
    form_json_array.push(radio_json);
  }
  
  function add_radio_option(radio_options_array) {
    var array_length = radio_options_array.length;
    var new_length = array_length + 2;
    var new_options_string = "radio_option_" + new_length;
    radio_options_array.push(new_options_string);
    return radio_options_array;
  }

  $( "#add_radio_option" ).click(function() {
    add_radio_option(radio_options_array);
    var i = radio_options_array.length - 1;
    var option_number = i + 2;
    var new_line = 'Option ' + option_number + ':  <input type="text" id="'+ radio_options_array[i] + '" name="'+ radio_options_array[i] + '"><br>';
    var new_option = '<option value="' + radio_options_array[i] + '">Option '+ option_number + '</option>';
    $("#add_options_to_radio").append(new_line);
  });  

  $("#clear_radio_options").click(function() {
    radio_options_array = [];
    var new_option = 'Option 1:  <input type="text" id="radio_option_1" name="radio_option_1"><br>';
    var new_select = '<option value="radio_option_1">Option 1</option>';
    $("#add_options_to_radio").empty();
    $("#add_options_to_radio").append(new_option);
  });

  
  // ----------- ADD PERSONAL MODULE ----------------
  $("#add_personal_info_module").click(function() {
    var personal_module_object = JSON.parse(personal_info_module_string);
    for (var i = 0; i < personal_module_object.length; i++) {
      form_json_array.push(personal_module_object[i]);

    }
      add_to_form(form_json_array);
  });
  
  // ----------- ADD STATUS MODULE ----------------
  $("#add_status_info_module").click(function() {
    var status_module_object = JSON.parse(status_info_module_string);
    for (var i = 0; i < status_module_object.length; i++) {
      form_json_array.push(status_module_object[i]);
    }
    add_to_form(form_json_array);
  });
  // ----------- END FORM CONTROL FUNCTIONS ----------------


  // ----------- EDIT FORM JQUERY EVENTS ----------------
  

  $("#show_html").click(function() {
    hide_tabs();
    $("#tabs-1").show();
  });
  
  $("#show_json").click(function() {
    hide_tabs();
    $("#tabs-2").show();
  });

  $("#form_table").on( "click", ".move_one_position_up",  function() {
    order_number = $(this).attr("id");
    if (order_number < 2) {
      return;
    }
    if (swap_order_numbers_up(order_number, form_json_array)) {
      form_json_array.move_up(parseInt(order_number));
      add_to_form(form_json_array);
    }
  });
  
  
  $("#form_table").on( "click", ".move_one_position_down",  function() {
    order_number = $(this).attr("id");
      if (order_number > form_json_array.length - 2) {
	return;
      }
      if (swap_order_numbers_down(order_number, form_json_array)) {
      form_json_array.move_down(parseInt(order_number));
      add_to_form(form_json_array);
    }
  });

  

  $("#save_all_changes").click(function() {
    save_changes(form_json_array);
  
  });
  $("#tabs-1").show();


  // ----------- EDIT FORM JQUERY EVENTS ----------------

});

//------------------------------------------------------------------------------------------------------------------
// helper functions
function hide_divs() {
  $("#select_div").hide();
  $("#radio_div").hide();
  $("#text_div").hide();
  $("#checkbox_div").hide();
  $("#header_div").hide();
  $("#label_div").hide();
  $("#paragraph_div").hide();
  $("#subheader_div").hide();
  $("#textarea_div").hide();
}
function hide_tabs() {
  $("#tabs-1").hide();
  $("#tabs-2").hide();
}

function clear_options_array(options_array) {
   return ["options_1"]
}

function remove_option(options_array) {
   options_array.pop();
   return options_array;
}

function add_checkbox_input(form_json_array) {
  var checkbox_label = $("#checkbox_label").val();
  var checkbox_default = $("#checkbox_default").val();
  var checkbox_required = $("#checkbox_required").prop('checked');
  var checkbox_sensitive = $("#checkbox_sensitive").val();
  var checkbox_id = $("#checkbox_id").val();
//   var checkbox_validations = $("#checkbox_validations");

  order_number = form_json_array.length;
  
  var checkbox_json = {
    type: "checkbox",
    label: checkbox_label,
    _default: checkbox_default,
    required: checkbox_required,
    sensitive: checkbox_sensitive,
    _id: checkbox_id,
//     validations: checkbox_validations,
    order_number: order_number,
  }
  form_json_array.push(checkbox_json);
}

function add_select_input(form_json_array, select_options_array) {
  var select_label = $("#select_label").val();
  var select_option_1 = $("#select_option_1").val();
  var select_default = $("#select_default").val();
  var select_required = $("#select_required").prop('checked');
  var select_sensitive = $("#select_sensitive").val();
  var select_id = $("#select_id").val();
  var order_number = form_json_array.length;
       
  var select_json = {
    type: "select",
    label: select_label,
    select_option_1: select_option_1,
    required: select_required,
    sensitive: select_sensitive,
    _id: select_id,
    order_number: order_number,
  }
  
  for (var i = 0; i < select_options_array.length; i++) {
    var element = '#' + select_options_array[i];
    select_json[select_options_array[i]] = $('#' + select_options_array[i] +'').val();
  }
    
  form_json_array.push(select_json);
  select_options_array = [];
}


//------------------------------------------------------------------------------------------------------------------
// read from incremented json to the html div. This gives users a chance to see what the div will look like.

function read_json_to_html(form_json_array) {
  $("#form_label").empty();
  $("#form_paragraph").empty();
  $("#form_table").empty();
  

  for (var i=0; i < form_json_array.length; i++) {
    if(form_json_array[i].type == "label") {
    buttons_string = add_edit_buttons(form_json_array[i].order_number);    
      $("#form_table").append('<h2>' + buttons_string + form_json_array[i].label + '</h2>');
    }
    if(form_json_array[i].type == "paragraph") {
      buttons_string = add_edit_buttons(form_json_array[i].order_number);
      $("#form_table").append( buttons_string + form_json_array[i].paragraph + '<br>');
    }
    if(form_json_array[i].type == "radio") {
      buttons_string = add_edit_buttons(form_json_array[i].order_number);
      var options_array = []
      for (var key in form_json_array[i]) {
        var key_string = key.toString();
        if (key_string.indexOf("radio_option_") == 0) {
	    options_array.push(key_string);
        }
      }
      
      var req = "";
      if (form_json_array[i].required) {
        req = "*";
      }
      var radio_string = "";
      var radio_string_start = '</td></tr><tr><td class=question>' + buttons_string  + form_json_array[i].label + req + '</td><td class="answer"><table><tr><td>' + form_json_array[i].low_hint + '</td><td>';
      var radio_string_end = '<td>' + form_json_array[i].high_hint + '</td></tr></table></td></tr>';
      for (var j = 0; j < options_array.length; j++) {
        var options_string = "";
// 	if(form_json_array[i].radio_default == options_array[j]) {
//           var option_string = '<td><input id="' + form_json_array[i][options_array[j]] + '" name="' + form_json_array[i]._id + '" type="radio" value="' + form_json_array[i][options_array[j]] + '" checked="true"></td>';
// 	} else {
	  var option_string = '<td><input id="' + form_json_array[i][options_array[j]] + '" name="' + form_json_array[i]._id + '" type="radio" value="' + form_json_array[i][options_array[j]] + '"></td>';
// 	}

	radio_string = radio_string + option_string;
      }
      var final_radio_string = radio_string_start + radio_string + radio_string_end;
      $("#form_table").append(final_radio_string);

    }
    if(form_json_array[i].type == "select") {
      buttons_string = add_edit_buttons(form_json_array[i].order_number);
      var options_array = [];
      for (var key in form_json_array[i]) {
        var key_string = key.toString();
        if (key_string.indexOf("select_option_") == 0) {
	    options_array.push(key_string);
        }
      }
      var req = "";
      if (form_json_array[i].required) {
        req = "*";
      }
      var begin_option = '<tr><td class=question>' + buttons_string + form_json_array[i].label + req +'</td><td class="answer"><div class="form_field"><select class="" id="' + form_json_array[i]._id + '" name="' + form_json_array[i]._id + '">';
      var end_option = '</select></div></td></tr>';
      var select_string = '<option value="">Choose one</option>';

      for (var j = 0; j < options_array.length; j++) {
	  var option_string = "<option>" + form_json_array[i][options_array[j]] + "</option>";
	  select_string = select_string + option_string;
      }
      var all_string = begin_option + select_string + end_option;
      $("#form_table").append(all_string);
    }
    if(form_json_array[i].type == "header") {
      buttons_string = add_edit_buttons(form_json_array[i].order_number);
      var new_header = '<tr><td class="question"><h2>' + buttons_string + form_json_array[i].header + '</h2></tr></td>';
      $("#form_table").append(new_header);
    }
    
    if(form_json_array[i].type == "textarea") {
      buttons_string = add_edit_buttons(form_json_array[i].order_number);

      var new_textarea = '<tr><td class=question>'+ buttons_string + form_json_array[i].label + ':</td><td class="answer">\
      <div class="form_field"><textarea class="" id="' + form_json_array[i]._id + '" name="' + form_json_array[i]._id + '"></textarea></div>\
      </td></tr>'
      $("#form_table").append(new_textarea);
    }
    
    if(form_json_array[i].type == "subheader") {
      buttons_string = add_edit_buttons(form_json_array[i].order_number);
      var new_subheader = '<tr><td class="question"><h3>' + buttons_string + form_json_array[i].subheader + '</tr></td></h3>';
      $("#form_table").append(new_subheader);
    }
    
    else if(form_json_array[i].type == "text") {
      buttons_string = add_edit_buttons(form_json_array[i].order_number);
      var required = "";
      if (form_json_array[i].required) {
        var required = "*";
      }
      var new_text_input = '<tr><td class=question>' + buttons_string + form_json_array[i].label + ': <span class=required-asterisk>' + required + '</span></td><td class="answer"><div class="form_field"><input class="" id="' + form_json_array[i]._id + '" name="' + form_json_array[i]._id + '" type="text"/></div></td></tr>'
      $("#form_table").append(new_text_input);
    }
    
    else if (form_json_array[i].type == "checkbox") {
      buttons_string = add_edit_buttons(form_json_array[i].order_number);
      var required = "";
      var checked = "";
      if (form_json_array[i].required == true) {
        required = "*";
      }
      
      if (form_json_array[i]._default == "y") {
        checked = " checked";
      }
      var new_checkbox = '<tr><td class=question><label for="' + form_json_array[i]._id + '">' + buttons_string + form_json_array[i].label + required +'</label></td><td class="answer"><div class="form_field"><input class="" name="' + form_json_array[i]._id + '" type="hidden" value="n"/><input class="" id="' + form_json_array[i]._id + '" name="' + form_json_array[i]._id + '" type="checkbox" value="y"' + checked + '></div></td></tr>';
      $("#form_table").append(new_checkbox);

    }
    
  }

}

//------------------------------------------------------------------------------------------------------------------
// clear options for select form

function clear_select_options(select_options_array) {

  select_options_array = [];
  var new_option = 'Option 1:  <input type="text" id="select_option_1" name="select_option_1"><br>';
  var new_select = '<option value="select_option_1">Option 1</option>';
  $("#add_options_to_select").empty();
  $("#add_options_to_select").append(new_option);
}

//------------------------------------------------------------------------------------------------------------------
// clear options for radio form

function clear_radio_options() {

  radio_options_array = [];
  var new_option = 'Option 1:  <input type="text" id="radio_option_1" name="radio_option_1"><br>';
  var new_select = '<option value="radio_option_1">Option 1</option>';
  $("#add_options_to_radio").empty();
  $("#add_options_to_radio").append(new_option);  
}

function get_json(incident_short_name, phases_json_array) {
  $.getJSON( "/incident_definition_ajax", { incident_short_name: incident_short_name},  function( data ) {
    phases_json_array.push(JSON.parse(data.phases_json));
    if (data.phases_json == "[]") {
      show_first_phase_form(incident_short_name, incident_short_name);
    } else {
      read_phases_json_to_html(data.phases_json, incident_short_name);
    }
  });
}

function get_form_json(phase,incident_short_name, form_json_array) {
  
  $.getJSON( "/incident_definition_ajax", { incident_short_name: incident_short_name, phase: phase},  function( data ) {
    if (data.forms_json == "[]") {
      $("#form_label").append("<h2>Create a form by using the controls on the left</h2>");
      var phases_array = JSON.parse(data.phases_json);
      var phase_data = {
	"phase_id": phases_array[0].phase_id,
	"phase_name": phases_array[0].phase_name,
	"incident_short_name": incident_short_name,
	"phase_short_name": phases_array[0].phase_short_name,
	
      }
      form_json_array.push(phase_data);
      var jString = JSON.stringify(form_json_array);
//       console.log(1);
	  $("#tabs-2").empty();
      $("#tabs-2").append(jString);
    } else {
      $("#form_label").append('<h2><a href="/incident_edit_form">Edit Form</a></h2>');

//       form_json_array = [];
      var arr = JSON.parse(data.forms_json);
      var jString = "";
      var any_equal = false;
      for (var k = 0; k < arr.length; k++) {
	for (var j = 0; j < arr[k].length; j ++) {
	  if (arr[k][j]['phase_short_name'] == phase) {
	    any_equal = true;
	    form_json_arr = arr[k];

	    for (var b = 0; b < arr[k].length; b++) {
	      form_json_array.push(arr[k][b]);
	    }
      $("#form_label").append('<h2><a href="/incident_edit_form">Edit Form</a></h2>');
          jString = JSON.stringify(form_json_array);

	    read_json_to_html(form_json_array);
	  	    $("#tabs-2").empty();
	    $("#tabs-2").append(jString);
// 	          console.log(jString);

	  }
	}
      }
    
      if (!any_equal) {
// 	console.log(3);
	  show_sidebar_form_creator();
	var phases_array = JSON.parse(data.phases_json);
	
	for (var n = 0; n < phases_array.length; n++) {
	  if (phase == phases_array[n].phase_short_name) {
	    var phase_data = {
	      "phase_id": phases_array[n].phase_id,
	      "phase_name": phases_array[n].phase_name,
	      "incident_short_name": incident_short_name,
	      "phase_short_name": phases_array[n].phase_short_name
	    }
	    form_json_array.push(phase_data);
	    var jString = JSON.stringify(form_json_array);
	    $("#tabs-2").empty();
	    $("#form_table").empty();
	    $("#form_label").empty();
	    $("#form_label").append("<h2>Create a form by using the controls on the left</h2>");
	    $("#tabs-2").append(jString);
	  }
	
	}

      }
    }
  });
  show_sidebar_form_creator();
}

function show_first_phase_form(incident_short_name, incident_short_name) {
  $('#first_phase_form').append('<input type="hidden" name="incident_short_name" value="' + incident_short_name + '" />');
}

function read_phases_json_to_html(phases_json_array, incident_short_name) {
  var arr = JSON.parse(phases_json_array);
  $("#phases_list").empty();
  $("#phases_list").append('<option value="None">Choose a Phase</option>');
  for (var i = 0; i < arr.length; i++) {
    var list_string = '<option value=' + arr[i].phase_short_name + '>'  + arr[i].phase_name + '</option>';
    $("#phases_list").append(list_string);
    $("#add_phase_form").append('<input type="hidden" name="incident_short_name" value="' + incident_short_name + '" />');
  }
}

function save_changes(form_json_array) {
//   console.log(form_json_array);
  var jString = JSON.stringify(form_json_array);
  $.post( "incident_save_form", {form_json_array:jString}, function( data ) {
//     console.log(data);
    var d = JSON.parse(data)
    window.location.replace('/incident_definition?message="Saved Successfully"&id=' + d[0].incident_key.toString());
  });
}

function hide_sidebar_form_creator() {
  $("#sidebar_form_creator").hide();
  $("#phases").hide();
  $("#add_phase_button").hide();
  $("#edit_phase_button").hide();
}

function show_sidebar_form_creator() {
  $("#sidebar_form_creator").show();
  $("#phases").show();
  $("#add_phase_button").show();
  $("#edit_phase_button").show();
}

function show_form_controls() {
  $("#phases").show();
  $("#add_phase_button").show();
  $("#edit_phase_button").show();
}

function hide_phases_list() {
  $("#phases_list").hide();
}

function show_phases_list() {
  $("#phases_list").show();
}

function hide_phases_buttons() {
  $("#phases_buttons").hide();
}

function show_phases_buttons() {
  $("#phases_buttons").show();
}

function add_edit_buttons(order_number) {
 buttons_string = '<a href="#' + order_number + '" class="move_one_position_up" id="' + order_number + '">+</a>\
		   <a href="#' + order_number + '" class="move_one_position_down" id="' + order_number + '">-</a>\
		   <a href="#' + order_number + '" class="delete_by_position" id="' + order_number + '">X</a>';
 return buttons_string;
  return " ";
}

function move_one_position_up(order_number, form_json_array) {
  for (var i = 0; i < form_json_array.length; i++) {
   if (form_json_array[i].order_number == order_number) {
     form_json_array[i].order_number = form_json_array.order_number - 1
   }
  if (form_json_array[i].order_number == order_number - 1) {
     form_json_array[i].order_number = form_json_array.order_number + 1
   }
  }
  return form_json_array
}

function move_one_position_down(order_number, form_json_array) {
  for (var i = 0; i < form_json_array.length; i++) {
   if (form_json_array[i].order_number == order_number) {
     form_json_array[i].order_number = form_json_array.order_number + 1
   }
  if (form_json_array[i].order_number == order_number + 1) {
     form_json_array[i].order_number = form_json_array.order_number - 1
   }
  }
}

function delete_by_position(order_number, form_json_array) {
  for (var i = 0; i < form_json_array.length; i++) {
    if (form_json_array[i].order_number == order_number) {
      delete form_json_array[i];
    }
    
    if (form_json_array[i].order_number > order_number) {
      form_json_array[i].order_number = form_json_array[i].order_number - 1; 
    }
  }  
}

Array.prototype.swap = function (x,y) {
  var b = this[x];
  this[x] = this[y];
  this[y] = b;
  return this;
}

Array.prototype.move_up = function(order_number) {
    var tmp = this[order_number - 1];
    this[order_number - 1] = this[order_number];
    this[order_number] = tmp;  
}

Array.prototype.move_down = function(order_number) {
    var tmp = this[order_number + 1];
    this[order_number + 1] = this[order_number];
    this[order_number] = tmp;
}

function swap_order_numbers_down(order_number, form_json_array) {
  if (order_number < form_json_array.length - 1) {
    form_json_array[order_number].order_number = parseInt(order_number) + 1;
    form_json_array[parseInt(order_number) + 1].order_number = order_number;
    return true;
  }
  return false;
  
}

function swap_order_numbers_up(order_number, form_json_array) {
  if (order_number > 0) {
    form_json_array[order_number].order_number = order_number - 1;
    form_json_array[order_number - 1].order_number = order_number;
    return true;
  }
  return false;
}

function add_to_form(form_json_array) {
  console.log(form_json_array);
  read_json_to_html(form_json_array);
  var jString = JSON.stringify(form_json_array);
  $("#tabs-2").empty();
  $("#tabs-2").append(jString);   
}

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


var personal_info_module_string = '[{"order_number": 1, "header": "Personal and Property Information", "type": "header"}, {"sensitive": true, "type": "text", "required": true, "order_number": 2, "_id": "name", "label": "Name", "validations": "None"}, {"sensitive": false, "type": "text", "required": true, "order_number": 3, "_id": "request_date", "label": "Date of Request", "validations": "date"}, {"sensitive": true, "type": "text", "required": true, "order_number": 4, "_id": "address", "label": "Street Address", "validations": "None"}, {"sensitive": false, "type": "text", "required": true, "order_number": 5, "_id": "city", "label": "City", "validations": "None"}, {"sensitive": false, "type": "text", "required": false, "order_number": 6, "_id": "county", "label": "County", "validations": "None"}, {"sensitive": false, "type": "text", "required": true, "order_number": 7, "_id": "state", "label": "State", "validations": "None"}, {"sensitive": false, "type": "text", "required": true, "order_number": 8, "_id": "zip_code", "label": "Zip Code", "validations": "None"}, {"sensitive": true, "type": "text", "required": true, "order_number": 9, "_id": "latitude", "label": "Latitude", "validations": "None"}, {"sensitive": true, "type": "text", "required": true, "order_number": 10, "_id": "longitude", "label": "Longitude", "validations": "None"}, {"sensitive": false, "type": "text", "required": true, "order_number": 11, "_id": "cross_street", "label": "Cross Street or Nearby Landmark", "validations": "None"}, {"sensitive": true, "type": "text", "required": true, "order_number": 12, "_id": "phone1", "label": "Phone 1", "validations": "phone"}, {"sensitive": true, "type": "text", "required": false, "order_number": 13, "_id": "phone2", "label": "Phone 2", "validations": "phone"}, {"sensitive": false, "type": "text", "required": false, "order_number": 14, "_id": "time_to_call", "label": "Best time to call", "validations": "None"}, {"select_option_1": "Trees", "select_option_2": "Wind", "sensitive": false, "type": "select", "required": true, "order_number": 15, "_id": "work_type", "select_option_3": "Fire", "label": "Primary Help Needed"}, {"select_option_1": "Rent", "select_option_2": "Own", "sensitive": false, "type": "select", "select_option_5": "Business", "required": false, "order_number": 16, "_id": "rent_or_own", "select_option_3": "Public Land", "label": "Rent/Own/Public", "select_option_4": "Non-Profit"}, {"sensitive": false, "type": "checkbox", "_default": "n", "required": false, "order_number": 17, "_id": "work_without_resident", "label": "Work without resident present"}, {"sensitive": false, "type": "checkbox", "_default": "n", "required": false, "order_number": 18, "_id": "member_of_organization", "label": "Member of your organization"}, {"sensitive": false, "type": "checkbox", "_default": "n", "required": false, "order_number": 19, "_id": "first_responder", "label": "First Responder"}, {"sensitive": false, "type": "checkbox", "_default": "n", "required": false, "order_number": 20, "_id": "older_than_60", "label": "Older than 60"}, {"sensitive": false, "type": "checkbox", "_default": "n", "required": false, "order_number": 21, "_id": "disabled", "label": "Disabled"}, {"order_number": 22, "_id": "special_needs", "type": "textarea", "label": "Special Needs", "validations": "None"}, {"sensitive": false, "type": "radio", "low_hint": "Low (1)", "required": false, "order_number": 23, "_id": "priority", "label": "Priority", "radio_option_4": "4", "radio_option_5": "5", "high_hint": "High (5)", "radio_option_1": "1", "radio_option_2": "2", "radio_option_3": "3"}]';

var status_info_module_string = '[{"order_number": 1, "header": "Claim, Status and Report", "type": "header"}, {"order_number": 2, "_default": "n", "type": "checkbox", "required": false, "_id": "claim_for_org", "label": "Claim for my organization", "sensitive": false}, {"order_number": 3, "select_option_3": "Open, needs follow up", "type": "select", "select_option_4": "Closed, completed", "select_option_5": "Closed, incomplete", "select_option_6": "Closed, out of scope", "select_option_7": "Closed, done by others", "select_option_1": "Open, unassigned", "select_option_2": "Open, partially completed", "_id": "status", "label": "Current Status", "required": true, "select_option_8": "Closed, no help wanted", "select_option_9": "Closed, rejected", "select_option_10": "Closed, duplicate", "sensitive": false}, {"order_number": 4, "validations": "None", "type": "text", "required": false, "_id": "total_volunteers", "label": "Volunteers", "sensitive": false}, {"order_number": 5, "validations": "None", "type": "text", "required": false, "_id": "hours_worked_per_volunteer", "label": "Hours per volunteer", "sensitive": false}, {"order_number": 6, "validations": "None", "type": "text", "required": false, "_id": "initials_of_resident_present", "label": "Initials of resident present during work", "sensitive": false}, {"order_number": 7, "validations": "None", "type": "text", "required": false, "_id": "status note", "label": "Status Notes", "sensitive": false}]';

