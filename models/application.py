from datetime import datetime
from . import db

class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    application_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    application_date = db.Column(db.Date, default=datetime.utcnow)
    status = db.Column(
        db.String(50), 
        default='Applied'
    )  # 'Applied', 'Shortlisted', 'Assessment', 'Interview', 'Selected', 'Rejected', 'Withdrawn'
    remarks = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = db.relationship('Student', back_populates='applications')
    job = db.relationship('Job', back_populates='applications')
    company = db.relationship('Company', back_populates='applications')
    interview_rounds = db.relationship('InterviewRound', back_populates='application', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'application_code': self.application_code,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else 'N/A',
            'job_id': self.job_id,
            'job_title': self.job.title if self.job else 'N/A',
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else 'N/A',
            'application_date': self.application_date.isoformat() if self.application_date else None,
            'status': self.status,
            'remarks': self.remarks,
            'rounds_count': len(self.interview_rounds)
        }

    def __repr__(self):
        return f"<Application {self.application_code} - {self.status}>"
