import os
from pathlib import Path
from dotenv import load_dotenv

# Base project directory
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env if present
load_dotenv(BASE_DIR / '.env')

class Config:
    """Base application configuration class."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-dev-secret-key-campusplacements-2024')
    
    # Database Configuration:
    # If DATABASE_URL is not set or empty, defaults to local SQLite file database
    # For RDS MySQL, set DATABASE_URL=mysql+pymysql://<user>:<password>@<rds_host>:3306/<dbname>
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        f"sqlite:///{BASE_DIR / 'campusplacements.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # AWS S3 Configuration
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', '')
    
    # Optional credentials for local testing without IAM
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', None)
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', None)
    
    # Upload settings
    UPLOAD_FOLDER = BASE_DIR / os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16 MB max
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'csv', 'xlsx', 'txt'}
