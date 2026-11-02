<?php
require 'config.php';

// Lấy 50 lần quét gần nhất
$stmt = $pdo->query("SELECT * FROM scan_history ORDER BY scan_date DESC LIMIT 50");
$history = $stmt->fetchAll(PDO::FETCH_ASSOC);
?>
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Lịch sử quét - AI Security Tool</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container mt-5">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2>🕒 Lịch sử Quét (Database)</h2>
        <a href="index.php" class="btn btn-secondary">Quay lại Trang chủ</a>
    </div>

    <div class="card shadow-sm">
        <div class="card-body">
            <table class="table table-hover align-middle">
                <thead class="table-dark">
                    <tr>
                        <th>ID</th>
                        <th>Loại</th>
                        <th>Mục tiêu</th>
                        <th>Lỗ hổng</th>
                        <th>Thời gian</th>
                        <th>Hành động</th>
                    </tr>
                </thead>
                <tbody>
                    <?php if (empty($history)): ?>
                        <tr><td colspan="6" class="text-center">Chưa có lịch sử quét nào.</td></tr>
                    <?php else: ?>
                        <?php foreach ($history as $row): ?>
                            <tr>
                                <td>#<?= $row['id'] ?></td>
                                <td>
                                    <span class="badge <?= $row['scan_type'] === 'SAST' ? 'bg-primary' : 'bg-danger' ?>">
                                        <?= $row['scan_type'] ?>
                                    </span>
                                </td>
                                <td class="text-truncate" style="max-width: 300px;">
                                    <?= htmlspecialchars($row['target']) ?>
                                </td>
                                <td>
                                    <?php if ($row['vuln_count'] > 0): ?>
                                        <span class="text-danger fw-bold"><?= $row['vuln_count'] ?> lỗi</span>
                                    <?php else: ?>
                                        <span class="text-success">An toàn</span>
                                    <?php endif; ?>
                                </td>
                                <td><?= date('d/m/Y H:i', strtotime($row['scan_date'])) ?></td>
                                <td>
                                    <button class="btn btn-sm btn-outline-info" 
                                            onclick="alert('Chi tiết JSON đã được lưu trong DB. Bạn có thể mở phpMyAdmin để xem cột details.')">
                                        Xem chi tiết
                                    </button>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    <?php endif; ?>
                </tbody>
            </table>
        </div>
    </div>
</div>
</body>
</html>