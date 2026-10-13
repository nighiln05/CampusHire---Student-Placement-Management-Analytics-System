from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import login_required
from models import db, Application, Student, Job, Company, InterviewRound, Placement

applications_bp = Blueprint('applications', __name__, url_prefix='/applications')

@applications_bp.route('/')
@login_required
def index():
    """List applications with search, status filters, and company filters."""
    search_query = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()
    company_filter = request.args.get('company_id', '').strip()

    query = Application.query

    if search_query:
        like_pattern = f"%{search_query}%"
        query = query.join(Student).join(Job).join(Company).filter(
            (Application.application_code.ilike(like_pattern)) |
            (Student.name.ilike(like_pattern)) |
            (Student.student_id.ilike(like_pattern)) |
            (Job.title.ilike(like_pattern)) |
            (Company.name.ilike(like_pattern))
        )

    if status_filter:
        query = query.filter(Application.status == status_filter)

    if company_filter:
        try:
            query = query.filter(Application.company_id == int(company_filter))
        except (ValueError, TypeError):
            pass

    applications = query.order_by(Application.application_date.desc(), Application.id.desc()).all()
    companies = Company.query.order_by(Company.name.asc()).all()

    statuses = ['Applied', 'Shortlisted', 'Assessment', 'Interview', 'Selected', 'Rejected', 'Withdrawn']

    return render_template(
        'applications/index.html',
        applications=applications,
        companies=companies,
        statuses=statuses,
        search_query=search_query,
        selected_status=status_filter,
        selected_company=company_filter
    )

@applications_bp.route('/<int:app_id>')
@login_required
def detail(app_id):
    """View application details and interview history."""
    application = Application.query.get_or_404(app_id)
    interview_rounds = InterviewRound.query.filter_by(application_id=application.id).order_by(InterviewRound.round_number.asc()).all()
    placement = Placement.query.filter_by(student_id=application.student_id, company_id=application.company_id).first()
    statuses = ['Applied', 'Shortlisted', 'Assessment', 'Interview', 'Selected', 'Rejected', 'Withdrawn']

    return render_template(
        'applications/detail.html',
        application=application,
        interview_rounds=interview_rounds,
        placement=placement,
        statuses=statuses
    )

@applications_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Submit a new student application."""
    students = Student.query.order_by(Student.name.asc()).all()
    jobs = Job.query.filter_by(status='Open').order_by(Job.title.asc()).all()

    if request.method == 'POST':
        student_id = request.form.get('student_id')
        job_id = request.form.get('job_id')
        app_date_str = request.form.get('application_date', '')
        status = request.form.get('status', 'Applied')
        remarks = request.form.get('remarks', '').strip()

        if not student_id or not job_id:
            flash('Please select both Student and Job Opening.', 'danger')
            return render_template('applications/form.html', students=students, jobs=jobs)

        student = Student.query.get(int(student_id))
        job = Job.query.get(int(job_id))

        if not student or not job:
            flash('Invalid student or job selection.', 'danger')
            return render_template('applications/form.html', students=students, jobs=jobs)

        # Check existing application for this student + job
        existing = Application.query.filter_by(student_id=student.id, job_id=job.id).first()
        if existing:
            flash(f'{student.name} has already applied to {job.title} at {job.company.name}.', 'warning')
            return render_template('applications/form.html', students=students, jobs=jobs)

        # Generate unique code
        total_apps = Application.query.count() + 101
        app_code = f"APP-2024-{total_apps}"

        app_date = date.today()
        if app_date_str:
            try:
                app_date = datetime.strptime(app_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        try:
            application = Application(
                application_code=app_code,
                student_id=student.id,
                job_id=job.id,
                company_id=job.company_id,
                application_date=app_date,
                status=status,
                remarks=remarks
            )
            db.session.add(application)
            db.session.commit()
            flash(f'Application {app_code} created successfully for {student.name}!', 'success')
            return redirect(url_for('applications.detail', app_id=application.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating application: {str(e)}', 'danger')

    return render_template('applications/form.html', students=students, jobs=jobs)

@applications_bp.route('/<int:app_id>/update-status', methods=['POST'])
@login_required
def update_status(app_id):
    """Update pipeline status for an application."""
    application = Application.query.get_or_404(app_id)
    new_status = request.form.get('status')
    remarks = request.form.get('remarks', '').strip()

    valid_statuses = ['Applied', 'Shortlisted', 'Assessment', 'Interview', 'Selected', 'Rejected', 'Withdrawn']
    if new_status in valid_statuses:
        application.status = new_status
        if remarks:
            application.remarks = remarks
        
        # If Selected, check if placement record should be created or promoted
        if new_status == 'Selected':
            # Check if student already placed elsewhere
            existing_plc = Placement.query.filter_by(student_id=application.student_id, status='Active').first()
            if not existing_plc:
                total_plcs = Placement.query.count() + 101
                plc = Placement(
                    placement_code=f"PLC-2024-{total_plcs}",
                    student_id=application.student_id,
                    company_id=application.company_id,
                    job_id=application.job_id,
                    placement_date=date.today(),
                    ctc=application.job.salary_ctc,
                    placement_type='On-campus',
                    status='Active'
                )
                db.session.add(plc)
                application.student.placement_status = 'Placed'
                flash(f'Application marked as Selected and Placement record created automatically!', 'success')
            else:
                flash(f'Application marked as Selected. (Student already holds an active placement at {existing_plc.company.name}).', 'info')
        elif new_status == 'Rejected':
            # Check if student has other active placements
            active_other = Placement.query.filter_by(student_id=application.student_id, status='Active').first()
            if not active_other:
                # Check if other active apps exist
                other_active_apps = Application.query.filter(
                    Application.student_id == application.student_id,
                    Application.id != application.id,
                    Application.status.in_(['Shortlisted', 'Assessment', 'Interview'])
                ).first()
                application.student.placement_status = 'In-Process' if other_active_apps else 'Unplaced'
            flash(f'Application status updated to {new_status}.', 'warning')
        else:
            flash(f'Application status updated to {new_status}.', 'success')

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating status: {str(e)}', 'danger')

    return redirect(request.referrer or url_for('applications.detail', app_id=app_id))
