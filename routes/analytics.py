from flask import Blueprint, render_template, request, jsonify
from . import login_required
from models import db, Student, Company, Job
from services import AnalyticsService

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/')
@login_required
def index():
    """Renders the Big Data Analytics dashboard page."""
    departments = [d[0] for d in db.session.query(Student.department).distinct().all()]
    grad_years = [y[0] for y in db.session.query(Student.graduation_year).distinct().order_by(Student.graduation_year.asc()).all()]
    companies = Company.query.order_by(Company.name.asc()).all()
    jobs = Job.query.order_by(Job.title.asc()).all()

    summary = AnalyticsService.get_dashboard_summary()

    return render_template(
        'analytics/index.html',
        departments=departments,
        grad_years=grad_years,
        companies=companies,
        jobs=jobs,
        summary=summary
    )

@analytics_bp.route('/api/data')
@login_required
def api_data():
    """Returns dynamic Chart.js JSON dataset for all 10 BDA analytics metrics with active filters."""
    filters = {
        'department': request.args.get('department'),
        'graduation_year': request.args.get('graduation_year'),
        'company_id': request.args.get('company_id'),
        'job_id': request.args.get('job_id')
    }
    # Clean empty strings
    filters = {k: v for k, v in filters.items() if v and v.strip()}

    metrics = AnalyticsService.get_analytics_metrics(filters)
    return jsonify(metrics)
