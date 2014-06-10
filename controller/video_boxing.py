import time
import os

debug = True

# Want control file...
video_length = 30 # in seconds
FIFO = "/var/www/FIFO"
ram_location = "/var/www/ram_media/"
storage_location = "/var/www/media/"



def get_last_file(): 
	files_in_ram = [ f for f in os.listdir(ram_location) if os.path.isfile(os.path.join(ram_location,f)) ]
	files_in_ram.sort() # otherwise it appears to be random
	num_files = len(files_in_ram)
	if(num_files > 1): 
		last_file = files_in_ram[0] # take oldest video
		print files_in_ram
		print str(num_files - 1) + " to be processed"
		return last_file
	else: 
		print "No file to be processed"
		return None

def remove_h264(file_name): 
	os.remove(ram_location + file_name)

def mp4_boxing(file_name): 
	# calls converter and copy to storage
	if debug: 
		print "Boxing " + file_name
	os.system("MP4Box -add " + ram_location + file_name + " " + storage_location + file_name[:-5] + ".mp4 > /dev/null")
	#remove_h264(file_name) # can be called here, only gets marked as deleted as first
	remove_h264(file_name)
	
	if debug: 
		print "Removing " + file_name
	


def main():
	while True:
		time.sleep(1)
		file_name = get_last_file()
		if file_name is not None: 
			mp4_boxing(file_name)
			
main()