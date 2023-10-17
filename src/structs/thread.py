class Thread:
    def __init__(self, json):
        self.no = None              #integer     always                                              The numeric post ID                                                                     any positive integer
        self.resto = None           #integer     always                                              For replies: this is the ID of the thread being replied to. For OP: this value is zero  0 or Any positive integer
        self.sticky = None          #integer     OP only, if thread is currently stickied            If the thread is being pinned to the top of the page                                    1 or not set
        self.closed = None          #integer     OP only, if thread is currently closed              If the thread is closed to replies                                                      1 or not set
        self.now = None             #string      always                                              MM/DD/YY(Day)HH:MM (:SS on some boards), EST/EDT timezone                               string
        self.time = None            #integer     always                                              UNIX timestamp the post was created                                                     UNIX timestamp
        self.name = None            #string      always                                              Name user posted with. Defaults to Anonymous                                            any string
        self.trip = None            #string      if post has tripcode                                The user's tripcode, in format: !tripcode or !!securetripcode                           any string
        self.id = None              #string      if post has ID                                      The poster's ID                                                                         any 8 characters
        self.capcode = None         #string      if post has capcode                                 The capcode identifier for a post                                                       Not set, mod, admin, admin_highlight, manager, developer, founder
        self.country = None         #string      if country flags are enabled                        Poster's ISO 3166-1 alpha-2 country code                                                2 character string or XX if unknown
        self.country_name = None    #string      if country flags are enabled                        Poster's country name                                                                   Name of any country
        self.sub = None             #string      OP only, if subject was included                    OP Subject text                                                                         any string
        self.com = None             #string      if comment was included                             Comment (HTML escaped)                                                                  any HTML escaped string
        self.tim = None             #integer     always if post has attachment                       Unix timestamp + microtime that an image was uploaded                                   integer
        self.filename = None        #string      always if post has attachment                       Filename as it appeared on the poster's device                                          any string
        self.ext = None             #string      always if post has attachment                       Filetype                                                                                .jpg, .png, .gif, .pdf, .swf, .webm
        self.fsize = None           #integer     always if post has attachment                       Size of uploaded file in bytes                                                          any integer
        self.md5 = None             #string      always if post has attachment                       24 character, packed base64 MD5 hash of file    
        self.w = None               #integer     always if post has attachment                       Image width dimension                                                                   any integer
        self.h = None               #integer     always if post has attachment                       Image height dimension                                                                  any integer
        self.tn_w = None            #integer     always if post has attachment                       Thumbnail image width dimension                                                         any integer
        self.tn_h = None            #integer     always if post has attachment                       Thumbnail image height dimension                                                        any integer
        self.filedeleted = None     #integer     if post had attachment and attachment is deleted    If the file was deleted from the post                                                   1 or not set
        self.spoiler = None         #integer     if post has attachment and attachment is spoilered  If the image was spoilered or not                                                       1 or not set
        self.custom_spoiler = None  #integer     if post has attachment and attachment is spoilered  The custom spoiler ID for a spoilered image                                             1-10 or not set
        self.omitted_posts = None   #integer     OP only                                             Number of replies minus the number of previewed replies                                 any integer
        self.omitted_images = None  #integer     OP only                                             Number of image replies minus the number of previewed image replies                     any integer
        self.replies = None         #integer     OP only                                             Total number of replies to a thread                                                     any integer
        self.images = None          #integer     OP only                                             Total number of image replies to a thread                                               any integer
        self.bumplimit = None       #integer     OP only, only if bump limit has been reached        If a thread has reached bumplimit, it will no longer bump                               1 or not set
        self.imagelimit = None      #integer     OP only, only if image limit has been reached       If an image has reached image limit, no more image replies can be made                  1 or not set
        self.last_modified = None   #integer     OP only                                             The UNIX timestamp marking the last time the thread was modified                        UNIX Timestamp
        self.tag = None             #string      OP only, /f/ only                                   The category of .swf upload                                                             Game, Loop, etc..
        self.semantic_url = None    #string      OP only                                             SEO URL slug for thread                                                                 string
        self.since4pass = None      #integer     if poster put 'since4pass' in the options field     Year 4chan pass bought                                                                  any 4 digit year
        self.unique_ips = None      #integer     OP only                                             Number of unique posters in a thread                                                    any integer
        self.m_img = None           #integer     any post that has a mobile-optimized image          Mobile optimized image exists for post                                                  1 or not set
        self.last_replies = None    #array       catalog OP only                                     JSON representation of the most recent replies to a thread                              array of JSON post objects

        self.__dict__.update(json)

    def __str__(self):
        return str(self.no)
    
    def __repr__(self):
        return self.__str__()

    def print(self):
        for key, value in self.__dict__.items():
            if type(value) == str and len(value) > 100:
                print("{} {}...{}".format(key, value[:50], value[-50:]))
            else:
                print(key, value)