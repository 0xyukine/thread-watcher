import methods.getmethods
import structs.catalog
import structs.thread
import structs.board
import structs.post

import requests

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