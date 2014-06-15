//
// Camera Interface
//
function set_preset(value) {

  document.getElementById("video_width").value = value.substr(0, 4);
  document.getElementById("video_height").value = value.substr(5, 4);
  document.getElementById("video_fps").value = value.substr(10, 2);
  document.getElementById("MP4Box_fps").value = value.substr(13, 2);
  document.getElementById("image_width").value = value.substr(16, 4);
  document.getElementById("image_height").value = value.substr(21, 4);
  send_cmd("px " + value);

}

function set_res() {
  
  while(document.getElementById("video_width").value.length < 4) document.getElementById("video_width").value = "0" + document.getElementById("video_width").value;
  while(document.getElementById("video_height").value.length < 4) document.getElementById("video_height").value = "0" + document.getElementById("video_height").value;
  while(document.getElementById("video_fps").value.length < 2) document.getElementById("video_fps").value = "0" + document.getElementById("video_fps").value;
  while(document.getElementById("MP4Box_fps").value.length < 2) document.getElementById("MP4Box_fps").value = "0" + document.getElementById("MP4Box_fps").value;
  while(document.getElementById("image_width").value.length < 4) document.getElementById("image_width").value = "0" + document.getElementById("image_width").value;
  while(document.getElementById("image_height").value.length < 4) document.getElementById("image_height").value = "0" + document.getElementById("image_height").value;
  
  send_cmd("px " + document.getElementById("video_width").value + " " + document.getElementById("video_height").value + " " + document.getElementById("video_fps").value + " " + document.getElementById("MP4Box_fps").value + " " + document.getElementById("image_width").value + " " + document.getElementById("image_height").value);

}

function set_ce() {
  
  while(document.getElementById("ce_u").value.length < 3) document.getElementById("ce_u").value = "0" + document.getElementById("ce_u").value;
  while(document.getElementById("ce_v").value.length < 3) document.getElementById("ce_v").value = "0" + document.getElementById("ce_v").value;
  
  send_cmd("ce " + document.getElementById("ce_en").value + " " + document.getElementById("ce_u").value + " " + document.getElementById("ce_v").value);

}

function set_roi() {
  
  while(document.getElementById("roi_x").value.length < 5) document.getElementById("roi_x").value = "0" + document.getElementById("roi_x").value;
  while(document.getElementById("roi_y").value.length < 5) document.getElementById("roi_y").value = "0" + document.getElementById("roi_y").value;
  while(document.getElementById("roi_w").value.length < 5) document.getElementById("roi_w").value = "0" + document.getElementById("roi_w").value;
  while(document.getElementById("roi_h").value.length < 5) document.getElementById("roi_h").value = "0" + document.getElementById("roi_h").value;
  
  send_cmd("ri " + document.getElementById("roi_x").value + " " + document.getElementById("roi_y").value + " " + document.getElementById("roi_w").value + " " + document.getElementById("roi_h").value);

}

/*
		End of camera interface
*/




//
// raspimjpeg web stream
//
var mjpeg_img;
var halted = 0;

// The main part of our streaming
function reload_img () {
  if(!halted) mjpeg_img.src = "cam_pic.php?time=" + new Date().getTime();
  else setTimeout("reload_img()", 500);
}

function error_img () {
  setTimeout("mjpeg_img.src = 'cam_pic.php?time=' + new Date().getTime();", 100);
}

//
// Ajax Status
//
var ajax_status;

if(window.XMLHttpRequest) {
  ajax_status = new XMLHttpRequest();
}
else {
  ajax_status = new ActiveXObject("Microsoft.XMLHTTP");
}


