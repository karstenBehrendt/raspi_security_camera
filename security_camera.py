#
#	This script is supposed to check if all processes are running smoothly and
#	restart them if they are not. 
#

import os
import time
import datetime
from subprocess import Popen, PIPE

import bootstrapping_functions as bf

debug = True

sleep_interval = 10

# Just because I don't trust these scripts yet
daily_reboot = True
reboot_hour = 15
reboot_minute = 15
reboot_second = 15

bootstap_log = "bootstrap.log"






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
	bf.reboot()
	
	
# Checking on all import webcam processes and second bootstrapper
def main():
	cur_path = os.path.dirname(__file__)
	if cur_path == "": 
		cur_path = "."
	bf.set_process_id(cur_path + "/bootstrapper/.bid")

	### start all processes

	# start second bootstrapper
	os.system("python " + cur_path + "/bootstrapper/bootstrapper2.py &")
	# start webstream and motion 
	os.system(cur_path + "/installer.sh start &")
	# start video_control
	os.system("python " + cur_path + "/controller/video_control.py &")

	
	# give second bootstrapper and video_control some time to initialize
	time.sleep(10)

	# process id bootstrapper 2
	pid_bs2 = bf.get_process_id(cur_path + "/bootstrapper/.b2id") 
	
	# process id video_control
	pid_vc = bf.get_process_id(cur_path + "/controller/.video_control_pid")
 
	if debug: 
		print "second bootstrapper pid: " + str(pid_bs2)
		print "video control pid: " + str(pid_vc)
 
	# run forever
	while True: 		
		time.sleep(sleep_interval)
		
		# currently bootstrapping fails if you kill all python processes
		# If second bootstrapper is down: 
		if not bf.check_if_process_running(pid_bs2): 
			bf.reboot()
		
		# If video_control stopped - we should also check if it still sends out commands regularly
		if not bf.check_if_process_running(pid_vc): 
			print "CRITICAL: video control is not running"
			#bf.reboot()
		
		# check on raspimjpeg
		process = Popen(["pgrep", "raspimjpeg"], stdout=PIPE)
		stdout = process.communicate()[0]
		if stdout == "": 
			print "CRITICAL: we are all going to die with raspi mjpeg"

		# check on raspimjpeg
		process = Popen(["pgrep", "motion"], stdout=PIPE)
		stdout = process.communicate()[0]
		if stdout == "": 
			print "CRITICAL: we are all going to die with motion"
		
		
		# TODO add another PIPE and check for stop messages, etc. here
		
		
		
		check_daily_reboot()
		if debug: 
			print("bootstrapper: everything is up and running")
		
		



main()
