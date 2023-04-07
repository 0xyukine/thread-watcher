import requests

BASE_URL = "https://a.4cdn.org"

def get_boards(session):
	return session.get(f"{BASE_URL}/boards.json")

def get_threads(session, board):
	return session.get(f"{BASE_URL}/{board}/threads.json")

def get_catalog(session, board):
	return session.get(f"{BASE_URL}/{board}/catalog.json")

def get_thread(session, board, thread_id):
	return session.get(f"{BASE_URL}/{board}/thread/{thread_id}.json")