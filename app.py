import os
from flask import Flask, render_template, redirect, url_for, session
from config import Config
from models import db

def create_app(config_class=Config):
    """Application factory for CampusPlacements."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure uploads folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.students import students_bp
    from routes.companies import companies_bp
    from routes.jobs import jobs_bp
    from routes.applications import applications_bp
    from routes.interviews import interviews_bp
    from routes.placements import placements_bp
    from routes.documents import documents_bp
    from routes.analytics import analytics_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(companies_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(applications_bp)
    app.register_blueprint(interviews_bp)
    app.register_blueprint(placements_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(analytics_bp)

    # Global context processor
    @app.context_processor
    def inject_global_vars():
        return {
            'app_name': 'CampusPlacements',
            'current_user': session.get('user_name', None),
            'current_role': session.get('user_role', None),
            's3_bucket': app.config.get('S3_BUCKET_NAME', '')
        }

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    return app

app = create_app()

if __name__ == '__main__':
    # Default port 5000, accessible on all interfaces
    app.run(host='0.0.0.0', port=5000, debug=True)
