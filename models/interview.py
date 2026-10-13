from datetime import datetime
from . import db

class InterviewRound(db.Model):
    __tablename__ = 'interview_rounds'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    interview_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id', ondelete='CASCADE'), nullable=False)
    round_number = db.Column(db.Integer, default=1)
    round_type = db.Column(
        db.String(50), 
        nullable=False
    )  # 'Aptitude', 'Technical', 'HR', 'Group Discussion', 'Managerial'
    round_date = db.Column(db.DateTime, default=datetime.utcnow)
    interviewer = db.Column(db.String(100), nullable=True)
    result = db.Column(db.String(30), default='Pending')  # 'Pending', 'Passed', 'Failed'
    remarks = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    application = db.relationship('Application', back_populates='interview_rounds')

    def to_dict(self):
        return {
            'id': self.id,
            'interview_code': self.interview_code,
            'application_id': self.application_id,
            'student_name': self.application.student.name if self.application and self.application.student else 'N/A',
            'company_name': self.application.company.name if self.application and self.application.company else 'N/A',
            'job_title': self.application.job.title if self.application and self.application.job else 'N/A',
            'round_number': self.round_number,
            'round_type': self.round_type,
            'round_date': self.round_date.isoformat() if self.round_date else None,
            'interviewer': self.interviewer,
            'result': self.result,
            'remarks': self.remarks
        }

    def __repr__(self):
        return f"<InterviewRound {self.interview_code} (Round {self.round_number}: {self.round_type})>"
