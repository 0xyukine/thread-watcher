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
		self.boards = []

	# def get_catalog(self, board):
	# 	threads = []
	# 	response = methods.getmethods.get_catalog(self.session, board).json()
	# 	for page in response:
	# 		for thread in page["threads"]:
	# 			threads.append(structs.thread.Thread(thread))

	# 	return threads

	def update_watched(self):
		board_dict = {}
		for board in self.boards:
			board_dict[board.board] = board.update_watched()
		
		return board_dict

	def get_catalog(self, board):
		for b in self.boards:
			if b.board == board:
				return b

		b = structs.board.Board(board)
		self.boards.append(b)
		return b

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

	def update_thread(self, board, thread_dict):
		old = [*thread_dict.values()][0]
		new = self.get_thread(board, [*thread_dict.keys()][0])

		#test which is longer, higher deletion rate could result in older version being longer
		if len(new) > len(old):
			count = len(old)
		else:
			count = len(new)

		count_old = 0
		count_new = 0

		deleted_posts = []

		new_list = []
		for i in range(len(new)):
			new_list.append(new[i].no)

		#iterate through both lists and record discrepancies
		for x in range(count):
			print(x)

			#keep iterating while appending old deleted posts until list items match again
			while True:
				if str(old[count_old]) == str(new[count_new].no):
					print("Match:",str(old[count_old]),str(new[count_new].no), len(old), len(new), count_old, count_new)
					count_new += 1
					count_old += 1
					break
				else:
					print("NoMat:",str(old[count_old]),str(new[count_new].no), len(old), len(new), count_old, count_new)
					deleted_posts.append(old[count_old])
					#Checks to see if incrementating will cause out of bounds error 
					if count_old + 1 == len(old):
						break
					else:
						count_old += 1
			
		if len(new) > count_new:
			new = new[count_new:]

		return(old, new, deleted_posts)

	def search_matched(self, thread_dict):
		matched_posts = {}
		for board in thread_dict["terms"]:
			catalog_threads = self.get_catalog(board)
			for thread in catalog_threads: 															#search through catalog
				op_terms = list(thread_dict["terms"][board].keys())									#use board terms as keys (typically thread general acronym in intended use case)
				if thread.sub != None:
					op_matches = re.findall(r'|'.join(op_terms), thread.sub, re.IGNORECASE)
					if op_matches:
						matched_posts[thread.no] = {"board":board, "sub":thread.sub, "posts":[]}
						post_terms = thread_dict["terms"][board][op_matches[0]]["sub_terms"] 		#prone to breaking if more than 1 matching term in sub
						if post_terms[0] != "":														#Matches everything if left as a null string
							for post in self.get_thread(board,thread.no):							#search through thread
								if post.com != None and post.no != thread.no:
									post_matches = re.findall(r'|'.join(post_terms), post.com, re.IGNORECASE)
									if post_matches:
										matched_posts[thread.no]["posts"].append({post.no:self.format_comment(post.com)})

		return matched_posts