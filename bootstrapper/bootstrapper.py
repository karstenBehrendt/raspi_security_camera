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

sleep_interval = 5

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
	bf.set_process_id(".bid")
	time.sleep(sleep_interval)
	pid = bf.get_process_id(".b2id")
	#pid = str(12345)
 
	# run forever
	while True: 		
		time.sleep(sleep_interval)
		
		# FIXME just restart second bootstrapper
		if not bf.check_if_process_running(pid): 
			bf.reboot()
		
		check_daily_reboot()
		if debug: 
			print("another time step")
		
		



main()
