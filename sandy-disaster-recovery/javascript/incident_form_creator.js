var warn_on_leave = false;
var first_run = true;
// window.onbeforeunload = function(){
//   if(warn_on_leave){
//       return 'Your changes have not been saved. To save, stay on this page and click "save".';
//   }
// };
$(function() {


  hide_divs();
  hide_tabs();
  hide_sidebar_form_creator();
  hide_phases_list();
  
    
  var select_options_array = [];
  var radio_options_array = [];
  var form_json_array = [];
  var phases_json_array = [];
  
  

  $("#save_all_changes").click(function() {
    save_changes(form_json_array);
  
  });
  $("#tabs-1").show();
  $( "#incident" ).change(function() {
    show_phases_list();

    var incident_full_name = $("#incident").val();
    get_json(incident_full_name, phases_json_array);
  });
  
  $( "#phases_list" ).change(function() {
    var phase = $("#phases_list").val();
    var incident_full_name = $("#incident").val();
//       $("#tabs-1").empty();
//       $("#tabs-2").empty();
    get_form_json(phase, incident_full_name, form_json_array);
  });
  
  $( "#add_phase_button" ).click(function() {
    $("#add_phase_form_div").show();
  });
  
  $("#edit_phase_button").click(function() {
    window.location.replace('/incident_edit_phase?incident=' + phases_json_array[0][0].incident_short_name);
  });
  $( "#close_phase_button" ).click(function() {
    $("#add_phase_form_div").hide();
  });
  
  $("#show_html").click(function() {
    hide_tabs();
    $("#tabs-1").show();
  });
  
  $("#show_json").click(function() {

    hide_tabs();
    $("#tabs-2").show();
  });

  var option_html = 'Option:  <input type="text" name="firstname"><br>';
  

  $( "#add_select_option" ).click(function() {
  
    add_select_option(select_options_array);
    var i = select_options_array.length - 1;
    var option_number = i + 2;
    var new_line = 'Option ' + option_number + ':  <input type="text" id="'+ select_options_array[i] + '" name="'+ select_options_array[i] + '"><br>';
    var new_option = '<option value="' + select_options_array[i] + '">Option '+ option_number + '</option>';
    $("#add_options_to_select").append(new_line);
    $("#select_default").append(new_option);
    // add to select options select default div
    // make a remove option(remove only removes last)
  });
  
  $("#clear_radio_options").click(function() {
    radio_options_array = [];
    var new_option = 'Option 1:  <input type="text" id="radio_option_1" name="radio_option_1"><br>';
    var new_select = '<option value="radio_option_1">Option 1</option>';
    $("#add_options_to_radio").empty();
    $("#radio_default").empty();
    $("#add_options_to_radio").append(new_option);
    $("#radio_default").append(new_select);
  // clear and reset text input
  // clear and reset default select
  
  });

  $("#clear_select_options").click(function() {
    select_options_array = [];
    var new_option = 'Option 1:  <input type="text" id="select_option_1" name="select_option_1"><br>';
    var new_select = '<option value="select_option_1">Option 1</option>';
    $("#add_options_to_select").empty();
    $("#select_default").empty();
    $("#add_options_to_select").append(new_option);
    $("#select_default").append(new_select);
  // clear and reset text input
  // clear and reset default select
  
  });
  
  
  $( "#add_radio_option" ).click(function() {
  
    add_radio_option(radio_options_array);
    var i = radio_options_array.length - 1;
    var option_number = i + 2;
    var new_line = 'Option ' + option_number + ':  <input type="text" id="'+ radio_options_array[i] + '" name="'+ radio_options_array[i] + '"><br>';
    var new_option = '<option value="' + radio_options_array[i] + '">Option '+ option_number + '</option>';
    $("#add_options_to_radio").append(new_line);
    $("#radio_default").append(new_option);
    // add to select options select default div
    // make a remove option(remove only removes last)
  });

//------------------------------------------------------------------------------------------------------------------
//    Show form Divs
  $( "#add_checkbox" ).click(function() {
	hide_divs();
	$("#checkbox_div").show();
  });
  
  $( "#add_select" ).click(function() {
	hide_divs();
	$("#select_div").show();
  });
  $( "#add_radio" ).click(function() {
	hide_divs();
	$("#radio_div").show();
  });
  $( "#add_text" ).click(function() {
	hide_divs();
	$("#text_div").show();
  });
  $( "#add_header" ).click(function() {
	hide_divs();
	$("#header_div").show();
  });
  $( "#add_subheader" ).click(function() {
	hide_divs();
	$("#subheader_div").show();
  });
  $("#add_label").click(function() {
	hide_divs();
	$("#label_div").show();
  });
  
  $("#add_paragraph").click(function() {
	hide_divs();
	$("#paragraph_div").show();
  });
  
  $("#add_textarea").click(function() {
      hide_divs();
      $("#textarea_div").show();
  });
  
//------------------------------------------------------------------------------------------------------------------
// add info from form divs to json
  
  $("#add_paragraph_to_form").click(function() {
	hide_divs();
	add_paragraph_input(form_json_array);
	read_json_to_html(form_json_array);
	$("#paragraph_form").trigger('reset');
	var jString = JSON.stringify(form_json_array);
	$("#tabs-2").empty();
	$("#tabs-2").append(jString);
  
  });
  
  $("#add_label_to_form").click(function() {
	hide_divs();
	add_label_input(form_json_array);
	read_json_to_html(form_json_array);
	$("#label_form").trigger('reset');
	var jString = JSON.stringify(form_json_array);
	$("#tabs-2").empty();
	$("#tabs-2").append(jString);
  
  });
  
  $( "#add_header_to_form" ).click(function() {
	hide_divs();
	add_header_input(form_json_array);
	read_json_to_html(form_json_array);
	$("#header_form").trigger('reset');
	var jString = JSON.stringify(form_json_array);
	$("#tabs-2").empty();
	$("#tabs-2").append(jString);
  });
  
  
    $( "#add_textarea_to_form" ).click(function() {
	hide_divs();
	add_textarea_input(form_json_array);
	read_json_to_html(form_json_array);
	$("#textarea_form").trigger('reset');
	var jString = JSON.stringify(form_json_array);
	$("#tabs-2").empty();
	$("#tabs-2").append(jString);
  });
    
  $( "#add_subheader_to_form" ).click(function() {
	hide_divs();
	add_subheader_input(form_json_array);
	read_json_to_html(form_json_array);
	$("#subheader_form").trigger('reset');
	var jString = JSON.stringify(form_json_array);
	$("#tabs-2").empty();
	$("#tabs-2").append(jString);
  });
  
  $( "#add_text_to_form" ).click(function() {
      hide_divs();
      add_text_input(form_json_array);
      $("#tabs-2").empty();
      $("#text_form").trigger('reset');
      


      var jString = JSON.stringify(form_json_array);
      $("#tabs-2").empty();
      $("#tabs-2").append(jString);
      read_json_to_html(form_json_array);
  });
  $( "#add_checkbox_to_form" ).click(function() {
      hide_divs();
      add_checkbox_input(form_json_array);
      $("#tabs-2").empty();
      $("#checkbox_form").trigger('reset');

      var jString = JSON.stringify(form_json_array);
      $("#tabs-2").empty();
      $("#tabs-2").append(jString);
      read_json_to_html(form_json_array);
  });  
  $( "#add_select_to_form" ).click(function() {
    hide_divs();
    add_select_input(form_json_array, select_options_array);
    $("#tabs-2").empty();
    $("#select_form").trigger('reset');
    clear_select_options(select_options_array);
    // only below clears array
    select_options_array = [];
    read_json_to_html(form_json_array);

    var jString = JSON.stringify(form_json_array);
    $("#tabs-2").empty();
    $("#tabs-2").append(jString);
  }); 

    $( "#add_radio_to_form" ).click(function() {
	hide_divs();
	add_radio_input(form_json_array, radio_options_array);
	// only below clears array
	radio_options_array = [];
	$("#tabs-2").empty();
	$("#select_form").trigger('reset');
	clear_radio_options();

	var jString = JSON.stringify(form_json_array);
	$("#tabs-2").empty();
	$("#tabs-2").append(jString);
	read_json_to_html(form_json_array);

  });      
  
  $("#form_table").on( "click", ".move_one_position_up",  function() {
    order_number = $(this).attr("id");
    form_json_array = move_one_position_up(parseInt(order_number));
    
    var jString = JSON.stringify(form_json_array);
    $("#tabs-2").empty();
    $("#tabs-2").append(jString);
    read_json_to_html(form_json_array);
  });
  

});

