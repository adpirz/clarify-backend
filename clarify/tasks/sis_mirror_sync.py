

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