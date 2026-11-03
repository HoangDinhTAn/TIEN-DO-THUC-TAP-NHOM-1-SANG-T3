from models import SessionLocal, init_db, Subject, Teacher, Room, Timeslot, ClassSchedule

def seed_data():
    init_db()
    db = SessionLocal()

    # Kiểm tra xem đã có dữ liệu chưa
    if db.query(Subject).count() > 0:
        print("Dữ liệu mẫu đã tồn tại!")
        db.close()
        return

    # 1. Thêm Môn học
    s1 = Subject(code="INT115", name="Lập trình Python", credits=3)
    s2 = Subject(code="INT116", name="Cơ sở dữ liệu", credits=3)
    db.add_all([s1, s2])
    db.commit()

    # 2. Thêm Giảng viên
    t1 = Teacher(full_name="Nguyễn Văn A", email="ane@school.edu.vn")
    t2 = Teacher(full_name="Trần Thị B", email="bt@school.edu.vn")
    db.add_all([t1, t2])
    db.commit()

    # 3. Thêm Phòng học
    r1 = Room(room_number="P.201", capacity=50)
    r2 = Room(room_number="P.302", capacity=30)
    db.add_all([r1, r2])
    db.commit()

    # 4. Thêm Khung thời gian (Timeslots)
    ts1 = Timeslot(day_of_week="Thứ 2", start_period=1, end_period=3)
    ts2 = Timeslot(day_of_week="Thứ 2", start_period=4, end_period=6)
    ts3 = Timeslot(day_of_week="Thứ 3", start_period=1, end_period=3)
    db.add_all([ts1, ts2, ts3])
    db.commit()

    # 5. Thêm Lớp học phần cần xếp lịch
    c1 = ClassSchedule(subject_id=s1.id, teacher_id=t1.id, expected_students=40)
    c2 = ClassSchedule(subject_id=s2.id, teacher_id=t2.id, expected_students=25)
    db.add_all([c1, c2])
    db.commit()

    db.close()
    print("Đã thêm dữ liệu mẫu thành công!")

if __name__ == "__main__":
    seed_data()