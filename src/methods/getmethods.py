import requests

BASE_URL = "https://a.4cdn.org"
IMG_URL = "https://i.4cdn.org"

session = requests.Session()

def get_boards():
	return session.get(f"{BASE_URL}/boards.json")

def get_threads(board):
	return session.get(f"{BASE_URL}/{board}/threads.json")

def get_catalog(board):
	return session.get(f"{BASE_URL}/{board}/catalog.json")

def get_thread(board, thread_id):
	return session.get(f"{BASE_URL}/{board}/thread/{thread_id}.json")

def get_img_url(board, post):
	return session.get(f"{IMG_URL}/{board}/{post.tim}{post.ext}").content