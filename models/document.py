from datetime import datetime
from . import db

class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    document_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    file_name = db.Column(db.String(255), nullable=False)
    s3_key = db.Column(db.String(500), nullable=False, index=True)  # Object key reference in Amazon S3
    file_type = db.Column(db.String(50), nullable=False)  # Extension or MIME type (e.g., pdf, csv, docx)
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    document_type = db.Column(
        db.String(50), 
        default='Resume'
    )  # 'Resume', 'Placement Report', 'Company Document', 'Dataset'
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='SET NULL'), nullable=True)
    uploaded_by = db.Column(db.String(100), default='Placement Coordinator')
    storage_backend = db.Column(db.String(20), default='S3')  # 'S3' or 'Local' (for graceful offline fallback)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    student = db.relationship('Student', back_populates='documents')

    @property
    def formatted_size(self):
        """Returns human-readable file size."""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def to_dict(self):
        return {
            'id': self.id,
            'document_code': self.document_code,
            'file_name': self.file_name,
            's3_key': self.s3_key,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'formatted_size': self.formatted_size,
            'document_type': self.document_type,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else None,
            'uploaded_by': self.uploaded_by,
            'storage_backend': self.storage_backend,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }

    def __repr__(self):
        return f"<Document {self.document_code} - {self.file_name}>"
