import methods.getmethods
import structs.catalog
import structs.thread
import structs.board
import structs.post

import requests
import html
import json
import re
import os

#ANSI escape codes to make terminal print more readable
GREEN = "\u001b[32;1m"
CYAN = "\u001b[36;1m"
MAGENTA = "\u001b[35;1m"
RESET = "\u001b[0m"

class ThreadWatcher:
	def __init__(self):
		self.session = requests.Session()

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

	def format_comment(self, comment, matched_terms=""):
		comment = re.sub(r'<br>+', '\n', comment)                                                                   #Replace br tags with newlines to maintain original readability
		comment = html.unescape(re.sub(r'<.*?>', '', comment))                                                      #Unescapes escaped special characters and removes HTML tags
		comment = re.sub(r'>{1}[\S ]*', r"{}\g<0>{}".format(GREEN, RESET), comment)                                 #Matches greentext and colours it green                                                    
		comment = re.sub(r'>>[\d]{8}', r"{}\g<0>{}".format(CYAN, RESET), comment)                                   #Matches reply and colours it cyan
		if matched_terms != "":
			comment = re.sub(r'|'.join(matched_terms), r"{}\g<0>{}".format(MAGENTA, RESET), comment)                #Matches found term and colours it magenta
		return comment

	def download(self, board, post, path):
		img = methods.getmethods.get_img_url(self.session, board, post)
		filename = f"{path}/{post.filename}{post.ext}"
		os.makedirs(os.path.dirname(filename), exist_ok=True)
		with open(filename, 'wb') as handler:
			handler.write(img)

	def create_config(self, dict_config=""):
		if dict_config == "":
			dict_config = {"terms":{},"watched":{}}
		else:
			self.check_config(dict_config)
		self.save_config(dict_config)

		return dict_config

	def save_config(self, dict_config):
		with open('./config.json', 'w') as file:
			json.dump(dict_config, file, indent=4)

	def load_config(self):
		with open('./config.json', 'r') as file:
			dict_config = json.load(file)
		return dict_config

	def check_config(self, dict_config):
		if dict_config.keys() != ["terms", "watched"]:
			return False
		else:
			return True

	def add_term(self, dict_config, board, term, sub_terms=[""]):
		if not board in dict_config["terms"].keys():
			dict_config["terms"][board] = {}

		if term in dict_config["terms"][board].keys():
			dict_config["terms"][board][term]["sub_terms"] = list(set(dict_config["terms"][board][term]["sub_terms"] + sub_terms))
		else:
			dict_config["terms"][board][term] = {"sub_terms":sub_terms}
		self.save_config(dict_config)

	def watch_thread(self, dict_config, board, thread_id, last_post_id):
		if not board in dict_config["watched"].keys():
			dict_config["watched"][board] = {}

		dict_config["watched"][board][thread_id] = last_post_id
		self.save_config(dict_config)