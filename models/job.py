from datetime import datetime
from . import db

class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    job_type = db.Column(db.String(50), default='Full-Time')  # 'Full-Time', 'Internship', 'Placement+Intern'
    location = db.Column(db.String(100), nullable=False)
    min_cgpa = db.Column(db.Float, default=6.5)
    required_skills = db.Column(db.Text, nullable=True)
    salary_ctc = db.Column(db.Float, nullable=False)  # Stored in LPA (e.g., 12.5) for quantitative analytics
    deadline = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default='Open')  # 'Open', 'Closed', 'Completed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = db.relationship('Company', back_populates='jobs')
    applications = db.relationship('Application', back_populates='job', cascade='all, delete-orphan')
    placements = db.relationship('Placement', back_populates='job')

    def to_dict(self):
        return {
            'id': self.id,
            'job_code': self.job_code,
            'company_id': self.company_id,
            'company_name': self.company.name if self.company else 'N/A',
            'title': self.title,
            'job_type': self.job_type,
            'location': self.location,
            'min_cgpa': self.min_cgpa,
            'required_skills': self.required_skills,
            'salary_ctc': self.salary_ctc,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'status': self.status,
            'applications_count': len(self.applications)
        }

    def __repr__(self):
        return f"<Job {self.job_code} - {self.title}>"
