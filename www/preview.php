<!DOCTYPE html>
<html>
  <head>
    <title>Recordings</title>
		<link rel="stylesheet" type="text/css" href="style.css" />
  </head>
  <body>
	
	
		<!-- CASES OF PREVIEW -->
    <?php

			/* CASE NO FILE SPECIFIED - redirects to first file */
			if(empty($_GET))
			{		
			
			  $files = scandir("media");
				// Check if recordings are available
				if(count($files) == 2)
				{
					echo "<p>No videos/images saved</p>";
				}
				
				// If recordings are available, select first one
				else 
				{
					foreach($files as $file)
					{
						if(($file != '.') && ($file != '..'))
						{
							// Select first video file and redirect to its preview
							header("Location: preview.php?file=$file"); 
							exit(); 	
						}
					}	
				}
			}
			
			/* CASE DELETE */ 
      if(isset($_GET["delete"])) {
        unlink("media/" . $_GET["delete"]);
      }
			
			/* CASE DELETE ALL */
      if(isset($_GET["delete_all"])) {
        $files = scandir("media");
        foreach($files as $file) unlink("media/$file");
      }
			
			/* CASE SINGLE FILE - MAIN VIEW */
      else if(isset($_GET["file"])) 
			{
				echo "<div id=main>"; 
				
        echo "<div id=heading><h1>Recorded Videos</h1></div>";
				
				echo "<div id=mjpeg_dest>"; 
        if(substr($_GET["file"], -3) == "jpg") echo "<img src='media/" . $_GET["file"] . "' width='640'>";
        else echo "<video id='recordedVideo' controls><source src='media/" . $_GET["file"] . "' type='video/mp4'>Your browser does not support the video tag.</video>";
        echo "</div>"; //end video/image div
				
				// Download and delete button
				echo "<p><input type='button' value='Download' onclick='window.open(\"download.php?file=" . $_GET["file"] . "\", \"_blank\");'> ";
        echo "<input type='button' value='Delete' onclick='window.location=\"preview.php?delete=" . $_GET["file"] . "\";'></p>";
      }
			
			/* List all recorded files */ 
			
			echo "<h1>Files</h1>"; 
		
			// Go through all files, get their names, link and list them
      $files = scandir("media");
      if(count($files) == 2) echo "<p>No videos/images saved</p>";
      else {
        foreach($files as $file) {
          if(($file != '.') && ($file != '..')) {
            $fsz = round ((filesize("media/" . $file)) / (1024 * 1024));
            echo "<p><a href='preview.php?file=$file'>$file</a> ($fsz MB)</p>";
          }
        }
				//delete all button
        echo "<p><input type='button' value='Delete all' onclick='if(confirm(\"Delete all?\")) {window.location=\"preview.php?delete_all\";}'></p>";
				
				echo "</div>"; // ends main div
      }
    ?>
  </body>
</html>
