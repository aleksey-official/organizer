<?php
require_once '../functions.php';
if (!isLoggedIn()) {
    http_response_code(401);
    echo json_encode(['error' => 'Not authorized']);
    exit;
}
$date = $_POST['date'] ?? '';
$description = $_POST['description'] ?? '';
if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $date)) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid date']);
    exit;
}
$user_id = getUserId();
$success = saveEventForDate($date, $description, $user_id);
if ($success) {
    logHistory('edit', $date);
    echo json_encode(['success' => true]);
} else {
    echo json_encode(['success' => false, 'error' => 'Database error']);
}