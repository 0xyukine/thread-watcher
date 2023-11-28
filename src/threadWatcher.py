import methods.getmethods
import structs.catalog
import structs.thread
import structs.board
import structs.post

import requests
import html
import json
import sys
import re
import os

from pathlib import Path

FWD = Path(__file__)
CWD = Path(sys.argv[0]).absolute()

#ANSI escape codes to make terminal print more readable
GREEN = "\u001b[32;1m"
CYAN = "\u001b[36;1m"
MAGENTA = "\u001b[35;1m"
RESET = "\u001b[0m"

class ThreadWatcher:
	def __init__(self, *, config="."):
		self.session = requests.Session()
		self.boards = []

		if Path(config).exists():
			path = Path(config)
			if path.absolute() == CWD:
				self.SWD = CWD
			elif path.is_absolute():
				self.SWD = path
			else:
				self.SWD = CWD.joinpath(path).resolve()
		else:
			self.SWD = Path(".")

		print(self.SWD)

	def create_catalog(self, board):
		for b in self.boards:
			if b.board == board:
				return b

		b = structs.board.Board(board)
		self.boards.append(b)
		return b

	def update_watched(self):
		board_dict = {}
		for board in self.boards:
			board_dict[board.board] = board.update_watched()
		
		return board_dict

	def auto_watch(self):
		d = self.load_config()["thread_watcher"]
		for board in d.keys():
			for scope in d[board]["catalog"].keys():
				for term in d[board]["catalog"][scope]:
					for thread in self.create_catalog(board).search(term,scope):
						try:
							self.create_catalog(board).watch_thread(thread)
						except ValueError as e:
							print(f"{thread.no}: {e} Matched term: {board}/{scope}/{term}")

	#Stand alone functions

	def get_catalog(self, board):
		threads = []
		response = methods.getmethods.get_catalog(self.session, board).json()
		for page in response:
			for thread in page["threads"]:
				threads.append(structs.thread.Thread(thread))

		return threads

	def get_thread(self, board, thread_id):
		posts = []
		response = methods.getmethods.get_thread(self.session, board, thread_id).json()
		for post in response["posts"]:
			posts.append(structs.post.Post(post))

		return posts

	def format_comment(self, comment, in_terminal=False, matched_terms=""):
		comment = re.sub(r'<br>+', '\n', comment)                                                                   #Replace br tags with newlines to maintain original readability
		comment = html.unescape(re.sub(r'<.*?>', '', comment))                                                      #Unescapes escaped special characters and removes HTML tags
		if in_terminal == True:
			comment = re.sub(r'>{1}[\S ]*', r"{}\g<0>{}".format(GREEN, RESET), comment)                                 #Matches greentext and colours it green                                                    
			comment = re.sub(r'>>[\d]{8}', r"{}\g<0>{}".format(CYAN, RESET), comment)                                   #Matches reply and colours it cyan
			if matched_terms != "":
				comment = re.sub(r'|'.join(matched_terms), r"{}\g<0>{}".format(MAGENTA, RESET), comment)                #Matches found term and colours it magenta
		return comment

	#\[sound=(.*)]
	def download(self, board, post, path):
		img = methods.getmethods.get_img_url(self.session, board, post)
		filename = f"{path}/{post.filename}{post.ext}"
		os.makedirs(os.path.dirname(filename), exist_ok=True)
		with open(filename, 'wb') as handler:
			handler.write(img)

	def save_config(self, dict_config={}, force=False):
		# if filepath == CWD or Path(filepath).is_absolute():
		# 	path = filepath
		# else:
		# 	path = CWD.joinpath(filepath).resolve()

		# path = path.joinpath("config.json")
		# print(path)

		path = self.SWD.joinpath('config.json')
		mode = 'x'

		if force == False:
			if path.exists():
				mode = 'w'
				if dict_config == {}:
					print("Config already exists, proceeding will erase old config")
					print("Are you sure you want to continue (Y/N)")
					r = input().upper()
					if r == "N":
						return
					print("Creating new config")
				else:
					print("Writing to config")

		with path.open(mode) as file:
			json.dump({"thread_watcher":dict_config}, file, indent=4)

	def load_config(self):
		with self.SWD.joinpath('config.json').open('r') as file:
			dict_config = json.load(file)
		return dict_config

	def check_config(self, dict_config):
		if "thread_watcher" in dict_config.keys():
			return True
		else:
			return False
	
	def add_term(self, *, board=None, type=None, scope=None, term=None):
		d = self.load_config()["thread_watcher"]
		if board == None and type == None and term == None:
			return
		if board not in ["a","b","vt","g","trash"]:
			return
		if type not in ["catalog","thread"]:
			return
		if type == "thread" and scope != None and scope not in ["all","com","sub"]:
			return

		if board not in d.keys():
			d[board] = {"catalog":{"all":[],"com":[],"sub":[]},"thread":[]}
		if type == "catalog":
			d[board][type][scope] += term
		elif type == "thread":
			d[board][type] += term
		
		self.save_config(d)