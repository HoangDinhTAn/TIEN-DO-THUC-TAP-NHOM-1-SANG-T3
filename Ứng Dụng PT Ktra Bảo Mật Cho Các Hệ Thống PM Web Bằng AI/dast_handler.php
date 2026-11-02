<?php
require 'analyzer.php';
require 'db.php'; // Gọi file kết nối DB

if ($_SERVER['REQUEST_METHOD'] === 'POST' && !empty($_POST['target_url'])) {
    $url = $_POST['target_url'];
    
     // 1. Cấu hình Payload
    $payloads = [
        'SQL Injection' => "' OR 1=1 --",
        'Cross-Site Scripting (XSS)' => "<script>alert('XSS')</script>",
        'Command Injection' => "127.0.0.1; whoami",
        'Local File Inclusion (LFI)' => "../../../../etc/passwd"
    ];

    $parsed_url = parse_url($url);
    parse_str($parsed_url['query'] ?? '', $query_params);
    
    if (empty($query_params)) {
        die("<div class='alert alert-danger'>Lỗi: URL phải có tham số (VD: ?id=1) để Tool có thể chèn Payload!</div><a href='index.php'>Quay lại</a>");
    }

    $param_key = array_key_first($query_params);
    $all_results = [];
    $total_vulns = 0;

    echo "<!DOCTYPE html><html><head><meta charset='UTF-8'><link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' rel='stylesheet'></head><body class='bg-light'><div class='container mt-5'>";
    echo "<h2>🎯 Kết quả Phân tích Động (DAST)</h2>";
    echo "<p>Mục tiêu: <strong>" . htmlspecialchars($url) . "</strong> (Tham số test: <code>$param_key</code>)</p><hr>";

    // 2. Vòng lặp gửi Payload
    foreach ($payloads as $type => $payload) {
        $query_params[$param_key] = $payload;
        $new_query = http_build_query($query_params);
        
        $scheme = $parsed_url['scheme'] ?? 'http';
        if (empty($scheme)) { $scheme = 'http'; }
        $test_url = $scheme . '://' . $parsed_url['host'] . ($parsed_url['path'] ?? '') . '?' . $new_query;

        echo "<div class='card mb-4 shadow-sm'>";
        echo "<div class='card-header bg-secondary text-white'>Đang test: <strong>$type</strong></div>";
        echo "<div class='card-body'>";
        echo "<p><strong>Payload gửi đi:</strong> <code>" . htmlspecialchars($payload) . "</code></p>";

        // Gửi Request
        $ch = curl_init($test_url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 10);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
        
        $response = curl_exec($ch);
        
        if ($response === false) {
            echo "<div class='alert alert-danger'>Lỗi cURL: " . curl_error($ch) . "</div>";
            curl_close($ch);
            echo "</div></div>";
            continue;
        }
        
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($http_code != 200 && $http_code != 302) {
            echo "<div class='alert alert-warning'>Không thể kết nối hoặc server trả về mã lỗi: HTTP $http_code</div>";
            echo "</div></div>";
            continue;
        }

        echo "<p class='text-muted'>Đang nhờ AI phân tích phản hồi từ server...</p>";

        // 3. Gọi AI Phân tích
        $ai_result = analyzeDASTWithAI($test_url, $type, $payload, $response, $http_code);
        
        // Lưu lại kết quả để tí nữa lưu DB
        $all_results[] = ['type' => $type, 'result' => $ai_result];
        if (!empty($ai_result['is_vulnerable']) && $ai_result['is_vulnerable'] !== 'false') {
            $total_vulns++;
        }

        // 4. Hiển thị kết quả
        if (isset($ai_result['is_vulnerable']) && $ai_result['is_vulnerable'] === true) {
            echo "<div class='alert alert-danger'>";
            echo "<h4>🚨 PHÁT HIỆN LỖ HỔNG: " . strtoupper($type) . "</h4>";
            echo "<p><strong>Mức độ:</strong> " . htmlspecialchars($ai_result['severity'] ?? 'N/A') . "</p>";
            echo "<p><strong>Bằng chứng:</strong> " . htmlspecialchars($ai_result['reason'] ?? 'N/A') . "</p>";
            echo "<hr>";
            echo "<p><strong>💡 Cách khắc phục:</strong> " . htmlspecialchars($ai_result['recommendation'] ?? 'N/A') . "</p>";
            echo "</div>";
        } else {
            echo "<div class='alert alert-success'>";
            echo "<h5>✅ Không phát hiện lỗ hổng $type rõ ràng.</h5>";
            echo "<p>Lý do: " . htmlspecialchars($ai_result['reason'] ?? 'Server phản hồi bình thường.') . "</p>";
            echo "</div>";
        }

        echo "</div></div>"; // Đóng card
    }
    
    // --- LƯU VÀO DATABASE (SAU KHI TEST XONG TẤT CẢ PAYLOAD) ---
    try {
        $stmt = $pdo->prepare("INSERT INTO scan_history (scan_type, target, vuln_count, details) VALUES (?, ?, ?, ?)");
        $stmt->execute([
            'DAST', 
            $url, 
            $total_vulns, 
            json_encode($all_results) // Lưu mảng kết quả thành JSON
        ]);
    } catch (Exception $e) {
        echo "<div class='alert alert-danger'>Lỗi lưu DB: " . $e->getMessage() . "</div>";
    }
    // -----------------------------------------------------------

    echo "<a href='index.php' class='btn btn-primary mt-3'>Quay lại Trang chủ</a>";
    echo "</div></body></html>";
} else {
    header("Location: index.php");
    exit;
}
?>