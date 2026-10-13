from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import login_required
from models import db, Placement, Student, Company, Job

placements_bp = Blueprint('placements', __name__, url_prefix='/placements')

@placements_bp.route('/')
@login_required
def index():
    """List all placement records with filters for type and search."""
    search_query = request.args.get('q', '').strip()
    type_filter = request.args.get('type', '').strip()
    company_filter = request.args.get('company_id', '').strip()

    query = Placement.query.filter_by(status='Active')

    if search_query:
        like_pattern = f"%{search_query}%"
        query = query.join(Student).join(Company).join(Job).filter(
            (Placement.placement_code.ilike(like_pattern)) |
            (Student.name.ilike(like_pattern)) |
            (Student.student_id.ilike(like_pattern)) |
            (Company.name.ilike(like_pattern)) |
            (Job.title.ilike(like_pattern))
        )

    if type_filter:
        query = query.filter(Placement.placement_type == type_filter)

    if company_filter:
        try:
            query = query.filter(Placement.company_id == int(company_filter))
        except (ValueError, TypeError):
            pass

    placements = query.order_by(Placement.placement_date.desc(), Placement.id.desc()).all()
    companies = Company.query.order_by(Company.name.asc()).all()

    return render_template(
        'placements/index.html',
        placements=placements,
        companies=companies,
        search_query=search_query,
        selected_type=type_filter,
        selected_company=company_filter
    )

@placements_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Manually add a placement record, preventing duplicates."""
    # List unplaced or in-process students
    students = Student.query.order_by(Student.name.asc()).all()
    companies = Company.query.order_by(Company.name.asc()).all()
    jobs = Job.query.filter_by(status='Open').order_by(Job.title.asc()).all()

    if request.method == 'POST':
        student_id = request.form.get('student_id')
        company_id = request.form.get('company_id')
        job_id = request.form.get('job_id')
        date_str = request.form.get('placement_date', '')
        ctc_str = request.form.get('ctc', '0')
        placement_type = request.form.get('placement_type', 'On-campus')

        if not student_id or not company_id or not job_id:
            flash('Please select Student, Company, and Job.', 'danger')
            return render_template('placements/form.html', students=students, companies=companies, jobs=jobs)

        # PREVENT DUPLICATE ACTIVE PLACEMENT RECORD FOR THE SAME STUDENT
        existing_active = Placement.query.filter_by(
            student_id=int(student_id), 
            status='Active'
        ).first()

        if existing_active:
            flash(
                f'Error: This student already holds an active placement at {existing_active.company.name} ({existing_active.placement_code}). A student cannot hold duplicate active placements.',
                'danger'
            )
            return render_template('placements/form.html', students=students, companies=companies, jobs=jobs)

        p_date = date.today()
        if date_str:
            try:
                p_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        total_plc = Placement.query.count() + 101
        plc_code = f"PLC-2024-{total_plc}"

        try:
            placement = Placement(
                placement_code=plc_code,
                student_id=int(student_id),
                company_id=int(company_id),
                job_id=int(job_id),
                placement_date=p_date,
                ctc=float(ctc_str),
                placement_type=placement_type,
                status='Active'
            )
            db.session.add(placement)

            # Update student status to Placed
            stu = Student.query.get(int(student_id))
            if stu:
                stu.placement_status = 'Placed'

            db.session.commit()
            flash(f'Placement record {plc_code} successfully registered!', 'success')
            return redirect(url_for('placements.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Failed to register placement: {str(e)}', 'danger')

    return render_template('placements/form.html', students=students, companies=companies, jobs=jobs)

@placements_bp.route('/<int:placement_id>/revoke', methods=['POST'])
@login_required
def revoke(placement_id):
    """Revokes or declines a placement record and resets student status."""
    placement = Placement.query.get_or_404(placement_id)
    student = placement.student
    try:
        placement.status = 'Declined'
        if student:
            student.placement_status = 'Unplaced'
        db.session.commit()
        flash(f'Placement record {placement.placement_code} marked as Declined.', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Error revoking placement: {str(e)}', 'danger')

    return redirect(url_for('placements.index'))
