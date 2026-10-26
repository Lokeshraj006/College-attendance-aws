from datetime import date

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import Select

from .config import get_settings
from .database import Base, engine, get_db
from .models import Attendance, Course, Student
from .schemas import (
    AttendanceCreate,
    AttendanceResponse,
    CourseCreate,
    CourseResponse,
    DashboardResponse,
    StudentCreate,
    StudentResponse,
)

settings = get_settings()
app = FastAPI(title="College Attendance API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/students", response_model=list[StudentResponse])
def list_students(db: Session = Depends(get_db)) -> list[Student]:
    return list(db.scalars(select(Student).order_by(Student.name)))


@app.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(payload: StudentCreate, db: Session = Depends(get_db)) -> Student:
    student = Student(**payload.model_dump())
    db.add(student)
    try:
        db.commit()
        db.refresh(student)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Student ID already exists.") from None
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unable to save the student.") from None
    return student


@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)) -> Student:
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found.")
    return student


@app.get("/courses", response_model=list[CourseResponse])
def list_courses(db: Session = Depends(get_db)) -> list[Course]:
    return list(db.scalars(select(Course).order_by(Course.course_id)))


@app.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(payload: CourseCreate, db: Session = Depends(get_db)) -> Course:
    course = Course(**payload.model_dump())
    db.add(course)
    try:
        db.commit()
        db.refresh(course)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Course ID already exists.") from None
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unable to save the course.") from None
    return course


def attendance_query() -> Select[tuple[Attendance]]:
    return select(Attendance).options(
        joinedload(Attendance.student), joinedload(Attendance.course)
    ).order_by(Attendance.attendance_date.desc(), Attendance.id.desc())


@app.get("/attendance", response_model=list[AttendanceResponse])
def list_attendance(
    student_id: int | None = Query(default=None, gt=0),
    course_id: int | None = Query(default=None, gt=0),
    attendance_date: date | None = None,
    db: Session = Depends(get_db),
) -> list[Attendance]:
    query = attendance_query()
    if student_id is not None:
        query = query.where(Attendance.student_id == student_id)
    if course_id is not None:
        query = query.where(Attendance.course_id == course_id)
    if attendance_date is not None:
        query = query.where(Attendance.attendance_date == attendance_date)
    return list(db.scalars(query).unique())


@app.post("/attendance", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
def create_attendance(payload: AttendanceCreate, db: Session = Depends(get_db)) -> Attendance:
    if db.get(Student, payload.student_id) is None:
        raise HTTPException(status_code=404, detail="Student not found.")
    if db.get(Course, payload.course_id) is None:
        raise HTTPException(status_code=404, detail="Course not found.")
    record = Attendance(**payload.model_dump())
    db.add(record)
    try:
        db.commit()
        db.refresh(record)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Attendance has already been recorded for this student, course, and date.",
        ) from None
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unable to save attendance.") from None
    return db.scalar(
        attendance_query().where(Attendance.id == record.id)
    )


@app.get("/attendance/student/{student_id}", response_model=list[AttendanceResponse])
def attendance_for_student(student_id: int, db: Session = Depends(get_db)) -> list[Attendance]:
    if db.get(Student, student_id) is None:
        raise HTTPException(status_code=404, detail="Student not found.")
    return list(db.scalars(attendance_query().where(Attendance.student_id == student_id)).unique())


@app.get("/dashboard", response_model=DashboardResponse)
def dashboard(
    selected_date: date | None = None,
    db: Session = Depends(get_db),
) -> DashboardResponse:
    target_date = selected_date or date.today()
    total_students = db.scalar(select(func.count(Student.id))) or 0
    total_courses = db.scalar(select(func.count(Course.id))) or 0
    records_for_date = db.scalar(
        select(func.count(Attendance.id)).where(Attendance.attendance_date == target_date)
    ) or 0
    present_count = db.scalar(
        select(func.count(Attendance.id)).where(
            Attendance.attendance_date == target_date, Attendance.status == "Present"
        )
    ) or 0
    absent_count = db.scalar(
        select(func.count(Attendance.id)).where(
            Attendance.attendance_date == target_date, Attendance.status == "Absent"
        )
    ) or 0
    return DashboardResponse(
        total_students=total_students,
        total_courses=total_courses,
        records_for_date=records_for_date,
        present_count=present_count,
        absent_count=absent_count,
    )
