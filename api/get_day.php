<?php
require_once '../functions.php';
$date = $_GET['date'] ?? '';
if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $date)) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid date']);
    exit;
}
$description = getEventForDate($date);
logHistory('view', $date);
$response = ['description' => $description];
if (isLoggedIn()) $response['can_edit'] = true;
echo json_encode($response);