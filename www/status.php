<html>
	<head>
		<title> Camera Status </title>
	</head>
	<body>
		<h2> Camera Status </h2>
		<br>
		Host name: <?php echo gethostname(); ?><br>
		IP-Address: <?php echo $_SERVER['SERVER_ADDR']; ?><br>
		<br>
		raspi_cam_status: <?php 
			$cam_status = file_get_contents("status_mjpeg.txt"); 
			if ($cam_status == "removing") { echo "Active"; }
			elseif ($cam_status == "storing") { echo "Active"; }
			else {echo $cam_status;} 
		?><br>
		Raspi_security_cam version: <?php echo file_get_contents("cam_version.txt") ?><br>
		<br>
	
	
	
	</body>
<html>