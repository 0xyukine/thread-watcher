import os
import re
import sys
import json
import html
import structs
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

DEFAULT_PATH = "/mnt/e/Stuff/"

#ANSI escape codes to make terminal print more readable
GREEN = "\u001b[32;1m"
CYAN = "\u001b[36;1m"
MAGENTA = "\u001b[35;1m"
RESET = "\u001b[0m"

def main():
    if len(sys.argv) > 1:
        print(sys.argv)
        if sys.argv[1] == "rip":
            if re.match(r'https://boards\.4chan\.org/\w/thread/\d{7,8}',sys.argv[2]) or re.match(r'https://boards\.4channel\.org/\w/thread/\d{7,8}',sys.argv[2]):
                thread = re.search(r'\w/thread/\d{7,8}',sys.argv[2])
                thread = thread.group(0)
                print(thread)
                r = requests.get(BASE_URL + thread + ".json")

                try:
                    out_folder = sys.argv[3]
                except:
                    out_folder = "4chan_download/"

                filepath = DEFAULT_PATH + out_folder
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                for post in r.json()["posts"]:
                    if "tim" in post.keys():
                        img = requests.get("https://i.4cdn.org/{}/{}{}".format(thread[0],post["tim"],post["ext"])).content
                        with open(filepath + str(post["tim"]) + post["ext"], 'wb') as handler:
                            handler.write(img)
            else:
                print("Invalid URL supplied")
        else:
            print("Invalid argument supplied")
    else:
        for board in BOARDS:                                                                                        #Iterates through user set list of boards
            r = requests.get("{}/{}/catalog.json".format(BASE_URL, board))                                          #Gets all of a board OP posts split into pages
            for page in r.json():
                for thread in page["threads"]:
                    for sub in SUBS:
                        if "sub" in thread.keys() and sub in thread["sub"]:                                         #Checks for search terms in OP subject
                            print("{}/{}{}:".format(board,thread["no"],thread["sub"]))
                            Thread(board, thread["no"])

def Thread(board, thread_no):
    """
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
    """
    r = requests.get("{}{}/thread/{}.json".format(BASE_URL, board, thread_no))
    for post in r.json()["posts"]:
        a = structs.Post(post)

        print(a.no)
        a.print()
        input()

def Comment(comment, matched_terms):
    comment = re.sub(r'<br>+', '\n', comment)                                                                   #Replace br tags with newlines to maintain original readability
    comment = html.unescape(re.sub(r'<.*?>', '', comment))                                                      #Unescapes escaped special characters and removes HTML tags
    comment = re.sub(r'>{1}[\S ]*', r"{}\g<0>{}".format(GREEN, RESET), comment)                                 #Matches greentext and colours it green                                                    
    comment = re.sub(r'>>[\d]{8}', r"{}\g<0>{}".format(CYAN, RESET), comment)                                   #Matches reply and colours it cyan
    comment = re.sub(r'|'.join(matched_terms), r"{}\g<0>{}".format(MAGENTA, RESET), comment)                    #Matches found term and colours it magenta
    return comment

if __name__ == "__main__":
    main()