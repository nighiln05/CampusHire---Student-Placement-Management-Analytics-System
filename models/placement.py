from datetime import datetime
from . import db

class Placement(db.Model):
    __tablename__ = 'placements'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    placement_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    # Unique constraint ensures a student can only hold ONE primary/active placement record
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), unique=True, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    placement_date = db.Column(db.Date, default=datetime.utcnow)
    ctc = db.Column(db.Float, nullable=False)  # Stored in LPA (e.g., 14.5)
    placement_type = db.Column(db.String(50), default='On-campus')  # 'On-campus', 'Off-campus'
    status = db.Column(db.String(30), default='Active')  # 'Active', 'Declined'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = db.relationship('Student', back_populates='placement')
    company = db.relationship('Company', back_populates='placements')
    job = db.relationship('Job', back_populates='placements')

    def to_dict(self):
        return {
            'id': self.id,
            'placement_code': self.placement_code,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else 'N/A',
            'department': self.student.department if self.student else 'N/A',
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else 'N/A',
            'job_id': self.job_id,
            'job_title': self.job.title if self.job else 'N/A',
            'placement_date': self.placement_date.isoformat() if self.placement_date else None,
            'ctc': self.ctc,
            'placement_type': self.placement_type,
            'status': self.status
        }

    def __repr__(self):
        return f"<Placement {self.placement_code} - {self.student_id}>"
