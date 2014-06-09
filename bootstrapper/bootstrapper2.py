#
# bootstrapper and bootstrapper2 supervise each other
#	bootstrapper checks on all webcam processes
#


import bootstrapping_functions as bf

import time
sleep_interval = 5

def main(): 
	bf.set_process_id(".b2id")	
	time.sleep(sleep_interval)
	pid = bf.get_process_id(".bid")
	
	while True: 
		time.sleep(sleep_interval)
		print("bootstrap2 up and running")
		# TODO make script somewhat smarter than rebooting
		if not bf.check_if_process_running(pid): 
			bf.reboot()





main()
