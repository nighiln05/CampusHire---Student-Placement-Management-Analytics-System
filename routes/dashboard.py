from flask import Blueprint, render_template, jsonify
from . import login_required
from services import AnalyticsService
from models import Application, InterviewRound, Placement, Student

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    """Main executive dashboard overview."""
    summary = AnalyticsService.get_dashboard_summary()

    # Recent applications (latest 6)
    recent_applications = Application.query.order_by(
        Application.application_date.desc(), 
        Application.id.desc()
    ).limit(6).all()

    # Upcoming / Recent interview rounds (latest 5)
    recent_interviews = InterviewRound.query.order_by(
        InterviewRound.round_date.desc(), 
        InterviewRound.id.desc()
    ).limit(5).all()

    # Recent placements (latest 5)
    recent_placements = Placement.query.order_by(
        Placement.placement_date.desc(), 
        Placement.id.desc()
    ).limit(5).all()

    return render_template(
        'dashboard/index.html',
        summary=summary,
        recent_applications=recent_applications,
        recent_interviews=recent_interviews,
        recent_placements=recent_placements
    )

@dashboard_bp.route('/api/dashboard-charts')
@login_required
def dashboard_charts_api():
    """Returns dynamic Chart.js JSON data for the 4 core dashboard charts."""
    metrics = AnalyticsService.get_analytics_metrics()
    return jsonify({
        'applications_by_month': metrics['applications_by_month'],
        'department_placements': metrics['department_placements'],
        'company_placements': metrics['company_placements'],
        'application_status_dist': metrics['application_status_dist']
    })
