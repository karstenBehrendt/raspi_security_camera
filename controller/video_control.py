#
#
#
#
#

import os
import time
from threading import Thread
import ConfigParser




# Parse config file
config = ConfigParser.ConfigParser()
cur_path = os.path.dirname(__file__)
if cur_path == "": 
	cur_path = "."
print cur_path + "/video_control_config.txt"
config.read(cur_path + "/video_control_config.txt")

print config.sections()

debug = bool(config.get("vSettings", "debug"))

sleep_interval = float(config.get("vSettings", "sleep_interval")) # in seconds
motion_threshold = float(config.get("vSettings", "motion_threshold")) # approx seconds of motion in video
video_length = float(config.get("vSettings", "video_length")) # in seconds

mjpeg_fifo = str(config.get("vSettings", "mjpeg_fifo"))
motion_fifo = str(config.get("vSettings", "motion_fifo"))
ram_location = str(config.get("vSettings", "ram_location"))
storage_location = str(config.get("vSettings", "storage_location"))
status_file = str(config.get("vSettings", "status_file"))


def process_file(file_name): 
	# Based on motion video_control, decide to keep or remove file. 
	keep = False
	if keep: 
		if debug: 
			print "File is being converted and moved"
		mp4_boxing(file_name)
	else:
		if debug: 
			print "last video was not interesting; it goes to /dev/null"
		remove_h264(file_name)


def get_last_file(): 
	files_in_ram = [ f for f in os.listdir(ram_location) if os.path.isfile(os.path.join(ram_location,f)) ]
	files_in_ram.sort() # otherwise it appears to be random
	num_files = len(files_in_ram)
	if debug: 
		#print str(num_files) + " files in ram"
		#print files_in_ram
		pass
	if(num_files >= 2): 
		last_file = files_in_ram[-2] # take the last stored video
		if debug: 
			print last_file
		return last_file
	else: 
		print "No file to be processed"
		return None

def remove_h264(file_name): 
	os.remove(ram_location + file_name)

def mp4_boxing(file_name): 
	# calls converter and copy to storage
	if debug: 
		print "MP4Box -add " + ram_location + file_name + " " + storage_location + file_name[:-5] + ".mp4"
	os.system("MP4Box -add " + ram_location + file_name + " " + storage_location + file_name[:-5] + ".mp4")
	if debug: 
		pass
		#print "Removing " + file_name
	remove_h264(file_name)	
	
	

	
def process_video(motion_counter): 
	# give it sometime to be completed
	time.sleep(5)
	video_length = 30 #in seconds
	file_name = get_last_file()
	if file_name is None: # first video will be ignored
		return 
	if motion_counter > motion_threshold:
		#(hopefully) temporary fix for dark video, if file too small it's noise 
		file_size = os.path.getsize(ram_location + file_name) / 1024.0  /1024.0 #MB
		if debug: 
			print "video file is " + str(file_size) + "MB" 
		if file_size < video_length * 0.2:
			if debug: 
				print "file too small - probably no light left" 
			remove_h264(file_name)
		else: 
			if debug: 
				print "converting to mp4 and storing"
			mp4_boxing(file_name)
	else: 
		if debug: 
			print "video wasn't deemed worthy. It will be discarded. Thrown into /dev/null"
		remove_h264(file_name)	
		
	
	
def start_video(): 
	os.system('echo "ca 1" > ' + mjpeg_fifo)
	
def stop_video(): 
	os.system('echo "ca 0" > ' +  mjpeg_fifo)
	
# For easy checking if process is alive	
def set_process_id(pid_file): 
	cur_path = os.path.dirname(__file__)
	if cur_path == "": 
		cur_path = "."
	pid = os.getpid()
	print cur_path + "/" + pid_file
	with open(cur_path + "/" + pid_file,"w") as myfile: 
		myfile.write(str(pid))

		
		
def main(): 
	set_process_id(".video_control_pid")
	print "video control is up and running"
	# empty ram disk - I hope no kids are looking at this. You should not do this. Also don't run with scissors. 
	os.system("rm " + ram_location + "* -f") # prints error if non-empty - FIXME
	
	set_process_id(".video_control_pid")
	
	current_video_length = 0
	motion_active = False
	motion_counter = 0
	
	# clear pipe
	try: 
		fifo = os.open(motion_fifo, os.O_RDONLY|os.O_NONBLOCK)
		fifo_content = os.read(fifo, 1000)
		os.close(fifo)
		print "pipe cleaned"
	except: 
		print "pipe clean"	

	# Yes, for ever and ever without stopping (ever)
	while True: 
		# Leave some processing time for others
		time.sleep(sleep_interval)
		current_video_length += sleep_interval
		
		# At some point, there was something I wanted to see...
		if(debug): 
			#print str(current_video_length) + " motion active: " + str(motion_active)
			pass

		# Check for motion information in pipe
		try:
			fifo = os.open(motion_fifo, os.O_RDONLY|os.O_NONBLOCK)
			fifo_content = os.read(fifo, 100)
			os.close(fifo)
			fifo_content.split('\n')
			# empty pipe means no state change
			if fifo_content == "": 
				if motion_active: 
					motion_counter += sleep_interval
			else: 
				fifo_content = fifo_content.splitlines()
				for fifo_line in fifo_content: 
					# 'ca 1' is sent if motion was detected
					if fifo_line == "ca 1": 
						if debug:
							print "motion detected at " + str(current_video_length)
						motion_active = True
						motion_counter +=sleep_interval
						with open(status_file, 'w') as f:
							f.write("storing")
					# 'ca 0' is sent if motion stopped, change state to no motion
					elif fifo_line == "ca 0": 
						if debug: 
							print "motion stopped at " + str(current_video_length)
						motion_active = False
						with open(status_file, 'w') as f: 
							f.write("removing")
					elif fifo_line == "": 
						pass
					elif fifo_line == "motion": 
						print "motion frame at " + str(current_video_length)
					else: 
						print "Undefined command in pipe"
		except:
			print "pipe wasn't ready - replace with socket in case of spare time"

		
		# check if time seconds # video interval = 0
		if current_video_length >= video_length: 
			stop_video()
			# convert and store video or delete it (own thread, so it does not delay this process)
			video_conversion_thread = Thread(target = process_video, args=(motion_counter,))
			video_conversion_thread.start()
			# reset all counters and start new video
			motion_counter = 0	
			current_video_length = 0
			#motion_active = False # for now, change activation method to motion frames
			if debug: 
				print "Starting new video"
			start_video()
			
			
		
		
main()

