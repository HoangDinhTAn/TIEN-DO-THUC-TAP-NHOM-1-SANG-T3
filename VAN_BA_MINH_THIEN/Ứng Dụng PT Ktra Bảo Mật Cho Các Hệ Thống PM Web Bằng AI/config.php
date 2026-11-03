<?php

// KẾT NỐI DATABASE (PDO)
try {
    $pdo = new PDO("mysql:host=localhost;dbname=ai_security_tool;charset=utf8mb4", "root", "");
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die("Lỗi kết nối CSDL: " . $e->getMessage());
}

?>