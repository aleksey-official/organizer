<?php
session_start();
$db = new mysqli('localhost', 'root', '', 'organizer');
if ($db->connect_error) {
    die("Connection failed: " . $db->connect_error);
}
?>