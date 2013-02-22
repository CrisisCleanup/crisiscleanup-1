import random
word_list = ["above", "apple", "bright", "begin", "current", "cradle", "draft", "drape", "elephant", "early", "fiddle", "folder", "green", "giant", 
                               "harvest", "handle", "igloo", "island", "jones", "jeep", "king", "kite", "latest", "lemonade", "monday", "meeting", "noodle",
                               "needle", "opera", "opening", "prune", "pastel", "quote", "question", "reader", "ready", "sunday", "species", "table", "twelve",
                               "under", "umbrella", "valid", "voice", "slide", "bottle", "grandpa", "television", "poster", "cloud", "again", "another", "boat", "bold", "coast", "candle", "door", "detail", "entry", "flower", "flow", "fleece", "grade", "degrees", 
                               "hold", "heel", "moon", "ocean", "lake", "river", "mountain", "hill", "orange", "flute", "glass", "paper",
                               "pine", "valley", "closet", "clock", "walk", "whisper", "water", "cafe", "coffee", "statue", "college", "thread", "toast",
                               "bottle", "barge", "stone", "cardboard", "pail", "chain", "grain", "select", "notebook", "pencil"]
                               
def generate_password():
    first_random = random.randint(0,49)
    second_random = random.randint(50,99)
    return word_list[first_random] +  word_list[second_random] + str(random.randint(100,999))
    