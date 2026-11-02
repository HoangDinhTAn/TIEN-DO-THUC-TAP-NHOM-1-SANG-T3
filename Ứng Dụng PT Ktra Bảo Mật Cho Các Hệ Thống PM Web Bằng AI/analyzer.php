<?php
require_once 'config.php';

// LỚP 1: HÀM LỌC THÔ BẰNG REGEX
function regexPreFilter($code) {
    $patterns = [
        '/(mysqli_query|mysql_query)\s*\(/i' => 'Hàm truy vấn SQL thô (Nguy cơ SQL Injection)',
        '/\$_(GET|POST|REQUEST|COOKIE)\s*\[/i' => 'Nhận dữ liệu người dùng trực tiếp',
        '/(eval|system|exec|shell_exec)\s*\(/i' => 'Hàm thực thi lệnh nguy hiểm',
        '/md5\s*\(/i' => 'Hàm băm mật khẩu yếu (MD5)',
        '/file_get_contents\s*\(/i' => 'Đọc file từ URL (Nguy cơ SSRF)'
    ];

    $found_lines = [];
    // Ép kiểu code về string để tránh lỗi Array to string
    $lines = explode("\n", (string)$code); 
    
    foreach ($lines as $idx => $line) {
        foreach ($patterns as $pattern => $desc) {
            if (preg_match($pattern, $line)) {
                $found_lines[] = [
                    'line' => $idx + 1,
                    'code' => trim($line),
                    'reason' => $desc
                ];
                break; 
            }
        }
    }
    return $found_lines;
}

// LỚP 2: HÀM GỌI AI CHO SAST (Upload file)
function callGroqAI($code, $suspicious) {
    $context = "Mã nguồn PHP cần phân tích:\n```php\n" . (string)$code . "\n```\n";
    $context .= "Các dòng nghi vấn do Regex tìm thấy:\n";
    foreach ($suspicious as $s) {
        // Ép kiểu an toàn cho từng phần tử
        $line_num = (string)($s['line'] ?? 'N/A');
        $line_code = (string)($s['code'] ?? '');
        $context .= "- Dòng {$line_num}: {$line_code}\n";
    }

    $prompt = "Bạn là một chuyên gia bảo mật cực kỳ khó tính. Nhiệm vụ của bạn là tìm ra lỗ hổng trong mã nguồn PHP sau.\n"
        . $context
        . "\nLƯU Ý: Bạn BẮT BUỘC phải tìm ra lỗi. Nếu thấy các hàm như mysqli_query, \$_POST, md5, bạn KHÔNG ĐƯỢC phép nói code này an toàn.\n"
        . "Hãy phân tích và trả về ĐÚNG định dạng JSON sau (Không có text thừa, không có markdown):\n"
        . "{\n"
        . "  \"has_vulnerability\": true,\n"
        . "  \"vulnerabilities\": [\n"
        . "    {\n"
        . "      \"type\": \"SQL Injection\",\n"
        . "      \"owasp\": \"A03:2021\",\n"
        . "      \"line\": 10,\n"
        . "      \"explain\": \"Giải thích ngắn gọn...\",\n"
        . "      \"fixed_code\": \"<?php // Code đã sửa an toàn ?>\"\n"
        . "    }\n"
        . "  ]\n"
        . "}";

    $data = [
        'model' => 'openai/gpt-oss-120b', // ĐÃ ĐỔI SANG MODEL MỚI
        'messages' => [['role' => 'user', 'content' => $prompt]],
        'temperature' => 0.1,
        'response_format' => ['type' => 'json_object']
    ];

    $ch = curl_init(GROQ_API_URL);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json',
        'Authorization: Bearer ' . GROQ_API_KEY
    ]);
    
    $response = curl_exec($ch);
    if ($response === false) {
        die("<div style='color:red; padding:20px;'>Lỗi kết nối API: " . curl_error($ch) . "</div>");
    }
    curl_close($ch);

    $json = json_decode($response, true);
    if (isset($json['error'])) {
        die("<div style='color:red; padding:20px;'>Lỗi từ Groq API: " . $json['error']['message'] . "</div>");
    }

    $ai_content = $json['choices'][0]['message']['content'] ?? '{}';
    
    // In ra màn hình Debug để kiểm tra
    echo "<div style='background:#222; color:#0f0; padding:15px; margin:15px; border-radius:5px;'>";
    echo "<strong>🔍 DEBUG (Dữ liệu AI trả về):</strong><br>";
    echo "<pre style='color:#fff; margin-top:10px;'>" . htmlspecialchars($ai_content) . "</pre>";
    echo "</div>";

    return json_decode($ai_content, true);
}

// LỚP 2: HÀM GỌI AI CHO DAST (Quét URL)
function analyzeDASTWithAI($url, $payload_type, $payload, $response_body, $http_code) {
    $response_snippet = substr(strip_tags((string)$response_body), 0, 1000);
    
    $prompt = "Bạn là một chuyên gia kiểm thử xâm nhập (Pentester).\n";
    $prompt .= "Tôi vừa thực hiện tấn công thử nghiệm lỗi **{$payload_type}** vào đường dẫn sau:\n";
    $prompt .= "URL: {$url}\n";
    $prompt .= "Payload sử dụng: {$payload}\n";
    $prompt .= "Mã HTTP trả về: {$http_code}\n\n";
    $prompt .= "Đây là một đoạn trích xuất nội dung (HTML/Text) mà server trả về:\n";
    $prompt .= "```html\n{$response_snippet}\n```\n\n";
    $prompt .= "Dựa vào phản hồi trên, hãy kết luận xem trang web có bị dính lỗ hổng {$payload_type} không.\n";
    $prompt .= "Trả về ĐÚNG định dạng JSON sau (không kèm text thừa):\n";
    $prompt .= "{\n";
    $prompt .= "  \"is_vulnerable\": true,\n";
    $prompt .= "  \"severity\": \"High\",\n";
    $prompt .= "  \"reason\": \"Giải thích lý do...\",\n";
    $prompt .= "  \"recommendation\": \"Lời khuyên khắc phục...\"\n";
    $prompt .= "}";

    $data = [
        'model' => 'openai/gpt-oss-120b', // ĐÃ ĐỔI SANG MODEL MỚI
        'messages' => [['role' => 'user', 'content' => $prompt]],
        'temperature' => 0.1,
        'response_format' => ['type' => 'json_object']
    ];

    $ch = curl_init(GROQ_API_URL);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json',
        'Authorization: Bearer ' . GROQ_API_KEY
    ]);
    
    $response = curl_exec($ch);
    curl_close($ch);

    $json = json_decode($response, true);
    $ai_content = $json['choices'][0]['message']['content'] ?? '{}';
    return json_decode($ai_content, true);
}
?>