//------------------------------------------------------------------------------------------------------------------
// helper functions
function hide_divs() {
  $("#first_phase_form_div").hide();
  $("#add_phase_form_div").hide();
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


//------------------------------------------------------------------------------------------------------------------
// add options to select
function add_select_option(select_options_array) {
   var array_length = select_options_array.length;
   var new_length = array_length + 2;
   var new_options_string = "select_option_" + new_length;
   select_options_array.push(new_options_string);
   return select_options_array;
}

//------------------------------------------------------------------------------------------------------------------
// add options to radio

function add_radio_option(select_options_array) {
   var array_length = select_options_array.length;
   var new_length = array_length + 2;
   var new_options_string = "radio_option_" + new_length;
   select_options_array.push(new_options_string);
   return select_options_array;
}

function remove_option(options_array) {
   options_array.pop();
   return options_array;
}

//------------------------------------------------------------------------------------------------------------------
// add get forms, add to json
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


function add_textarea_input(form_json_array) {
  var textarea_label = $("#textarea_label").val();
  var textarea_id = $("#textarea_id").val();
  order_number = form_json_array.length;

  var header_json = {
    "type": "textarea",
    "textarea_label": textarea_label,
    "textarea_id": textarea_id,
    "order_number": order_number,
  }
  form_json_array.push(header_json);
  
}


function add_text_input(form_json_array) {
  var text_label = $("#text_label").val();
  var text_default = $("#text_default").val();
  var text_placeholder = $("#text_placeholder").val();
  var text_required = $('#text_required').prop('checked')
  var text_sensitive = $('#text_sensitive').prop('checked')
  var text_id = $("#text_id").val();
  
  var text_infobox = $("#text_infobox").val();
  var text_printer = $("#text_printer").val();
  var text_mobile = $("#text_mobile").val();
  var text_sms = $("#text_sms").val();
  
  order_number = form_json_array.length;

    
  var text_json = {
    type: "text",
    text_label: text_label,
    text_default: text_default,
    text_placeholder: text_placeholder,
    text_required: text_required,
    text_sensitive: text_sensitive,
    text_id: text_id,
    text_infobox: text_infobox,
    text_printer: text_printer,
    text_mobile: text_mobile,
    text_sms: text_sms,
    order_number: order_number,

  }
  
  form_json_array.push(text_json);
}

function add_checkbox_input(form_json_array) {
  var checkbox_label = $("#checkbox_label").val();
  var checkbox_default = $("#checkbox_default").val();
  var checkbox_required = $("#checkbox_required").prop('checked');
  var checkbox_sensitive = $("#checkbox_sensitive").prop("checked");
  var checkbox_id = $("#checkbox_id").val();
  var checkbox_checked_value = $("#checkbox_checked_value").val();
  var checkbox_unchecked_value = $("#checkbox_unchecked_value").val();
  var checkbox_infobox = $("#checkbox_infobox").val();
  var checkbox_printer = $("#checkbox_printer").val();
  var checkbox_mobile = $("#checkbox_mobile").val();
  var checkbox_sms = $("#checkbox_sms").val();
  
  order_number = form_json_array.length;
  
  var checkbox_json = {
    type: "checkbox",
    checkbox_label: checkbox_label,
    checkbox_default: checkbox_default,
    checkbox_required: checkbox_required,
    checkbox_sensitive: checkbox_sensitive,
    checkbox_id: checkbox_id,
    checkbox_checked_value: "y",
    checkbox_unchecked_value: "n",
    checkbox_infobox: checkbox_infobox,
    checkbox_printer: checkbox_printer,
    checkbox_mobile: checkbox_mobile,
    checkbox_sms: checkbox_sms,
    order_number: order_number,
  }
  
  form_json_array.push(checkbox_json);
}

function add_select_input(form_json_array, select_options_array) {
  var select_label = $("#select_label").val();
  var select_option_1 = $("#select_option_1").val();
  var select_default = $("#select_default").val();
  var select_required = $("#select_required").prop('checked');
  var select_sensitive = $("#select_sensitive").prop("checked");
  var select_id = $("#select_id").val();
  var select_infobox = $("#select_infobox").val();
  var select_printer = $("#select_printer").val();
  var select_mobile = $("#select_mobile").val();
  var select_sms = $("#select_sms").val();
  var order_number = form_json_array.length;
       
  var select_json = {
    type: "select",
    select_label: select_label,
    select_option_1: select_option_1,
    select_default: select_default,
    select_required: select_required,
    select_sensitive: select_sensitive,
    select_id: select_id,
    select_infobox: select_infobox,
    select_printer: select_printer,
    select_mobile: select_mobile,
    select_sms: select_sms,
    order_number: order_number,
  }
  
  for (var i = 0; i < select_options_array.length; i++) {
    var element = '#' + select_options_array[i];
    select_json[select_options_array[i]] = $('#' + select_options_array[i] +'').val();
  }
    
  form_json_array.push(select_json);
  select_options_array = [];
}

function add_radio_input(form_json_array, radio_options_array) {
  var radio_label = $("#radio_label").val();
  var radio_option_1 = $("#radio_option_1").val();
  var radio_default = $("#radio_default").val();
  var radio_required = $("#radio_required").prop('checked');
  var radio_sensitive = $("#radio_sensitive").prop("checked");
  var radio_id = $("#radio_id").val();
  var radio_low_hint = $("#radio_low_hint").val();
  var radio_high_hint = $("#radio_high_hint").val();
  var radio_infobox = $("#radio_infobox").val();
  var radio_printer = $("#radio_printer").val();
  var radio_mobile = $("#radio_mobile").val();
  var radio_sms = $("#radio_sms").val();
  var order_number = form_json_array.length
    
  var radio_json = {
    type: "radio",
    radio_label: radio_label,
    radio_option_1: radio_option_1,
    radio_default: radio_default,
    radio_required: radio_required,
    radio_sensitive: radio_sensitive,
    radio_id: radio_id,
    radio_low_hint: radio_low_hint,
    radio_high_hint: radio_high_hint,
    radio_infobox: radio_infobox,
    radio_printer: radio_printer,
    radio_mobile: radio_mobile,
    radio_sms: radio_sms,
    order_number: order_number,
  }
  
  for (var i = 0; i < radio_options_array.length; i++) {
    var element = '#' + radio_options_array[i];
    radio_json[radio_options_array[i]] = $('#' + radio_options_array[i] +'').val();
  }
    
  
  form_json_array.push(radio_json);

}

//------------------------------------------------------------------------------------------------------------------
// read from incremented json to the html div. This gives users a chance to see what the div will look like.

function read_json_to_html(form_json_array) {
  //TODO
  //console.log("read_json_to_html");
  form_json_array.sort(function (a, b) {
    return a.order_number > b.order_number;
  });
  if (first_run) {
    first_run = false;
  } else {
    warn_on_leave = true;
  }
  
  //console.log("continue");
  $("#form_label").empty();
  $("#form_paragraph").empty();
  $("#form_table").empty();
  

  for (var i=0; i < form_json_array.length; i++) {
    if(form_json_array[i].type == "label") {
    buttons_string = add_edit_buttons(form_json_array[i].order_number);

    //console.log("label");
    
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
      if (form_json_array[i].radio_required) {
        req = "*";
      }
      var radio_string = "";
      var radio_string_start = '</td></tr><tr><td class=question>' + buttons_string  + form_json_array[i].radio_label + req + '</td><td class="answer"><table><tr><td>' + form_json_array[i].radio_low_hint + '</td><td>';
      var radio_string_end = '<td>' + form_json_array[i].radio_high_hint + '</td></tr></table></td></tr>';
      for (var j = 0; j < options_array.length; j++) {
        var options_string = "";
	if(form_json_array[i].radio_default == options_array[j]) {
          var option_string = '<td><input id="' + form_json_array[i][options_array[j]] + '" name="' + form_json_array[i].radio_label + '" type="radio" value="' + form_json_array[i][options_array[j]] + '" checked="true"></td>';
	} else {
	  var option_string = '<td><input id="' + form_json_array[i][options_array[j]] + '" name="' + form_json_array[i].radio_label + '" type="radio" value="' + form_json_array[i][options_array[j]] + '"></td>';
	}

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
      if (form_json_array[i].select_required) {
        req = "*";
      }
      var begin_option = '<tr><td class=question>' + buttons_string + form_json_array[i].select_label + req +'</td><td class="answer"><div class="form_field"><select class="" id="' + form_json_array[i].select_id + '" name="' + form_json_array[i].select_id + '">';
      var end_option = '</select></div></td></tr>';
      var select_string = "";

      for (var j = 0; j < options_array.length; j++) {
        var option_string = "";
        if(form_json_array[i].select_default == options_array[j]) {
	  var option_string = "<option selected>" + form_json_array[i][options_array[j]] + "</option>";
	  select_string = select_string + option_string;
        } else {
	  var option_string = "<option>" + form_json_array[i][options_array[j]] + "</option>";
	  select_string = select_string + option_string;
	}
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

      var new_textarea = '<tr><td class=question>'+ buttons_string + form_json_array[i].textarea_label + ':</td><td class="answer">\
      <div class="form_field"><textarea class="" id="' + form_json_array[i].textarea_id + '" name="' + form_json_array[i].textarea_id + '"></textarea></div>\
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
      if (form_json_array[i].text_required) {
        var required = "*";
      }
      var new_text_input = '<tr><td class=question>' + buttons_string + form_json_array[i].text_label + ': <span class=required-asterisk>' + required + '</span></td><td class="answer"><div class="form_field"><input class="" id="' + form_json_array[i].text_id + '" name="' + form_json_array[i].text_id + '" type="text" value="' + form_json_array[i].text_default + '" placeholder="' + form_json_array[i].text_placeholder + '"/></div></td></tr>'
      $("#form_table").append(new_text_input);
    }
    
    else if (form_json_array[i].type == "checkbox") {
      buttons_string = add_edit_buttons(form_json_array[i].order_number);
      var required = "";
      var checked = "";
      if (form_json_array[i].checkbox_required == true) {
        required = "*";
      }
      
      if (form_json_array[i].checkbox_default == "y") {
        checked = " checked";
      }
      var new_checkbox = '<tr><td class=question><label for="' + form_json_array[i].checkbox_id + '">' + buttons_string + form_json_array[i].checkbox_label + required +'</label></td><td class="answer"><div class="form_field"><input class="" name="' + form_json_array[i].checkbox_id + '" type="hidden" value="' +form_json_array[i].checkbox_unchecked_value + '"/><input class="" id="' + form_json_array[i].checkbox_id + '" name="' + form_json_array[i].checkbox_id + '" type="checkbox" value="' +form_json_array[i].checkbox_checked_value + '"' + checked + '></div></td></tr>';
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
  $("#select_default").empty();
  $("#add_options_to_select").append(new_option);
  $("#select_default").append(new_select);
}

//------------------------------------------------------------------------------------------------------------------
// clear options for radio form

function clear_radio_options() {

  radio_options_array = [];
  var new_option = 'Option 1:  <input type="text" id="radio_option_1" name="radio_option_1"><br>';
  var new_select = '<option value="radio_option_1">Option 1</option>';
  $("#add_options_to_radio").empty();
  $("#radio_default").empty();
  $("#add_options_to_radio").append(new_option);
  $("#radio_default").append(new_select);
  
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
    //console.log("empty tabs-1");
//       $("#tabs-1").empty();

      $("#form_label").append("<h2>Create a form by using the controls on the left</h2>");

//       $("#tabs-2").append(data.forms_json);
      var phases_array = JSON.parse(data.phases_json);

      //console.log(phases_array[0].phase_id);
      var phase_data = {
	"phase_id": phases_array[0].phase_id,
	"phase_name": phases_array[0].phase_name,
	"incident_short_name": incident_short_name,
	"phase_short_name": phases_array[0].phase_short_name,
	
      }
      form_json_array.push(phase_data);
      var jString = JSON.stringify(form_json_array);

      $("#tabs-2").append(jString);

//       form_json_array.push(data.phases_json[0].phase_id);
//       //console.log(form_json_array);
//       //console.log(form_json_array.push(data.phases_json[0].phase_id));
//       $("#tabs-2").append(form_json_array);
//       show_first_phase_form(incident_short_name, incident_short_name);
    } else {
//     hide_sidebar_form_creator();
    $("#form_label").append('<h2><a href="/incident_edit_form">Edit Form</a></h2>');

    
    var arr = JSON.parse(data.forms_json);
    //console.log(arr.length);
    var any_equal = false;
    for (var k = 0; k < arr.length; k++) {
        //console.log(k);
//         alert(arr[k]);
      for (var j = 0; j < arr[k].length; j ++) {
        
//         //console.log(j);
        //console.log(arr[k][j]);
	//console.log(arr[k][j]['phase_short_name'] + '=:');
	//console.log(phase.toString() + '=:=');
	if (arr[k][j]['phase_short_name'] == phase) {
	  //console.log("eq");
	  any_equal = true;
  // 	form_json_array.push(arr[0]);
	  form_json_array = arr[k];
	  var jString = JSON.stringify(form_json_array);
	  $("#tabs-2").empty();
	  $("#tabs-2").append(jString);

// 	  alert(jString);
	  read_json_to_html(form_json_array);
// 	      hide_sidebar_form_creator();
    $("#form_label").append('<h2><a href="/incident_edit_form">Edit Form</a></h2>');

	}
      }
    }
    
    if (!any_equal) {
        show_sidebar_form_creator();

      $("#form_label").append("<h2>Create a form by using the controls on the left</h2>");
//       $("#tabs-2").append(data.forms_json);
      var phases_array = JSON.parse(data.phases_json);
      
      for (var n = 0; n < phases_array.length; n++) {
	if (phase == phases_array[n].phase_short_name) {
	  //console.log(phases_array[n].phase_short_name);
	  var phase_data = {
	    "phase_id": phases_array[n].phase_id,
	    "phase_name": phases_array[n].phase_name,
	    "incident_short_name": incident_short_name,
	    "phase_short_name": phases_array[n].phase_short_name,
	    
	  }
	  form_json_array.push(phase_data);
	  var jString = JSON.stringify(form_json_array);

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

  $("#first_phase_form_div").show();
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
  form_json_array.sort(function (a, b) {
    return a.order_number > b.order_number;
  });
  var jString = JSON.stringify(form_json_array);
  //console.log(jString);

  $.post( "incident_save_form", {form_json_array:jString}, function( data ) {
    //console.log(data);
    window.location.replace('/incident_form_creator?message="Successfully saved form"')

  });

}

function hide_sidebar_form_creator() {
  console.log("hide_sidebar_form_creator");
  $("#sidebar_form_creator").hide();
  $("#phases").hide();
  $("#add_phase_button").hide();
  $("#edit_phase_button").hide();

}

function show_sidebar_form_creator() {
  console.log("show_sidebar_form_creator");
  $("#sidebar_form_creator").show();
  $("#phases").show();
  $("#add_phase_button").show();
  $("#edit_phase_button").show();

}

function show_form_controls() {
  console.log("show_form_controls");
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

function add_edit_buttons(order_number) {
//  buttons_string = '<a href="#' + order_number + '" class="move_one_position_up" id="' + order_number + '">+</a>\
// 		   <a href="#' + order_number + '" class="move_one_position_down" id="' + order_number + '">-</a>\
// 		   <a href="#' + order_number + '" class="delete_by_position" id="' + order_number + '">X</a>';
//  return buttons_string;
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
