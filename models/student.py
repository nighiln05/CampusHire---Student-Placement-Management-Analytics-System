from datetime import datetime
from . import db

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    department = db.Column(db.String(100), nullable=False, default='Artificial Intelligence & Data Science')
    batch = db.Column(db.String(20), nullable=False, default='2023')
    graduation_year = db.Column(db.Integer, nullable=False, default=2025)
    cgpa = db.Column(db.Float, nullable=False, default=8.0)
    skills = db.Column(db.Text, nullable=True)  # Comma-separated or tags
    placement_status = db.Column(db.String(30), default='Unplaced')  # 'Placed', 'Unplaced', 'In-Process'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    applications = db.relationship('Application', back_populates='student', cascade='all, delete-orphan')
    placement = db.relationship('Placement', back_populates='student', uselist=False, cascade='all, delete-orphan')
    documents = db.relationship('Document', back_populates='student', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'department': self.department,
            'batch': self.batch,
            'graduation_year': self.graduation_year,
            'cgpa': self.cgpa,
            'skills': self.skills,
            'placement_status': self.placement_status,
            'applications_count': len(self.applications),
            'has_placement': bool(self.placement)
        }

    def __repr__(self):
        return f"<Student {self.student_id} - {self.name}>"
