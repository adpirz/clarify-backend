

from sis_mirror.models import (
    Students, Users, Sites, AttendanceFlags,
    Sections, Categories, Courses, Gradebooks,
    DailyRecords, GradeLevels, GradebookSectionCourseAff,
    SsCube, SectionTimeblockAff, Timeblocks, SsCurrent,
    Assignments, ScoreCache, Sessions, Terms, UserTermRoleAff
)

from clarify.models import (
    Student,
    Staff,
    Site,
    Term,
    GradeLevel,
    Section,
    EnrollmentRecord,
    StaffSectionRecord,
    DailyAttendanceNode
)

"""
Entry point is a teacher or staff
Build everything that doesn't currently exist in order for current term:
- Staff
- Site
- Term
- GradeLevels 
- Sections
- StaffRecord
- Enrollment record
- DailyAttendnace node
"""


