import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask
from config import Config
from models import db

def init_database():
    """Initializes the database by dropping and creating all tables."""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        print(f"[*] Connecting to database at: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print("[*] Creating all database tables...")
        db.create_all()
        print("[+] Database tables successfully created!")

if __name__ == '__main__':
    init_database()
