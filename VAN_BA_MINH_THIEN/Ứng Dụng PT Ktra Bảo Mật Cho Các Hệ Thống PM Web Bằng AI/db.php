<?php
$host = 'localhost';
$dbname = 'ai_security_tool'; // Khớp chính xác với tên DB trên ảnh của bạn
$username = 'root';           // Mặc định XAMPP
$password = '';               // Mặc định XAMPP

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8mb4", $username, $password);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
} catch (PDOException $e) {
    die("Lỗi kết nối CSDL: " . $e->getMessage());
}
?>