from .announcement import AnnouncementSchema, UpdateAnnouncementSchema
from .assignment_submission import AssignmentSubmissionSchema, UpdateAssignmentSubmissionSchema
from .assignment import assignmentSchema, UpdateAssignmentSchema
from .attendance import AttendanceSchema,UpdateAttendanceSchema
from .auth_schema import RegisterAdminSchema, RegisterTeacherSchema,RegisterStudentSchema,UpdateTeacherSchema,UpdateStudentSchema,loginSchema,UpdateMyUsernameSchema,ChangeMyPasswordSchema
from .course import CourseSchema, UpdateCourseSchema
from .enrollment import EnrollmentSchema,UpdateEnrollmentSchema
from .event import EventSchema,UpdateEventSchema
from .result import ResultSchema, UpdateResultSchema
from .section import SectionSchema,UpdateSectionSchema
from .subject import subjectSchema,UpdateSubjectSchema

__all__ = ["AnnouncementSchema","UpdateAnnouncementSchema","AssignmentSubmissionSchema","UpdateAssignmentSubmissionSchema","assignmentSchema","UpdateAssignmentSchema","AttendanceSchema","UpdateAttendanceSchema", "RegisterAdminSchema","RegisterTeacherSchema","RegisterStudentSchema","UpdateTeacherSchema","UpdateStudentSchema","loginSchema","UpdateMyUsernameSchema","ChangeMyPasswordSchema","CourseSchema","UpdateCourseSchema","EnrollmentSchema","UpdateEnrollmentSchema","EventSchema","UpdateEventSchema","ResultSchema","UpdateResultSchema","SectionSchema","UpdateSectionSchema", "subjectSchema","UpdateSubjectSchema"]
from .school import ClassSectionSchema, UpdateClassSectionSchema, SubjectTeacherSchema, ClassSubjectSchema, ChapterSchema, UpdateChapterSchema, AcademicSessionSchema, TeacherSubjectSchema
from .teaching import (DailyAttendanceSchema, ChapterProgressSchema, DiaryEntrySchema, ClassTestSchema,
                       UpdateClassTestSchema, ClassTestMarksSchema, TimetableSlotSchema, TimetableSettingsSchema)
from .exam import (ExamTermSchema, UpdateExamTermSchema, ClassPapersSchema, UpdatePaperSchema, PaperReviewSchema,
                   PaperMarksSchema, ReportRemarksSchema, PromotionSchema, GradeScaleSchema)
