// 1. Hàm gửi dữ liệu hàng loạt lên Backend
async function handleSaveBatch() {
    // Thu thập dữ liệu từ bảng hoặc các ô input trên giao diện của bạn vào một mảng
    // Ví dụ mảng classesData:
    let classesData = [
        {
            "subject_code": "INT101",
            "subject_name": "Lập trình Cơ bản",
            "credits": 3,
            "teacher_name": "Nguyễn Văn A",
            "day_of_week": "Thứ 2",
            "start_period": 1,
            "end_period": 3,
            "campus": "Cơ sở 1",
            "building": "A1",
            "room_number": "101"
        },
        // ... các dòng khác
    ];

    try {
        let response = await fetch("http://127.0.0.1:8000/api/classes/detailed/batch", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(classesData)
        });

        let result = await response.json();

        if (response.ok) {
            alert(result.message); // Hiển thị thông báo lưu thành công
            
            // LƯU Ý: Đừng viết lệnh xóa dữ liệu trên bảng ở đây nếu bạn muốn giữ lại hiển thị!
            // Thay vào đó, bạn có thể giữ nguyên màn hình hoặc gọi ngay hàm chạy xếp lịch bên dưới.
            
        } else {
            // Nếu có lỗi (trùng mã học phần, trùng phòng, trùng giờ), hiển thị chi tiết lỗi Backend trả về
            alert("Lỗi: " + result.detail);
        }
    } catch (error) {
        console.error("Lỗi kết nối tới server:", error);
        alert("Không thể kết nối tới server FastAPI!");
    }
}

// 2. Hàm gọi thuật toán tô màu đồ thị và vẽ thời khóa biểu
async function handleRunSchedule() {
    try {
        // Bước A: Chạy thuật toán xếp lịch
        let runRes = await fetch("http://127.0.0.1:8000/api/schedule/run-graph-coloring", {
            method: "POST"
        });
        let runResult = await runRes.json();
        
        if (!runRes.ok) {
            alert("Lỗi xếp lịch: " + runResult.detail);
            return;
        }

        // Bước B: Lấy dữ liệu đã xếp xong để đổ lên lưới thời khóa biểu trên giao diện
        let genRes = await fetch("http://127.0.0.1:8000/api/schedule/generate", {
            method: "POST"
        });
        let genResult = await genRes.json();

        if (genResult.status === "success") {
            renderTimetableGrid(genResult.data); // Hàm vẽ bảng thời khóa biểu của bạn
        }
    } catch (error) {
        console.error("Lỗi khi chạy thuật toán:", error);
    }
}

function renderTimetableGrid(data) {
    // Logic dùng để duyệt qua mảng `data` và điền tên môn học, phòng học vào các ô tương ứng trên bảng HTML của bạn
    console.log("Dữ liệu thời khóa biểu nhận được:", data);
}