
import os
from subprocess import PIPE, Popen


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