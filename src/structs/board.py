import re
import requests
import structs.thread

BASE_URL = "https://a.4cdn.org"
VALID_FIELDS = {"all","sub","com"}

class Board:
    def __init__(self, board: str):
        self.board = None               #string      always              The directory the board is located in.                                         Any string
        self.title = None               #string      always              The readable title at the top of the board.                                    Any string
        self.ws_board = None            #integer     always              Is the board worksafe                                                          1 or 0
        self.per_page = None            #integer     always              How many threads are on a single index page                                    Any positive integer
        self.pages = None               #integer     always              How many index pages does the board have                                       Any positive integer
        self.max_filesize = None        #integer     always              Maximum file size allowed for non .webm attachments (in KB)                    Any positive integer
        self.max_webm_filesize = None   #integer     always              Maximum file size allowed for .webm attachments (in KB)                        Any positive integer
        self.max_comment_chars = None   #integer     always              Maximum number of characters allowed in a post comment                         Any positive integer
        self.max_webm_duration = None   #integer     always              Maximum duration of a .webm attachment (in seconds)                            Any positive integer
        self.bump_limit = None          #integer     always              Maximum number of replies allowed to a thread before the thread stops bumping  Any positive integer
        self.image_limit = None         #integer     always              Maximum number of image replies per thread before image replies are discarded  Any positive integer
        self.cooldowns = None           #array       always      
        self.meta_description = None    #integer     always              SEO meta description content for a board                                       Any string
        self.spoilers = None            #integer     only if enabled     Are spoilers enabled                                                           1 or 0
        self.custom_spoilers = None     #integer     only if enabled     How many custom spoilers does the board have                                   Any positive integer
        self.is_archived = None         #integer     only if enabled     Are archives enabled for the board                                             1 or 0
        self.board_flags = None         #array       only if enabled     Array of flag codes mapped to flag names    
        self.country_flags = None       #integer     only if enabled     Are flags showing the poster's country enabled on the board                    1 or 0
        self.user_ids = None            #integer     only if enabled     Are poster ID tags enabled on the board                                        1 or 0
        self.oekaki = None              #integer     only if enabled     Can users submit drawings via browser the Oekaki app                           1 or 0
        self.sjis_tags = None           #integer     only if enabled     Can users submit sjis drawings using the [sjis] tags                           1 or 0
        self.code_tags = None           #integer     only if enabled     Board supports code syntax highlighting using the [code] tags                  1 or 0
        self.math_tags = None           #integer     only if enabled     Board supports [math] TeX and [eqn] tags                                       1 or 0
        self.text_only = None           #integer     only if enabled     Is image posting disabled for the board                                        1 or 0
        self.forced_anon = None         #integer     only if enabled     Is the name field disabled on the board                                        1 or 0
        self.webm_audio = None          #integer     only if enabled     Are webms with audio allowed?                                                  1 or 0
        self.require_subject = None     #integer     only if enabled     Do OPs require a subject                                                       1 or 0
        self.min_image_width = None     #integer     only if enabled     What is the minimum image width (in pixels)                                    Any positive integer
        self.min_image_height = None    #integer     only if enabled     What is the minimum image height (in pixels)                                   Any positive integer

        boards = requests.get(f"{BASE_URL}/boards.json").json()["boards"]
        for b in boards:
            if b["board"] == board:
                self.__dict__.update(b)

        self.threads = []
        self.threads_old = []
        self.threads_new = []
        self.threads_bump_order = []
    
        self.watched_threads = []

        self.update()

    def get_threads(self):
        response = requests.get(f"{BASE_URL}/{self.board}/catalog.json").json()
        self.threads.clear()
        for page in response:
            for thread in page["threads"]:
                self.threads.append(structs.thread.Thread(thread, self.board, self.watched_threads))

        return self.threads

    def watch_thread(self, thread):
        if not isinstance(thread, structs.thread.Thread):
            raise TypeError(f"Object of type {type(thread)} supplied, expected thread {type(structs.thread.Thread)}")
        if thread.no in [x.no for x in self.watched_threads]:
            raise ValueError("Thread already in watched list")
        
        self.watched_threads.append(thread)

    def update(self):
        self.threads = self.get_threads()
        self.threads_bump_order = self.threads
        self.threads = sorted(self.threads, key=lambda x: x.no)                         #numerical order - creation date ascending
        self.threads_new = [item for item in self.threads if item not in self.threads_old]
        self.threads_old = self.threads

        return self.threads_new

    def update_watched(self):
        thread_dict = {}
        for thread in self.watched_threads:
            thread_dict[thread.no] = thread.update()
        
        return thread_dict
    
    def index(self, thread_no: int):
        for thread in self.threads:
            if thread.no == thread_no:
                return thread

    def search(self, term, field="all"):
        matches = []
        field = field.lower()
        if field not in VALID_FIELDS:
            raise ValueError(f"Fields must be one of {VALID_FIELDS}")
        
        if not self.threads:
            raise ValueError("Thread list empty, update before searching")

        if type(term) == list:
            term = "|".join(term)
        ex = re.compile(term, re.IGNORECASE)    

        if field == "all":
            for thread in self.threads:
                if (thread.sub != None and re.search(ex,thread.sub)) or (thread.com != None and re.search(ex,thread.com)):
                    matches.append(thread)
        else:
            for thread in self.threads:
                if getattr(thread,field) != None and re.search(ex, getattr(thread,field)):
                    matches.append(thread)
        
        return matches