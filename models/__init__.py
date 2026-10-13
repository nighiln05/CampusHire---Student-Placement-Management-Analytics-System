from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .student import Student
from .company import Company
from .job import Job
from .application import Application
from .interview import InterviewRound
from .placement import Placement
from .document import Document

__all__ = [
    'db',
    'User',
    'Student',
    'Company',
    'Job',
    'Application',
    'InterviewRound',
    'Placement',
    'Document'
]
