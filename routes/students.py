from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from . import login_required
from models import db, Student, Application, InterviewRound, Placement, Document

students_bp = Blueprint('students', __name__, url_prefix='/students')

@students_bp.route('/')
@login_required
def index():
    """List all students with search and filter capability."""
    search_query = request.args.get('q', '').strip()
    department_filter = request.args.get('department', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = Student.query

    if search_query:
        like_pattern = f"%{search_query}%"
        query = query.filter(
            (Student.name.ilike(like_pattern)) | 
            (Student.student_id.ilike(like_pattern)) | 
            (Student.email.ilike(like_pattern)) |
            (Student.skills.ilike(like_pattern))
        )

    if department_filter:
        query = query.filter(Student.department == department_filter)

    if status_filter:
        query = query.filter(Student.placement_status == status_filter)

    students = query.order_by(Student.id.asc()).all()

    # Distinct departments for the filter dropdown
    departments = [d[0] for d in db.session.query(Student.department).distinct().all()]

    return render_template(
        'students/index.html',
        students=students,
        departments=departments,
        search_query=search_query,
        selected_department=department_filter,
        selected_status=status_filter
    )

@students_bp.route('/<int:student_id>')
@login_required
def detail(student_id):
    """View complete profile for a student."""
    student = Student.query.get_or_404(student_id)
    applications = Application.query.filter_by(student_id=student.id).order_by(Application.application_date.desc()).all()
    placement = Placement.query.filter_by(student_id=student.id, status='Active').first()
    documents = Document.query.filter_by(student_id=student.id).order_by(Document.uploaded_at.desc()).all()
    
    # Gather interview rounds for this student across all applications
    app_ids = [a.id for a in applications]
    interviews = []
    if app_ids:
        interviews = InterviewRound.query.filter(
            InterviewRound.application_id.in_(app_ids)
        ).order_by(InterviewRound.round_date.desc()).all()

    return render_template(
        'students/detail.html',
        student=student,
        applications=applications,
        placement=placement,
        documents=documents,
        interviews=interviews
    )

@students_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Create a new student record."""
    if request.method == 'POST':
        student_id_val = request.form.get('student_id', '').strip().upper()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        department = request.form.get('department', '').strip()
        batch = request.form.get('batch', '').strip() or '2023'
        grad_year = request.form.get('graduation_year', '').strip()
        cgpa = request.form.get('cgpa', '').strip()
        skills = request.form.get('skills', '').strip()

        # Validation
        if not student_id_val or not name or not email or not department:
            flash('Please fill in all required fields (Roll ID, Name, Email, Department).', 'danger')
            return render_template('students/form.html', student=None)

        # Check uniqueness
        if Student.query.filter((Student.student_id == student_id_val) | (Student.email == email)).first():
            flash('Student ID or Email already exists in the system.', 'warning')
            return render_template('students/form.html', student=None)

        try:
            student = Student(
                student_id=student_id_val,
                name=name,
                email=email,
                phone=phone,
                department=department,
                batch=batch,
                graduation_year=int(grad_year) if grad_year else 2025,
                cgpa=float(cgpa) if cgpa else 0.0,
                skills=skills,
                placement_status='Unplaced'
            )
            db.session.add(student)
            db.session.commit()
            flash(f'Student {name} ({student_id_val}) registered successfully!', 'success')
            return redirect(url_for('students.detail', student_id=student.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding student: {str(e)}', 'danger')

    return render_template('students/form.html', student=None)

@students_bp.route('/<int:student_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(student_id):
    """Edit existing student details."""
    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        student.name = request.form.get('name', '').strip()
        student.phone = request.form.get('phone', '').strip()
        student.department = request.form.get('department', '').strip()
        student.batch = request.form.get('batch', '').strip()
        grad_year = request.form.get('graduation_year', '').strip()
        cgpa = request.form.get('cgpa', '').strip()
        student.skills = request.form.get('skills', '').strip()
        student.placement_status = request.form.get('placement_status', student.placement_status)

        if grad_year:
            student.graduation_year = int(grad_year)
        if cgpa:
            student.cgpa = float(cgpa)

        try:
            db.session.commit()
            flash(f'Student {student.name} updated successfully!', 'success')
            return redirect(url_for('students.detail', student_id=student.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Failed to update student: {str(e)}', 'danger')

    return render_template('students/form.html', student=student)

@students_bp.route('/<int:student_id>/delete', methods=['POST'])
@login_required
def delete(student_id):
    """Delete student record."""
    student = Student.query.get_or_404(student_id)
    name = student.name
    try:
        db.session.delete(student)
        db.session.commit()
        flash(f'Student {name} deleted successfully.', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to delete student: {str(e)}', 'danger')

    return redirect(url_for('students.index'))
