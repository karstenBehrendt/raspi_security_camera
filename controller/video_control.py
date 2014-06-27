#
#
#
#
#

import os
import time
import threading
import ConfigParser
import math



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
max_video_length = float(config.get("vSettings", "video_length")) # in seconds

mjpeg_fifo = str(config.get("vSettings", "mjpeg_fifo"))
motion_fifo = str(config.get("vSettings", "motion_fifo"))
ram_location = str(config.get("vSettings", "ram_location"))
storage_location = str(config.get("vSettings", "storage_location"))
status_file = str(config.get("vSettings", "status_file"))


def system_call(sys_call): 
	if debug: 
		print "sys_call " + str(sys_call) 
	os.system(sys_call)


# checks for active threads
# if none is active and queue is not empty, starts a new one. 
def process_queue(queue): 
	if threading.active_count() != 1: 
		#print "number of active counts too hight: " + str(threading.active_count())
		return queue # one thread is still boxing
	
	if not queue: 
		return queue # queue is empty
		
	# if thread available and queue not empty: 
	new_job = queue[0]
	queue.pop(0)
	
	# Queue is just a simple list of system calls - TODO this can be done smarter
	# start thread
	boxing_thread = threading.Thread(target = system_call, args=(new_job,))
	boxing_thread.start()
	
	return queue




def get_last_file(): 
	files_in_ram = [ f for f in os.listdir(ram_location) if os.path.isfile(os.path.join(ram_location,f)) ]
	files_in_ram.sort() # otherwise it appears to be random
	num_files = len(files_in_ram)
	if debug: 
		#print str(num_files) + " files in ram"
		#print files_in_ram
		pass
	if(num_files >= 1): 
		last_file = files_in_ram[-1] # take the last stored video
		if debug: 
			print last_file
		return last_file
	else: 
		print "No file to be processed"
		return None

def remove_h264(file_name): 
	os.remove(ram_location + file_name)

# returns list of system calls for boxing
def mp4_boxing(file_name, start, end): 
	system_calls = []
	# Store full video, only writing to disk once. 
		
	if debug: 
		print "MP4Box -add " + ram_location + file_name + " " + "-splitx " + str(start) + ":" + str(end) + " " + storage_location + file_name[:-5] + ".mp4"
		# Convert to MP4
	# Current bug here: 
	# Videos that should be split from someTime to end are stored completely. 
	# The new gpac MP4Box is going to support splitting till end. 
	# The current arm release does not do this. Until then - this bug is most likely going to stay. 
	# MP4Box -add file -splitx 0:end outfile actucally works, just not when specifying start != 0
	# bug is fixed in MP4Box, waiting for release
	if not end == 'end': 
		system_calls.append("MP4Box -add " + ram_location + file_name + " " + "-splitx " + str(start) + ":" + str(end) + " " + storage_location + file_name[:-5] + ".mp4")	
	else: 
		system_calls.append("MP4Box -add " + ram_location + file_name + " " + storage_location + file_name[:-5] + ".mp4")
	
	if debug: 
		print "Removing " + file_name
	
	# You could mv / change file names here
	
	# In both cases remove original video file
	system_calls.append("rm " + ram_location + file_name + " -f")
	return system_calls


	
# Checks what to do with the video and delegates tasks
# input: list of motion events (starts and stops)
def enqueue_video(motion, queue): 
	# give the video some time to be completely written to temporary location (maybe memory)
	# time.sleep(5) - TODO check if this was needed at any point
	
	if debug: 
		print "motion: " + str(motion)
	
	file_name = get_last_file()
	if file_name is None: 
		return queue
	
	# current split method: always output one file. 
	# Simple case: motions starts and stops - just cut video
	# Other case: Split using first start and last end. 
	# How much memory do I need to have it all done without using the hard drive/SD card?
	
	# if no motion information is available, just remove current file
	if not motion: 
		if debug:
			pass 
			#print "video wasn't deemed worthy. It will be discarded. Thrown into /dev/null"
		remove_h264(file_name) # can be done without queue			
		return queue
	
	# get all parameters for boxing call
	# MP4Box cuts of end automatically if end is too big
	num_motions = len(motion)
	start = 0 if (motion[0][0] - 2) < 0 else int( math.floor( motion[0][0] -2 + 0.5) )
	end = "end" if (motion[num_motions - 1][1] + 2 > max_video_length) else int( math.floor( motion[num_motions - 1][1] + 2 + 0.5) )

	# sum over all detected motions
	motion_time = 0
	for m in motion: 
		motion_time += m[1] - m[0]
	
	# time from first motion to last motion in seconds
	if end == "end": 
		video_length = max_video_length - start
	else: 
		video_length = end - start 
	
	
	if motion_time > motion_threshold:
		# (hopefully temporary) fix for dark video, if file too small it's noise 
		file_size = os.path.getsize(ram_location + file_name) / 1024.0  /1024.0 #MB
		if debug: 
			print "video file is " + str(file_size) + "MB" 
		# FIXME - add fps factor to fix - this one works for 25fps
		if file_size < video_length * 0.6:
			if debug: 
				print "file too small - probably no light left" 
			remove_h264(file_name)
		else: 
			if debug: 
				print "converting to mp4, splitting and storing"
			# adds new system calls to queue
			queue.extend(	mp4_boxing(file_name, start, end) )
	return queue
	
# can be removed. 
def process_video_old(motion_counter): 
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
	detected_motion = [] # a list of current motions
	current_motion = [0,0]

	queue = [] # videos to be processed
	
	# create ram directory
	os.system("mkdir " + ram_location)

	
	# clear pipe
	try: 
		fifo = os.open(motion_fifo, os.O_RDONLY|os.O_NONBLOCK)
		fifo_content = os.read(fifo, 1000)
		os.close(fifo)
		print "pipe cleaned"
	except: 
		print "pipe clean"	

	print "Video recording started"
	start_video()
	# Yes, for ever and ever without stopping (ever)
	while True: 
	
		# Leave some processing time for others
		time.sleep(sleep_interval)
		current_video_length += sleep_interval
		
		
		
		# At some point, there was something I wanted to see...
		if(debug): 
			#print str(current_video_length) + " motion active: " + str(motion_active)
			pass

		# Check for motion information in pipe, looks a little bulky...
		try: #in case file is opened - it happens, eventhough not too open
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
						#motion_counter +=sleep_interval
						current_motion[0] = current_video_length
						with open(status_file, 'w') as f:
							f.write("storing")
					# 'ca 0' is sent if motion stopped, change state to no motion
					elif fifo_line == "ca 0": 
						if debug: 
							print "motion stopped at " + str(current_video_length)
						current_motion[1] = current_video_length
						detected_motion.append(current_motion)
						current_motion = [0,0]
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
			pass
			#print "motion pipe wasn't ready"

			
		# process open boxing jobs
		if current_video_length > 3: # give it some time to finish 
			queue = process_queue(queue)
			
		
		# check if time seconds # video interval = 0
		if current_video_length >= max_video_length: 
			if motion_active: 
				current_motion[1] = current_video_length
				detected_motion.append(current_motion)
			stop_video()
			
			# convert and store video or delete it (own thread, in queue)
			queue = enqueue_video(detected_motion, queue)
			print "in queue: " + str(queue)
			# reset all counters and start new video
			detected_motion = []
			current_motion = [0,0]
			if motion_active: 
				current_motion[0] = 0
			current_video_length = 0
			#motion_active = False # for now, change activation method to motion frames
			if debug:
				print "----------------------------------------------------" 
				print "Starting new video"
			start_video()
			
			
		
		
main()

