import json

def populate_incident_form(form_json, phase_number, defaults=None, hidden_elements = {}):
  i = 0
  string = ""
  label = ""
  paragraph = ""
  defaults_json = None
  if defaults:
    try:
      defaults_json = json.loads(defaults)
    except:
      defaults_json = defaults

  if phase_number:
    phase_number = return_phase_number_int(phase_number)
  
  else:
    phase_number = 0

  if not check_if_form_exists(form_json, phase_number):
    string = "<h2>No Form Added</h2>"
    label = ""
    paragraph=""
    return string, label, paragraph

  # If form exists, continue

  for obj in form_json[phase_number]:
    i+=1
    
    ### If the object is holding the value of label, set the label.
    if "type" in obj and obj["type"] == "label":
      label = obj['label']
      
    ### If the object is a paragraph, set paragraph variable
    elif "type" in obj and obj["type"] == "paragraph":
      paragraph = obj["paragraph"]
      
    ### If the object is a header, send to get_header_html()
    elif "type" in obj and obj["type"] == "header":
      string = get_header_html(obj, string)
      
    ### If the object is a subheader, send to get_subheader_html()
    elif "type" in obj and obj["type"] == "subheader":
      string = get_subheader_html(obj, string)
      
    ### If the object is holding the phase_id, set the hidden phase_id value
    elif "phase_id" in obj:
      string = get_phase_html(obj, string)
      
    ### If the object is a text field, send to get_text_html() 
    elif "type" in obj and obj["type"] == "text":
      default_value = get_default_value(defaults_json, obj)
      string = get_text_html(obj, string, default_value)

    ### If the object is a textarea, send to get_textarea_html()
    elif "type" in obj and obj["type"] == "textarea":
      default_value = get_default_value(defaults_json, obj)
      string = get_textarea_html(obj, string, default_value)
    
    ### If the object is a checkbox, send to get_checkbox_html()
    elif "type" in obj and obj["type"] == "checkbox":
      default_value = get_default_value(defaults_json, obj)
      string = get_checkbox_html(obj, string, default_value)

    ### if the object is a select, send to get_select_html()
    elif "type" in obj and obj["type"] == "select":
      default_value = get_default_value(defaults_json, obj)
      string = get_select_html(obj, string, default_value)
      
    ### if the object is a radio, send to get_radio_html()
    elif "type" in obj and obj["type"] == "radio":
      default_value = get_default_value(defaults_json, obj)
      string = get_radio_html(obj, string, default_value)
  
  for key in hidden_elements:
    hidden_string = '<input type="hidden" name="' + str(key) + '" id="' + str(key) + ' value="' + str(hidden_elements[key]) + '">'  
    string += hidden_string
    
  return string, label, paragraph


def get_text_html(obj, string, default_value):
  required = ""
  suggestion = get_suggestion_div(obj["_id"])
  edit_string = force_click_edit(obj["_id"])
  readonly_string = set_readonly(obj["_id"])
  default_string = ""
  if default_value:
    default_string = ' value="' + str(default_value) + '"'
  if obj["required"] == True:
    required = "*"
  new_text_input = '<tr><td class=question>' +obj['label'] + str(edit_string) + ': <span class=required-asterisk>' + required + '</span></td><td class="answer"><div class="form_field"><input class="" id="' + obj['_id'] + '" name="' + obj['_id'] + '" type="text" ' + readonly_string + default_string + ' /></div>' + suggestion + '</td></tr>'
  string += new_text_input  
  return string
  
def get_phase_html(obj, string):
  string += '<input type="hidden" id="phase_id" name="phase_id" value="' + obj["phase_id"] + '">'
  return string

def get_header_html(obj, string):
  new_header = '<tr><td class="question"><h2>' + obj['header'] + '</h2></tr></td>'
  string += new_header
  return string

def get_subheader_html(obj, string):
  new_subheader = '<tr><td class="question"><h3>' + obj['subheader'] + '</h3></tr></td>' 
  string += new_subheader
  return string

