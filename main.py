import os
import re
import json
import html
import requests

from dotenv import load_dotenv
load_dotenv()

BASE_URL = 'https://a.4cdn.org/'
"""
Loads values in from a .env file in the same directory.
Maintaining the python format for lists in the .env file
necessitates the use of json.load to properly import them
as lists. Might be worth changing the .env and using built
in split methods as opposed to importing another library.
"""
BOARDS = json.loads(os.getenv('BOARDS'))
SUBS = json.loads(os.getenv('SUBS'))
TERMS = json.loads(os.getenv('TERMS'))

#ANSI escape codes to make terminal print more readable
GREEN = "\u001b[32;1m"
CYAN = "\u001b[36;1m"
MAGENTA = "\u001b[35;1m"
RESET = "\u001b[0m"

def main():
    for board in BOARDS:                                                                                        #Iterates through user set list of boards
        r = requests.get("{}/{}/catalog.json".format(BASE_URL, board))                                          #Gets all of a board OP posts split into pages
        for page in r.json():
            for thread in page["threads"]:
                for sub in SUBS:
                    if "sub" in thread.keys() and sub in thread["sub"]:                                         #Checks for search terms in OP subject
                        print("{}/{}{}:".format(board,thread["no"],thread["sub"]))
                        Thread(board, thread["no"])

def Thread(board, thread_no):
    seen_posts = []
    r = requests.get("{}{}/thread/{}.json".format(BASE_URL, board, thread_no))                                  #Gets thread / json of all the replies in a thread
    for post in r.json()["posts"]:
        try:
            matched_terms = re.findall(r'|'.join(TERMS), post["com"], re.IGNORECASE)
            if matched_terms and post["no"] != thread_no:
                print(post["no"], matched_terms)
                print(Comment(post["com"], matched_terms))
                print("")
        except KeyError:
            pass
        except Exception as e:
            print(e)
    return

def Comment(comment, matched_terms):
    comment = re.sub(r'<br>+', '\n', comment)                                                                   #Replace br tags with newlines to maintain original readability
    comment = html.unescape(re.sub(r'<.*?>', '', comment))                                                      #Unescapes escaped special characters and removes HTML tags
    comment = re.sub(r'>{1}[\S ]*', r"{}\g<0>{}".format(GREEN, RESET), comment)                                 #Matches greentext and colours it green                                                    
    comment = re.sub(r'>>[\d]{8}', r"{}\g<0>{}".format(CYAN, RESET), comment)                                   #Matches reply and colours it cyan
    comment = re.sub(r'|'.join(matched_terms), r"{}\g<0>{}".format(MAGENTA, RESET), comment)                    #Matches found term and colours it magenta
    return comment

if __name__ == "__main__":
    main()