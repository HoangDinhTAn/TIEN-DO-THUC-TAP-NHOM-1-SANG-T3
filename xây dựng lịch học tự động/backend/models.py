from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Lưu file timetable.db ngay tại thư mục gốc của dự án
DATABASE_URL = "sqlite:///timetable.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String)
    credits = Column(Integer)

class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String, nullable=True)

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    campus = Column(String)
    building = Column(String)
    room_number = Column(String)

class Timeslot(Base):
    __tablename__ = "timeslots"
    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(String)
    start_period = Column(Integer)
    end_period = Column(Integer)

class ClassSchedule(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    timeslot_id = Column(Integer, ForeignKey("timeslots.id"), nullable=True)

    subject = relationship("Subject")
    teacher = relationship("Teacher")
    room = relationship("Room")
    timeslot = relationship("Timeslot")

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()