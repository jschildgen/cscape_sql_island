<?php
require_once("config.php");

header('Content-Type: application/json');


$LLM_API_URL = "https://api.openai.com/v1/chat/completions";
$LLM_MODEL = "gpt-6-luna";
$API_KEY = $OPENAI_API_KEY;

$LLM_API_URL = "https://api.blablador.fz-juelich.de/v1/chat/completions";
$LLM_MODEL = "alias-large";
$API_KEY = $LLM_API_KEY;


$jsonInput = file_get_contents('php://input');
$postData = json_decode($jsonInput, true) ?: [];

// Only handle image validation
if (empty($postData['image_data'] ?? '')) {
    echo json_encode(['valid' => false, 'reason' => 'No image data provided', 'debug' => 'image_data field missing']);
    exit;
}

$imageData = $postData['image_data'];

// Basic base64 validation
if (!preg_match('/^[a-zA-Z0-9\/+=]+$/', $imageData)) {
    echo json_encode(['valid' => false, 'reason' => 'Invalid base64 image data', 'debug' => 'Base64 format invalid']);
    exit;
}

// Detect MIME type
$imageMime = 'image/png';
$firstBytes = base64_decode(substr($imageData, 0, 8));
if ($firstBytes !== false && strlen($firstBytes) >= 3) {
    if ($firstBytes[0] === "\xFF" && $firstBytes[1] === "\xD8" && $firstBytes[2] === "\xFF") {
        $imageMime = 'image/jpeg';
    }
}

$imageUrl = "data:{$imageMime};base64," . $imageData;

// Simple prompt
$prompt = "Check if this is the correct ER diagram. We need villages(villageid primary key) and inhabitants(personid primary key, name, gender, job, gold). 1:N from village to inhabitant (lives in), 1:N from inhabitant to village (chief). Answer only a single word: OK or a one word error, e.g. MISSING_ATTRIBUTES, MISSING_ENTITIES, MISSING_RELATIONSHIPS, MISSING_CARDINALITIES, MISSING_PRIMARY_KEY, ... (or whatever the reason is)";

// Build request
$data = [
    "model" => $LLM_MODEL,
    "messages" => [
        [
            "role" => "user",
            "content" => [
                ["type" => "text", "text" => $prompt],
                ["type" => "image_url", "image_url" => ["url" => $imageUrl]]
            ]
        ]
    ],
    "max_completion_tokens" => 5000,
    "reasoning_effort" => "low"
    //"temperature" => 0.1
];

// Send request
$ch = curl_init($LLM_API_URL);
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_POST => true,
    CURLOPT_HTTPHEADER => [
        "Authorization: Bearer " . $API_KEY,
        "Content-Type: application/json"
    ],
    CURLOPT_POSTFIELDS => json_encode($data),
    CURLOPT_TIMEOUT => 60
]);

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$curlError = curl_error($ch);
curl_close($ch);

// Handle response
if ($httpCode !== 200 || !$response) {
    echo json_encode([
        'valid' => false,
        'reason' => 'LLM API error: HTTP ' . $httpCode,
        'debug' => substr($response, 0, 500) . ($curlError ? " | cURL: " . $curlError : "")
    ]);
    exit;
}

$json = json_decode($response, true);

if (!$json) {
    echo json_encode([
        'valid' => false,
        'reason' => 'Invalid JSON from LLM',
        'debug' => substr($response, 0, 500)
    ]);
    exit;
}

// Extract content
$content = '';
if (isset($json['choices'][0]['message']['content'])) {
    $content = $json['choices'][0]['message']['content'];
} else {
    echo json_encode([
        'valid' => false,
        'reason' => 'No content in LLM response',
        'debug' => substr(json_encode($json), 0, 5000)
    ]);
    exit;
}

$content = trim($content);

// Simple parsing: OK means valid, anything else is the error reason
if (strtoupper($content) === 'OK') {
    file_put_contents('chat.txt', "#ER_SOLVED" . "\n", FILE_APPEND | LOCK_EX);
    echo json_encode(['valid' => true, 'reason' => 'OK']);
} else {
    echo json_encode(['valid' => false, 'reason' => strtoupper($content), 'debug' => 'LLM response: ' . $response]);
}
