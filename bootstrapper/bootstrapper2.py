#
# bootstrapper and bootstrapper2 supervise each other
#	bootstrapper checks on all webcam processes
#


import bootstrapping_functions as bf
import os

import time
sleep_interval = 10

def main(): 
	cur_path = os.path.dirname(__file__)
	if cur_path == "": 
		cur_path = "."

	bf.set_process_id(cur_path + "/.b2id")	
	time.sleep(sleep_interval)
	pid = bf.get_process_id(cur_path + "/.bid")
	
	print("bootstrap2 up and running")
	
	while True: 
		time.sleep(sleep_interval)

		# TODO make script somewhat smarter than rebooting
		if not bf.check_if_process_running(pid): 
			print "CRITICAL: Second bootstrap script could not find first bootstrap script"
			bf.reboot()





main()
