from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StudentCreate(BaseModel):
    student_id: str = Field(min_length=1, max_length=30)
    name: str = Field(min_length=1, max_length=120)
    department: str = Field(min_length=1, max_length=120)
    academic_year: str = Field(min_length=1, max_length=30)


class StudentResponse(StudentCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CourseCreate(BaseModel):
    course_id: str = Field(min_length=1, max_length=30)
    course_name: str = Field(min_length=1, max_length=160)


class CourseResponse(CourseCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class AttendanceCreate(BaseModel):
    student_id: int = Field(gt=0)
    course_id: int = Field(gt=0)
    attendance_date: date
    status: Literal["Present", "Absent"]


class AttendanceResponse(AttendanceCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student: StudentResponse
    course: CourseResponse


class DashboardResponse(BaseModel):
    total_students: int
    total_courses: int
    records_for_date: int
    present_count: int
    absent_count: int
