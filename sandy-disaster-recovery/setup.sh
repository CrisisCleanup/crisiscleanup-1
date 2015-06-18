virtualenv virtenv
source virtenv/bin/activate
pip install -r requirements.txt
green='\E[32;47m'

cecho ()                     # Color-echo.
                             # Argument $1 = message
                             # Argument $2 = color
{
local default_msg="No message passed."
                             # Doesn't really need to be a local variable.

message=${1:-$default_msg}   # Defaults to default message.
color=${2:-$black}           # Defaults to black, if not specified.

  echo -e "$color"
  echo "$message"
  #Reset    
  tput sgr0            # Reset to normal.

  return
}  

cecho "If you don't see any red text, then you're good to go." $green