ajax_status.onreadystatechange = function() {
	/* Changing content based on status file */
  if(ajax_status.readyState == 4 && ajax_status.status == 200) {

    if(ajax_status.responseText == "off")
		{
			// status indicators
			document.getElementById("videoRecording").innerHTML = "camera disabled"; 
			document.getElementById("videoRecording").style.cssText="background-color: white"; 
			document.getElementById("videoWillBeStored").innerHTML = "this part is going not going to be stored"; 
			document.getElementById("videoWillBeStored").style.cssText= "background-color: white"; 

			// start button 
			document.getElementById("restartButton").innerHTML = "Start"; 
			document.getElementById("restartButton").setAttribute( "onClick", "javascript: start_camera();" )
			
    }
    else if(ajax_status.responseText == "storing") 
		{
		
			// status indicators
			document.getElementById("videoRecording").innerHTML = "video stream active"; 
			document.getElementById("videoRecording").style.cssText= "background-color: green"; 
			document.getElementById("videoWillBeStored").innerHTML = "this part is going to be stored"; 
			document.getElementById("videoWillBeStored").style.cssText= "background-color: green"; 
			
			// manual record button
			document.getElementById("recordingButtonDiv").innerHTML = '<button class="bigButton" onclick="stopRecording()">stop\nrecording</button>'; 
			
			// stop button 
			document.getElementById("restartButton").innerHTML = "Stop"; 
			document.getElementById("restartButton").setAttribute( "onClick", "javascript: send_security_camera('off');" )
			

		}
		else if(ajax_status.responseText == "removing")
		{
			// status indicators
			document.getElementById("videoRecording").innerHTML = "video stream active"; 
			document.getElementById("videoRecording").style.cssText= "background-color: green"; 
			document.getElementById("videoWillBeStored").innerHTML = "this part is going not going to be stored"; 
			document.getElementById("videoWillBeStored").style.cssText= "background-color: red"; 
			
			// manual record button
			document.getElementById("recordingButtonDiv").innerHTML = '<button class="bigButton" onclick="startRecording()" >Record</button>'; 
			
			
			// stop button 
			document.getElementById("restartButton").innerHTML = "Stop"; 
			document.getElementById("restartButton").setAttribute( "onClick", "javascript: send_security_camera('off');" )
		}
    else if(ajax_status.responseText.substr(0,5) == "Error") alert("Error in RaspiMJPEG: " + ajax_status.responseText.substr(7) + "\nRestart RaspiMJPEG (./RPi_Cam_Web_Interface_Installer.sh start) or the whole RPi.");
    
    reload_ajax(ajax_status.responseText);

  }
	
}

/*
	Some 'dynamic html'
*/
function start_camera()
{
	window.location="start.php";
}

function splitSettingsDiv()
{
	document.getElementById("settingsDiv").innerHTML = "" + 
	"<button class='smallButton' onclick=\"window.location = 'video_settings.html'\"> Camera </button> <br>" + 
	"<button class='smallButton' onclick=\"window.location = 'motion_settings.html'\"> Motion </button><br>" +
	"<button class='smallButton' onclick=\"window.location = 'storage_settings.html'\"> Storage </button>"; 
}

function startRecording()
{
	// send signal to start recording to video control script
	send_cmd_video_control("ca 1"); 
	document.getElementById("recordingButtonDiv").innerHTML = '<button class="bigButton" onclick="stopRecording()">stop\nrecording</button>'; 
	
}

function stopRecording()
{
	// send signal to stop recording to video control script
	send_cmd_video_control("ca 0"); 
	document.getElementById("recordingButtonDiv").innerHTML = '<button class="bigButton" onclick="startRecording()" >Record</button>'; 

}

function status_popup()
{
	new_window = window.open("status.php", "Camera Status", 'height=250, width=300');
	if(window.focus) {new_window.focus()}
	return false; 
}





/*
	End of 'dynamic html'
*/


/*
	Communication with status file
*/

function reload_ajax (last) {
  ajax_status.open("GET","status_mjpeg.php?last=" + last,true);
  ajax_status.send();
}

//
// Ajax Commands
//
var ajax_cmd;

if(window.XMLHttpRequest) {
  ajax_cmd = new XMLHttpRequest();
}
else {
  ajax_cmd = new ActiveXObject("Microsoft.XMLHTTP");
}

/*
	Communication with raspimjpeg
*/
function send_cmd (cmd) {
	// Because Javacript does not like changing server files too much, this is done with php
  ajax_cmd.open("GET","raspimjpeg_pipe.php?cmd=" + cmd,true);
  ajax_cmd.send();
}

// Communication with video control script
function send_cmd_video_control (cmd) {
	// Because Javacript does not like changing server files too much, this is done with php
  ajax_cmd.open("GET","video_control_pipe.php?cmd=" + cmd,true);
  ajax_cmd.send();
}

function send_security_camera(cmd) {
	// Because Javacript does not like changing server files too much, this is done with php
  ajax_cmd.open("GET","security_camera_pipe.php?cmd=" + cmd,true);
  ajax_cmd.send();
}


//
// main - started by body onload
//
function init() {

  // status
  reload_ajax("");
  // mjpeg
  mjpeg_img = document.getElementById("mjpeg_dest");
  mjpeg_img.onload = reload_img;
  mjpeg_img.onerror = error_img;
  reload_img();


}
