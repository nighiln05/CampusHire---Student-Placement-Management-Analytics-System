from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import login_required
from models import db, Job, Company, Application

jobs_bp = Blueprint('jobs', __name__, url_prefix='/jobs')

@jobs_bp.route('/')
@login_required
def index():
    """List job opportunities with search and status filters."""
    search_query = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()
    company_filter = request.args.get('company_id', '').strip()

    query = Job.query

    if search_query:
        like_pattern = f"%{search_query}%"
        query = query.filter(
            (Job.title.ilike(like_pattern)) |
            (Job.job_code.ilike(like_pattern)) |
            (Job.required_skills.ilike(like_pattern)) |
            (Job.location.ilike(like_pattern))
        )

    if status_filter:
        query = query.filter(Job.status == status_filter)

    if company_filter:
        try:
            query = query.filter(Job.company_id == int(company_filter))
        except (ValueError, TypeError):
            pass

    jobs = query.order_by(Job.id.desc()).all()
    companies = Company.query.order_by(Company.name.asc()).all()

    return render_template(
        'jobs/index.html',
        jobs=jobs,
        companies=companies,
        search_query=search_query,
        selected_status=status_filter,
        selected_company=company_filter
    )

@jobs_bp.route('/<int:job_id>')
@login_required
def detail(job_id):
    """View job opening details and applicants."""
    job = Job.query.get_or_404(job_id)
    applications = Application.query.filter_by(job_id=job.id).order_by(Application.application_date.desc()).all()
    return render_template('jobs/detail.html', job=job, applications=applications)

@jobs_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Create a new job opportunity."""
    companies = Company.query.order_by(Company.name.asc()).all()

    if request.method == 'POST':
        company_id = request.form.get('company_id')
        job_code = request.form.get('job_code', '').strip().upper()
        title = request.form.get('title', '').strip()
        job_type = request.form.get('job_type', 'Full-Time')
        location = request.form.get('location', '').strip()
        min_cgpa = request.form.get('min_cgpa', '6.0')
        salary_ctc = request.form.get('salary_ctc', '0')
        deadline_str = request.form.get('deadline', '').strip()
        required_skills = request.form.get('required_skills', '').strip()
        description = request.form.get('description', '').strip()
        status = request.form.get('status', 'Open')

        if not company_id or not job_code or not title or not location:
            flash('Please fill in Company, Job Code, Title, and Location.', 'danger')
            return render_template('jobs/form.html', job=None, companies=companies)

        if Job.query.filter_by(job_code=job_code).first():
            flash(f'Job Code "{job_code}" already exists.', 'warning')
            return render_template('jobs/form.html', job=None, companies=companies)

        deadline = None
        if deadline_str:
            try:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        try:
            job = Job(
                company_id=int(company_id),
                job_code=job_code,
                title=title,
                job_type=job_type,
                location=location,
                min_cgpa=float(min_cgpa),
                salary_ctc=float(salary_ctc),
                deadline=deadline,
                required_skills=required_skills,
                description=description,
                status=status
            )
            db.session.add(job)
            db.session.commit()
            flash(f'Job opportunity "{title}" posted successfully!', 'success')
            return redirect(url_for('jobs.detail', job_id=job.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error posting job: {str(e)}', 'danger')

    return render_template('jobs/form.html', job=None, companies=companies)

@jobs_bp.route('/<int:job_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(job_id):
    """Edit job details."""
    job = Job.query.get_or_404(job_id)
    companies = Company.query.order_by(Company.name.asc()).all()

    if request.method == 'POST':
        job.company_id = int(request.form.get('company_id', job.company_id))
        job.title = request.form.get('title', '').strip()
        job.job_type = request.form.get('job_type', job.job_type)
        job.location = request.form.get('location', '').strip()
        job.min_cgpa = float(request.form.get('min_cgpa', job.min_cgpa))
        job.salary_ctc = float(request.form.get('salary_ctc', job.salary_ctc))
        deadline_str = request.form.get('deadline', '').strip()
        if deadline_str:
            try:
                job.deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        job.required_skills = request.form.get('required_skills', '').strip()
        job.description = request.form.get('description', '').strip()
        job.status = request.form.get('status', job.status)

        try:
            db.session.commit()
            flash(f'Job "{job.title}" updated successfully!', 'success')
            return redirect(url_for('jobs.detail', job_id=job.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating job: {str(e)}', 'danger')

    return render_template('jobs/form.html', job=job, companies=companies)

@jobs_bp.route('/<int:job_id>/delete', methods=['POST'])
@login_required
def delete(job_id):
    """Delete a job opportunity."""
    job = Job.query.get_or_404(job_id)
    title = job.title
    try:
        db.session.delete(job)
        db.session.commit()
        flash(f'Job "{title}" deleted.', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting job: {str(e)}', 'danger')

    return redirect(url_for('jobs.index'))
