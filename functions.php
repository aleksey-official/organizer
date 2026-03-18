<?php
require_once 'config.php';

function isLoggedIn() {
    return isset($_SESSION['user_id']);
}

function getUserId() {
    return $_SESSION['user_id'] ?? null;
}

function getUserName() {
    return $_SESSION['username'] ?? null;
}

function logHistory($action, $date) {
    global $db;
    $user_id = getUserId();
    $stmt = $db->prepare("INSERT INTO history (user_id, action, target_date) VALUES (?, ?, ?)");
    $stmt->bind_param("iss", $user_id, $action, $date);
    $stmt->execute();
    $stmt->close();
}

function getEventForDate($date) {
    global $db;
    $stmt = $db->prepare("SELECT description FROM events WHERE event_date = ?");
    $stmt->bind_param("s", $date);
    $stmt->execute();
    $result = $stmt->get_result();
    if ($row = $result->fetch_assoc()) {
        return $row['description'];
    }
    return null;
}

function saveEventForDate($date, $description, $user_id) {
    global $db;
    $stmt = $db->prepare("INSERT INTO events (event_date, description, created_by) VALUES (?, ?, ?) ON DUPLICATE KEY UPDATE description = VALUES(description), created_by = VALUES(created_by)");
    $stmt->bind_param("ssi", $date, $description, $user_id);
    return $stmt->execute();
}
?>