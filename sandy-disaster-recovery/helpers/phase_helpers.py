def get_phase_name(form_json, phase_number):
  phase_number = int(phase_number)
  i = 0
  phase_name = ""
  for obj in form_json:
    if phase_number == i:
      for data in obj:
	if 'phase_name' in data:
	  phase_name = data["phase_name"]
    i += 1
  return phase_name


def get_phase_number(form_json, phase_id):
  i = 0
  string = ""
  label = ""
  paragraph = ""
  phase_number = 0
  i = 0
  for obj in form_json:
    for o in obj:
      if "phase_id" in o and o['phase_id'] == phase_id:
	phase_number = i
    i+=1
    
  return phase_number


def populate_phase_links(phases_json, this_phase = None):
  if this_phase == None:
    this_phase == "0"
  links = "<h3>Phases</h3>"
  i = 0
  for phase in phases_json:
    num = str(i).replace('"', '')
    separator = ""
    if i > 0:
      separator = " | "
    if str(i) == this_phase:
      links = links + separator + '<a style="font-weight:bold; font-size:150%" href="/?phase_number=' + str(i) + '">' + phase['phase_name'] + '</a>'
    else:
      links = links + separator + '<a href="/?phase_number=' + str(i) + '">' + phase['phase_name'] + '</a>'

    i+=1
    
  return links


def get_phase_id(form_json, phase_number):
  phase_number = int(phase_number)
  i = 0
  phase_id = ""
  for obj in form_json:
    if phase_number == i:
      for data in obj:
	if 'phase_id' in data:
	  phase_id = data["phase_id"]
    i += 1
  return phase_id
    