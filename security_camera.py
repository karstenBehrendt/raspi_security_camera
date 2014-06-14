#
#	This script is supposed to check if all processes are running smoothly and
#	restart them if they are not. 
#

import os
import time
import datetime
import sys
from subprocess import Popen, PIPE

debug = True

sleep_interval = 2

# Just because I don't trust these scripts yet
daily_reboot = True
reboot_hour = 15
reboot_minute = 15
reboot_second = 15


cam_active = True
bs_fifo = "/var/www/bootstrapper_pipe"

cur_path = os.path.dirname(__file__)
if cur_path == "": 
	cur_path = "."
error_log = cur_path + "/error.log"


	
def add_to_log(error_msg): 
	with open(error_log, 'a') as el: 
		el.write( str(error_msg) + "\n")
	
	
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


# turns off all processes and stops
# motion is still running, but doesn't get any new images
def turn_off_camera(pid_bs2, pid_vc): 
	camera_active = False
	# stop bootstrapper
	os.system("kill " + str(pid_bs2))
	# stop video control
	os.system("kill " + str(pid_vc))
	# stop recording
	os.system("echo 'ca 0' > /var/www/FIFO")
	# stop raspimjpeg
	os.system(cur_path + "/installer.sh stop")
	# stop raspimjpeg
	os.system("sudo pkill motion") # get sudo out of here
	# tell web interface camera is off
	with open("/var/www/status_mjpeg.txt", "w") as f: 
		f.write("off")
		
	exit()
	
	
def turn_on_camera(): 
	camera_active = True
	
	# start second bootstrapper
	os.system("python " + cur_path + "/bootstrapper/bootstrapper2.py &")
	# start webstream and motion 
	os.system(cur_path + "/installer.sh start &")
	# start video_control
	os.system("python " + cur_path + "/controller/video_control.py &")
	
	# give second bootstrapper and video_control some time to initialize
	time.sleep(10)

	# process id bootstrapper 2
	pid_bs2 = get_process_id(cur_path + "/bootstrapper/.b2id") 
	
	# process id video_control
	pid_vc = get_process_id(cur_path + "/controller/.video_control_pid")

	if debug: 
		print "Camera systems up and running"
		#at least hopefully, there is no check implemented
	
	return [pid_bs2, pid_vc]


# Is there a downside to having the return between each step?
def check_daily_reboot(): 			
	current_time = datetime.datetime.now()
	if not daily_reboot:
		return
	if current_time.hour != reboot_hour:
		return
	if current_time.minute != reboot_minute:
		return
	if abs(current_time.second - reboot_second) < (sleep_interval + 1):
		return
	with open(bootstrap_log, "a") as myfile: 
		myfile.write("Planned daily reboot: ", current_time)
	reboot()
	
	
# Checking on all import webcam processes and second bootstrapper
def main():

	set_process_id(cur_path + "/bootstrapper/.bid")

	### start all processes
	pid_bs2, pid_vc = turn_on_camera()

	if debug: 
		print "second bootstrapper pid: " + str(pid_bs2)
		print "video control pid: " + str(pid_vc)
 
	# run forever
	while True: 		
		time.sleep(sleep_interval)
		
		# currently bootstrapping fails if you kill all python processes
		# If second bootstrapper is down: 
		if not check_if_process_running(pid_bs2): 
			print "bootstrapper is not running"
			add_to_log("bs2 missing - " + datetime.datetime.now().__str__() )
			reboot()
		
		# If video_control stopped - we should also check if it still sends out commands regularly
		if not check_if_process_running(pid_vc): 
			print "CRITICAL: video control is not running"
			add_to_log("video control missing - " + datetime.datetime.now().__str__() )
			reboot()
		
		# check on raspimjpeg
		process = Popen(["pgrep", "raspimjpeg"], stdout=PIPE)
		stdout = process.communicate()[0]
		if stdout == "": 
			print "CRITICAL: we are all going to die with raspi mjpeg"
			add_to_log("raspimjpeg missing - " + datetime.datetime.now().__str__() )
			reboot()

		# check on raspimjpeg
		process = Popen(["pgrep", "motion"], stdout=PIPE)
		stdout = process.communicate()[0]
		if stdout == "": 
			print "CRITICAL: we are all going to die with motion"
			add_to_log("motion missing - " + datetime.datetime.now().__str__() )
			reboot()
		
		
		# TODO add another PIPE and check for stop messages, etc. here
		
		if True: 
			fifo = os.open(bs_fifo, os.O_RDONLY|os.O_NONBLOCK)
			fifo_content = os.read(fifo, 100)
			os.close(fifo)
			fifo_content = fifo_content.splitlines()
			for fifo_line in fifo_content: 
				if fifo_line == "off": 
					turn_off_camera(pid_bs2, pid_vc)
				if fifo_line == "on": 
					turn_on_camera()
		#except:
		#	pass
					
		check_daily_reboot()
		if debug: 
			pass
			#print("bootstrapper: everything is up and running")
		
		



main()
