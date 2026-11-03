from sqlalchemy.orm import Session
from models import SessionLocal, ClassSchedule, Room, Timeslot

def solve_timetable():
    db = SessionLocal()
    
    classes = db.query(ClassSchedule).all()
    rooms = db.query(Room).all()
    timeslots = db.query(Timeslot).all()
    
    if not rooms or not timeslots or not classes:
        db.close()
        return {"status": "error", "message": "Thiếu dữ liệu phòng học, khung thời gian hoặc lớp học phần!"}

    busy_rooms = set()      
    busy_teachers = set()   
    
    assignment_results = []

    for cls in classes:
        assigned = False
        for room in rooms:
            for ts in timeslots:
                room_slot_key = (room.id, ts.id)
                teacher_slot_key = (cls.teacher_id, ts.id)
                
                if room_slot_key not in busy_rooms and teacher_slot_key not in busy_teachers:
                    busy_rooms.add(room_slot_key)
                    busy_teachers.add(teacher_slot_key)
                    
                    assignment_results.append({
                        "class_id": cls.id,
                        "room_id": room.id,
                        "timeslot_id": ts.id
                    })
                    assigned = True
                    break
            if assigned:
                break
        
        if not assigned:
            db.close()
            return {"status": "failed", "message": f"Không thể xếp lịch cho lớp ID: {cls.id} do thiếu phòng hoặc trùng giờ!"}

    db.close()
    return {"status": "success", "data": assignment_results}