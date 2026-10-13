from datetime import datetime
from . import db

class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), unique=True, nullable=False, index=True)
    industry = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    website = db.Column(db.String(255), nullable=True)
    hr_contact_name = db.Column(db.String(100), nullable=True)
    hr_contact_email = db.Column(db.String(120), nullable=True)
    hr_contact_phone = db.Column(db.String(20), nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    jobs = db.relationship('Job', back_populates='company', cascade='all, delete-orphan')
    applications = db.relationship('Application', back_populates='company', cascade='all, delete-orphan')
    placements = db.relationship('Placement', back_populates='company', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'industry': self.industry,
            'location': self.location,
            'website': self.website,
            'hr_contact_name': self.hr_contact_name,
            'hr_contact_email': self.hr_contact_email,
            'hr_contact_phone': self.hr_contact_phone,
            'description': self.description,
            'jobs_count': len(self.jobs),
            'placements_count': len(self.placements)
        }

    def __repr__(self):
        return f"<Company {self.name}>"