def get_textarea_html(obj, string, default_value):
  if not default_value:
    default_value=""
    
  new_textarea = '<tr><td class=question>' + obj['label'] + ':</td><td class="answer"><div class="form_field"><textarea class="" id="' + obj['_id'] + '" name="' + obj['_id'] + '">' + default_value + '</textarea></div></td></tr>'
  string += new_textarea
  return string

def get_checkbox_html(obj, string, default_value):
  required = ""
  checked = ""
  if "required" in obj and obj["required"] == True:
    required = "*"
  if obj["_default"] == "y" or default_value == "y":
    checked = " checked"
  new_checkbox = '<tr><td class=question><label for="' + obj['_id'] + '">' + obj['label'] + required +'</label></td><td class="answer"><div class="form_field"><input class="" name="' + obj['_id'] + '" type="hidden" value="n"/><input class="" id="' + obj['_id'] + '" name="' + obj['_id'] + '" type="checkbox" value="y"' + checked + '></div></td></tr>'
  string += new_checkbox
  return string

def get_select_html(obj, string, default_value):
  options_array = []
  required = ""
  for key in obj:
    if "select_option_" in key:
      options_array.append(key)
  if obj["required"]:
    required = "*"
  begin_option = '<tr><td class=question>' + obj['label'] + required + '</td><td class="answer"><div class="form_field"><select class="" id="' + obj['_id'] + '" name="' + obj['_id'] + '">'
  end_option = '</select></div></td></tr>'
  select_string = '<option value="">Choose one</option>'

  options_array.sort()
  for option in options_array:
    selected = ""
    if obj[option] == default_value:
      selected = " selected"
    option_string = ""
    option_string = "<option" + selected + ">" + obj[option] + "</option>"
    select_string = select_string + option_string

  new_select = begin_option + select_string + end_option
  string += new_select
  return string

def get_radio_html(obj, string, default_value):
  options_array = []
  required = ""
  for key in obj:
    if "radio_option_" in key:
      options_array.append(key)
  if obj["required"]:
	  required = "*"
  radio_string = "";
  radio_string_start = '</td></tr><tr><td class=question>' + obj['label'] + required + '</td><td class="answer"><table><tr><td>' + obj["low_hint"] + '</td><td>'
  radio_string_end = '<td>' + obj['high_hint'] + '</td></tr></table></td></tr>'
  options_array.sort()
  for option in options_array:
    checked = ""
    if default_value == obj[option]:
      checked = ' checked="checked"'
      
    options_string = ""
    option_string = '<td><input id="' + obj['_id'] + '" name="' + obj['_id'] + '" type="radio" value="' + obj[option] + '"' + checked +'"></td>'
    radio_string = radio_string + option_string
  string = string + radio_string_start + radio_string + radio_string_end
  return string
  
def return_phase_number_int(phase_number):
  if phase_number:
    phase_number = int(str(phase_number))
  else:
    phase_number = 0
  return phase_number
    
def check_if_form_exists(form_json, phase_number):
  try:  
    form_json[phase_number]
    return True
  except:
    return False

def get_suggestion_div(id_string):
  suggestion_string = ""
  if id_string == "city" or id_string == "county" or id_string == "state":
    suggestion_string = '<div id=' + id_string + 'Suggestion></div></td></tr>'
  elif id_string == "zip_code":
    suggestion_string = '<div id=zipCodeSuggestion></div></td></tr>'

  return suggestion_string

def force_click_edit(id_string):
  edit_string = ""
  if id_string == "latitude":
    edit_string = """<small>(<a href="#" onclick="document.getElementById('latitude').readOnly=false; document.getElementById('latitude').focus(); return false;">edit</a>)</small>"""
  elif id_string == "longitude":
    edit_string = """<small>(<a href="#" onclick="document.getElementById('longitude').readOnly=false; document.getElementById('longitude').focus(); return false;">edit</a>)</small>"""
  return edit_string

def set_readonly(id_string):
  readonly_string = ""
  if id_string == "latitude" or id_string == "longitude":
    readonly_string = "readonly"
  return readonly_string

def get_default_value(defaults_json, obj):
  try:
    default_string = None
    if defaults_json:
      _id=obj["_id"]
      default_string = defaults_json[_id]
    return default_string
  except:
    pass