from collections import defaultdict
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models import SessionLocal, Subject, Teacher, Room, Timeslot, ClassSchedule, init_db

app = FastAPI()

# Cấu hình CORS cho phép Frontend kết nối
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ClassDetailSchema(BaseModel):
    subject_code: str
    subject_name: str
    credits: int
    teacher_name: str
    day_of_week: str
    start_period: int
    end_period: int
    campus: str
    building: str
    room_number: str

# 1. API Nhập liệu tự do: Lưu toàn bộ dữ liệu vào CSDL mà KHÔNG báo lỗi trùng lặp hay xung đột
@app.post("/api/classes/detailed/batch")
def create_detailed_classes_batch(classes: list[ClassDetailSchema], db: Session = Depends(get_db)):
    for item in classes:
        # Xử lý Môn học (Cho phép trùng mã môn để mở nhiều nhóm lớp học phần khác nhau)
        subject = db.query(Subject).filter(Subject.code == item.subject_code).first()
        if not subject:
            subject = Subject(code=item.subject_code, name=item.subject_name, credits=item.credits)
            db.add(subject)
            db.commit()
            db.refresh(subject)

        # Xử lý Giảng viên
        teacher = db.query(Teacher).filter(Teacher.full_name == item.teacher_name).first()
        if not teacher:
            teacher = Teacher(full_name=item.teacher_name)
            db.add(teacher)
            db.commit()
            db.refresh(teacher)

        # Xử lý Phòng học
        room = db.query(Room).filter(
            Room.campus == item.campus,
            Room.building == item.building,
            Room.room_number == item.room_number
        ).first()
        if not room:
            room = Room(campus=item.campus, building=item.building, room_number=item.room_number)
            db.add(room)
            db.commit()
            db.refresh(room)

        # Xử lý Khung giờ ban đầu do người dùng nhập
        timeslot = db.query(Timeslot).filter(
            Timeslot.day_of_week == item.day_of_week,
            Timeslot.start_period == item.start_period,
            Timeslot.end_period == item.end_period
        ).first()
        if not timeslot:
            timeslot = Timeslot(day_of_week=item.day_of_week, start_period=item.start_period, end_period=item.end_period)
            db.add(timeslot)
            db.commit()
            db.refresh(timeslot)

        # Lưu bản ghi vào bảng ClassSchedule để chờ thuật toán sắp xếp lại
        db_class = ClassSchedule(
            subject_id=subject.id,
            teacher_id=teacher.id,
            room_id=room.id,
            timeslot_id=timeslot.id
        )
        db.add(db_class)
    
    db.commit()
    return {"message": "Nhập liệu thành công! Bạn có thể bấm chạy thuật toán để hệ thống tự động sắp xếp thời khóa biểu tối ưu."}

# 2. Thuật toán Tự động Xếp lịch: Tô màu đồ thị kết hợp tham lam (Giải quyết triệt để xung đột)
@app.post("/api/schedule/run-graph-coloring")
def run_graph_coloring_algorithm(db: Session = Depends(get_db)):
    classes = db.query(ClassSchedule).all()
    timeslots = db.query(Timeslot).all()
    rooms = db.query(Room).all()
    
    if not classes:
        raise HTTPException(status_code=400, detail="Không có lớp học phần nào để xếp lịch!")
    if not timeslots:
        raise HTTPException(status_code=400, detail="Chưa cấu hình danh sách khung giờ (Timeslot) trong hệ thống!")
    if not rooms:
        raise HTTPException(status_code=400, detail="Chưa cấu hình danh sách phòng học trong hệ thống!")

    # Chuyển đổi dữ liệu thành các đỉnh (vertices) của đồ thị
    class_list = []
    for c in classes:
        class_list.append({
            "id": c.id,
            "teacher_id": c.teacher_id,
            "subject_name": c.subject.name if c.subject else "N/A"
        })
    
    # Sắp xếp danh sách lớp theo thứ tự ưu tiên (Thuật toán tham lam / Welsh-Powell)
    sorted_classes = sorted(class_list, key=lambda x: x["id"], reverse=True)
    
    teacher_busy = defaultdict(set) # Theo dõi giảng viên bận theo khung giờ
    room_busy = defaultdict(set)       # Theo dõi phòng học bận theo khung giờ
    
    allocation_results = {}
    unassigned_classes = []

    # Duyệt qua từng lớp để "tô màu" (gán Khung giờ và Phòng học hợp lý)
    for c in sorted_classes:
        c_id = c["id"]
        t_id = c["teacher_id"]
        
        assigned = False
        # Thử duyệt qua từng khung giờ có sẵn
        for ts in timeslots:
            ts_id = ts.id
            
            # Kiểm tra ràng buộc: Giảng viên đã có lịch dạy ở khung giờ này chưa?
            if t_id in teacher_busy[ts_id]:
                continue 
                
            # Tìm một phòng học còn trống ở khung giờ này
            available_room = None
            for r in rooms:
                if r.id not in room_busy[ts_id]:
                    available_room = r.id
                    break
            
            # Nếu thỏa mãn: Giảng viên rảnh và tìm được phòng trống -> Gán lịch!
            if available_room is not None:
                allocation_results[c_id] = {
                    "timeslot_id": ts_id,
                    "room_id": available_room
                }
                # Đánh dấu giảng viên và phòng học bận ở khung giờ này
                teacher_busy[ts_id].add(t_id)
                room_busy[ts_id].add(available_room)
                assigned = True
                break
                
        if not assigned:
            unassigned_classes.append(c_id)

    # Cập nhật kết quả sắp xếp chuẩn vào CSDL SQLite
    for c_id, alloc in allocation_results.items():
        db_class = db.query(ClassSchedule).filter(ClassSchedule.id == c_id).first()
        if db_class:
            db_class.timeslot_id = alloc["timeslot_id"]
            db_class.room_id = alloc["room_id"]
            
    db.commit()
    
    if unassigned_classes:
        return {
            "status": "warning",
            "message": f"Xếp lịch hoàn tất, nhưng có {len(unassigned_classes)} lớp không tìm được phòng hoặc khung giờ phù hợp do thiếu tài nguyên!",
            "unassigned_ids": unassigned_classes
        }
        
    return {
        "status": "success", 
        "message": "Thuật toán tô màu đồ thị đã tự động sắp xếp thời khóa biểu thành công, đảm bảo không có xung đột!"
    }

# 3. API Lấy kết quả hiển thị lên lưới thời khóa biểu
@app.post("/api/schedule/generate")
def generate_schedule(db: Session = Depends(get_db)):
    classes = db.query(ClassSchedule).all()
    result = []
    for c in classes:
        if c.timeslot and c.room and c.subject and c.teacher:
            result.append({
                "subject_code": c.subject.code,
                "subject_name": c.subject.name,
                "teacher_name": c.teacher.full_name,
                "day_of_week": c.timeslot.day_of_week,
                "start_period": c.timeslot.start_period,
                "end_period": c.timeslot.end_period,
                "room_info": f"{c.room.room_number} - {c.room.building} ({c.room.campus})"
            })
    return {"status": "success", "data": result}