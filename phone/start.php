<?php
require_once("config.php");

file_put_contents('chat.txt', '');
echo("mysql -h ".$DB_HOST." -u ".$DB_USER." -p".$DB_PASS." ".$DB_NAME." < 1_setup.dump");
system("mysql -h ".$DB_HOST." -u ".$DB_USER." -p".$DB_PASS." ".$DB_NAME." < 1_setup.dump");

echo "OK";
