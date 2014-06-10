#
#
#
#
#

import os
import time

debug = True

check_interval = 0.05 # in seconds
motion_active = True
motion_counter = 0
FIFO2 = "/var/www/FIFO2"

	
def start_video(): 
	os.system('echo "ca 1" > ' + FIFO)
	
def stop_video(): 
	os.system('echo "ca 0" > ' +  FIFO)
	
# For easy checking if process is alive	
def set_process_id(pid_file): 
	pid = os.getpid()
	with open(pid_file,"w") as myfile: 
		myfile.write(str(pid))


def check_motion(): 
		pass
		
def store_motion_info(): 
	pass
			
		
		
def main(): 
	print "ficken"
	set_process_id("video_control_pid")
	# Yes, for ever and ever without stopping (ever)
	while True: 
		time.sleep(sleep_interval)
		if(debug): 
			pass
		fifo = open(FIFO2)
		fifo_content = fifo.read()
		print fifo_content
		fifo_content.split('\n')
		if fifo_content == "": 
			if motion_active: 
				motion_counter += sleep_interval
			continue
		for fifo_line in fifo_content: 
			if fifo_line == "ca 1": 
				motion_active = True
				motion_counter +=sleep_interval
			if fifo_line == "ca 0": 
				motion_active = False



		
			
		# check if time seconds # video interval = 0
		if False: 
			stop_video()
			start_video()
			motion_counter = 0
			#send signal with motion information about last video
			
		
		
main()
		
		
		



