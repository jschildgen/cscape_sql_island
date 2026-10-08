<?php
// Get the message from POST data
$message = isset($_POST['message']) ? $_POST['message'] : '';

// Validate and sanitize the message
$message = trim($message);

// Remove newlines
$message = str_replace("\n", '', $message);
$message = str_replace("\r", '', $message);

// Only process if message is not empty
if (!empty($message)) {
    // Append message to chat.txt as a new line
    file_put_contents('chat.txt', $message . "\n", FILE_APPEND | LOCK_EX);
    
    // Return success
    echo json_encode(['status' => 'success', 'message' => 'Message saved']);
} else {
    // Return error if message is empty
    http_response_code(400);
    echo json_encode(['status' => 'error', 'message' => 'No message provided']);
}
?>