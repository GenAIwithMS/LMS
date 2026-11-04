from src.db import db, pakistan_time


class ExamTerm(db.Model):
    """An exam of a session, like "First Term" or "Final" of 2026-27.

    After marks_deadline (or once the admin locks the term) marks can't be changed.
    Students see their report cards only after the admin publishes the term.
    """
    __tablename__ = 'exam_terms'
    __table_args__ = (db.UniqueConstraint('session_id', 'name', name='uq_exam_term_session_name'),)
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    session_id = db.Column(db.BigInteger, db.ForeignKey('academic_sessions.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    marks_deadline = db.Column(db.Date, nullable=True)
    is_locked = db.Column(db.Boolean, nullable=False, default=False)
    is_published = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=pakistan_time)

    session = db.relationship('AcademicSession', lazy=True)


class ExamPaper(db.Model):
    """One subject's paper in a term, for every section of that subject's class.

    question_status: none (nothing uploaded), submitted (waiting for the admin),
    approved, or returned (the admin sent it back with a note).
    """
    __tablename__ = 'exam_papers'
    __table_args__ = (db.UniqueConstraint('term_id', 'subject_id', name='uq_exam_paper_term_subject'),)
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    term_id = db.Column(db.BigInteger, db.ForeignKey('exam_terms.id'), nullable=False)
    class_id = db.Column(db.BigInteger, db.ForeignKey('school_classes.id'), nullable=False)
    subject_id = db.Column(db.BigInteger, db.ForeignKey('subjects.id'), nullable=False)
    total_marks = db.Column(db.Numeric(5, 2), nullable=False, default=100)
    passing_marks = db.Column(db.Numeric(5, 2), nullable=False, default=33)
    exam_date = db.Column(db.Date, nullable=True)
    question_file = db.Column(db.String(255), nullable=True)
    question_status = db.Column(db.String(20), nullable=False, default='none')
    review_note = db.Column(db.Text, nullable=True)
    uploaded_by = db.Column(db.BigInteger, db.ForeignKey('teachers.id'), nullable=True)

    term = db.relationship('ExamTerm', backref='papers', lazy=True)
    school_class = db.relationship('SchoolClass', lazy=True)
    subject = db.relationship('Subject', lazy=True)
    uploader = db.relationship('Teacher', lazy=True)


class ExamMark(db.Model):
    """One student's marks in one paper. section_id is the student's section when the
    marks were entered, so old report cards stay right after students are promoted."""
    __tablename__ = 'exam_marks'
    __table_args__ = (db.UniqueConstraint('paper_id', 'student_id', name='uq_exam_mark_paper_student'),)
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    paper_id = db.Column(db.BigInteger, db.ForeignKey('exam_papers.id'), nullable=False)
    student_id = db.Column(db.BigInteger, db.ForeignKey('students.id'), nullable=False)
    section_id = db.Column(db.BigInteger, db.ForeignKey('sections.id'), nullable=False)
    obtained_marks = db.Column(db.Numeric(5, 2), nullable=True)
    is_absent = db.Column(db.Boolean, nullable=False, default=False)
    entered_by = db.Column(db.BigInteger, db.ForeignKey('teachers.id'), nullable=True)
    entered_at = db.Column(db.DateTime, default=pakistan_time, onupdate=pakistan_time)

    paper = db.relationship('ExamPaper', backref='marks', lazy=True)
    student = db.relationship('Student', lazy=True)


class ReportRemark(db.Model):
    """The class incharge's remarks on a student's report card for a term."""
    __tablename__ = 'report_remarks'
    __table_args__ = (db.UniqueConstraint('term_id', 'student_id', name='uq_report_remark_term_student'),)
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    term_id = db.Column(db.BigInteger, db.ForeignKey('exam_terms.id'), nullable=False)
    student_id = db.Column(db.BigInteger, db.ForeignKey('students.id'), nullable=False)
    remarks = db.Column(db.Text, nullable=False)
    written_by = db.Column(db.BigInteger, db.ForeignKey('teachers.id'), nullable=True)
    updated_at = db.Column(db.DateTime, default=pakistan_time, onupdate=pakistan_time)
