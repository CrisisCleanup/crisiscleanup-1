import random

first_word_list = ["above", "apple", "bright", "begin", "current", "cradle", "draft", "drape", "elephant", "early", "fiddle", "folder", "green", "giant", 
                               "harvest", "handle", "igloo", "island", "jones", "jeep", "king", "kite", "latest", "lemonade", "monday", "meeting", "noodle",
                               "needle", "opera", "opening", "prune", "pastel", "quote", "question", "reader", "rotate", "sunday", "species", "table", "twelve",
                               "under", "umbrella", "valid", "voice", "slide", "bottle", "grandpa", "television", "poster", "cloud"]

second_word_list = ["again", "another", "boat", "bold", "current", "cradle", "draft", "drape", "elephant", "early", "fiddle", "folder", "green", "giant", 
                               "harvest", "handle", "igloo", "island", "jones", "jeep", "king", "kite", "latest", "lemonade", "monday", "meeting", "noodle",
                               "needle", "opera", "opening", "prune", "pastel", "quote", "question", "reader", "rotate", "sunday", "species", "table", "twelve",
                               "under", "umbrella", "valid", "voice", "slide", "bottle", "grandpa", "television", "poster", "cloud"]
                               
def generate_password():
    return first_word_list[random.randrange(0,50)] +  second_word_list[random.randrange(0,50)] + str(random.randrange(100,999))
    