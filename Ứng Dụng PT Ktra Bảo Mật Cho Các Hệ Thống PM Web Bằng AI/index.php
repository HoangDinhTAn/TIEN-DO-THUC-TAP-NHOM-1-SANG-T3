<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>AI Security Tool</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script>
        function switchTab(tab) {
            document.getElementById('sast-form').style.display = (tab === 'sast') ? 'block' : 'none';
            document.getElementById('dast-form').style.display = (tab === 'dast') ? 'block' : 'none';
            document.getElementById('tab-sast').className = (tab === 'sast') ? 'nav-link active' : 'nav-link';
            document.getElementById('tab-dast').className = (tab === 'dast') ? 'nav-link active' : 'nav-link';
        }
    </script>
</head>
<body class="bg-light">
<div class="container mt-5">
    <div class="card shadow">
         <div class="card-header bg-dark text-white text-center py-3">
            <img src="anninh.png" alt="Logo" style="height: 70px; margin-bottom: 15px;">
            <h1>🛡️ AI Security Tool</h1>
            <p>(Giải pháp bảo mật dành cho Vibecoder)</p>
            <!-- NÚT XEM LỊCH SỬ ĐƯỢC THÊM VÀO ĐÂY -->
            <a href="history.php" class="btn btn-outline-light btn-sm mt-2">🕒 Xem Lịch sử Quét</a>
        </div>
        <div class="card-body">
            <!-- Thanh điều hướng Tab -->
            <ul class="nav nav-tabs mb-4">
                <li class="nav-item">
                    <a class="nav-link active" id="tab-sast" href="#" onclick="switchTab('sast')">📁 Phân tích Tĩnh (Upload Code)</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" id="tab-dast" href="#" onclick="switchTab('dast')">🌐 Phân tích Động (Quét URL)</a>
                </li>
            </ul>

            <!-- FORM 1: SAST (Tĩnh) -->
            <div id="sast-form">
                <form action="sast_handler.php" method="POST" enctype="multipart/form-data">
                    <div class="mb-3">
                        <label class="form-label fw-bold">Tải file code PHP lên:</label>
                        <input class="form-control" type="file" name="code_file" accept=".php,.txt" required>
                    </div>
                    <button type="submit" class="btn btn-primary">🚀 Phân tích Code</button>
                </form>
            </div>
            <!-- FORM 2: DAST (Động) -->
            <div id="dast-form" style="display: none;">
                <form action="dast_handler.php" method="POST">
                    <div class="mb-3">
                        <label class="form-label fw-bold">Nhập URL cần quét (VD: http://localhost):</label>
                        <input class="form-control" type="url" name="target_url" placeholder="Điền link vào website vào đây" required>
                    </div>
                    <button type="submit" class="btn btn-danger">🎯 Bắt đầu tấn công thử nghiệm</button>
                </form>
            </div>
        </div>
    </div>
</div>
</body>
</html>