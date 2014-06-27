#
# this bootstrapper and the start script check on each other if they are still alive. 
# That is all this script does.



import os
from subprocess import Popen, PIPE

import time
sleep_interval = 10


debug = True



def get_process_id(b_file): 
	f = open(b_file, "r")
	pid = f.read()
	pid = str(pid)
	#print(pid)
	return pid


def set_process_id(b_file): 
	pid = os.getpid()
	with open(b_file,"w") as myfile: 
		myfile.write(str(pid))

# in case of really bad errors, reboot
def reboot(): 
	print("rebooting system") 
	process = Popen(['sudo', 'reboot'], stdout=PIPE)
	stdout, stderr = process.communicate()
	if stdout is not None: 
		print("stdout: " + stdout)
	if stderr is not None: 
		print("stderr: " + stderr)
			
			
def check_if_process_running(pid): 
	try:
		os.kill(int(pid), 0)
		return True
	except:
		return False






def main(): 
	cur_path = os.path.dirname(__file__)
	if cur_path == "": 
		cur_path = "."

	set_process_id(cur_path + "/.b2id")	
	time.sleep(sleep_interval)
	pid = get_process_id(cur_path + "/.bid")
	
	print("bootstrap2 up and running")
	
	while True: 
		time.sleep(sleep_interval)

		if debug: 
			print "bootstrapper up and running"
		
		# reboot on error, this may be done smarter
		if not check_if_process_running(pid): 
			print "CRITICAL: Second bootstrap script could not find first bootstrap script"
			reboot()





main()
