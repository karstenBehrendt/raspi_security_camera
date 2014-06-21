Security Camera with web interface

The special thing about this tool is that it works in real-time, stores videos including frames before deteced motion and motion detection is based on 'motion'. The real fun part: Full HD 25fps, stable with web interface. Any pi with raspicam can now be a fully functioning security IP cam. 


-------------------------------------------------------------------------------
Installation: 

1) Go to home directory (cd ~) #user pi

2) Clone repo (git clone https://github.com/karstenBehrendt/raspi_security_camera.git)

3) cd ~/raspi_security_camera

4) Set permissions (chmod u+x installer.sh)

5) ./installer.sh install

6) python security_camera.py (for manual start)

7) ./installer.sh autostart_yes #if you want it to start on reboot, for a long time

Default passwords: 
guest: guest, test: test, admin: admin
Actually currently disabled until first release. 

