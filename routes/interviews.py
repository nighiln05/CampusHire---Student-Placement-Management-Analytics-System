from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import login_required
from models import db, InterviewRound, Application

interviews_bp = Blueprint('interviews', __name__, url_prefix='/interviews')

@interviews_bp.route('/')
@login_required
def index():
    """List all interview rounds with filters by result and round type."""
    result_filter = request.args.get('result', '').strip()
    type_filter = request.args.get('type', '').strip()
    search_query = request.args.get('q', '').strip()

    query = InterviewRound.query

    if result_filter:
        query = query.filter(InterviewRound.result == result_filter)

    if type_filter:
        query = query.filter(InterviewRound.round_type == type_filter)

    if search_query:
        like_pattern = f"%{search_query}%"
        query = query.join(Application).filter(
            (InterviewRound.interview_code.ilike(like_pattern)) |
            (InterviewRound.interviewer.ilike(like_pattern)) |
            (InterviewRound.remarks.ilike(like_pattern))
        )

    interviews = query.order_by(InterviewRound.round_date.desc(), InterviewRound.id.desc()).all()
    round_types = ['Aptitude', 'Technical', 'HR', 'Group Discussion', 'Managerial']
    results = ['Pending', 'Passed', 'Failed']

    return render_template(
        'interviews/index.html',
        interviews=interviews,
        round_types=round_types,
        results=results,
        selected_result=result_filter,
        selected_type=type_filter,
        search_query=search_query
    )

@interviews_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Schedule a new interview round for an application."""
    app_id = request.args.get('app_id')
    application = None
    if app_id:
        application = Application.query.get(int(app_id))

    applications = Application.query.filter(
        Application.status.in_(['Shortlisted', 'Assessment', 'Interview'])
    ).all()

    if request.method == 'POST':
        target_app_id = request.form.get('application_id')
        round_type = request.form.get('round_type')
        round_number = request.form.get('round_number', '1')
        date_str = request.form.get('round_date', '')
        interviewer = request.form.get('interviewer', '').strip()
        result = request.form.get('result', 'Pending')
        remarks = request.form.get('remarks', '').strip()

        if not target_app_id or not round_type:
            flash('Please select an Application and Round Type.', 'danger')
            return render_template('interviews/form.html', applications=applications, preselected_app=application)

        round_date = datetime.now()
        if date_str:
            try:
                round_date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                try:
                    round_date = datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    pass

        total_int = InterviewRound.query.count() + 101
        int_code = f"INT-{total_int}"

        try:
            round_obj = InterviewRound(
                interview_code=int_code,
                application_id=int(target_app_id),
                round_number=int(round_number),
                round_type=round_type,
                round_date=round_date,
                interviewer=interviewer,
                result=result,
                remarks=remarks
            )
            db.session.add(round_obj)
            
            # Update application status to Interview if not already
            app_to_update = Application.query.get(int(target_app_id))
            if app_to_update and app_to_update.status in ['Applied', 'Shortlisted', 'Assessment']:
                app_to_update.status = 'Interview'

            db.session.commit()
            flash(f'Interview round ({round_type}) scheduled successfully!', 'success')
            return redirect(url_for('applications.detail', app_id=target_app_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error scheduling interview: {str(e)}', 'danger')

    return render_template('interviews/form.html', applications=applications, preselected_app=application)

@interviews_bp.route('/<int:interview_id>/update', methods=['POST'])
@login_required
def update(interview_id):
    """Update result and remarks for an interview round."""
    interview = InterviewRound.query.get_or_404(interview_id)
    new_result = request.form.get('result')
    new_remarks = request.form.get('remarks', '').strip()

    if new_result in ['Pending', 'Passed', 'Failed']:
        interview.result = new_result
    if new_remarks:
        interview.remarks = new_remarks

    try:
        db.session.commit()
        flash(f'Interview round {interview.interview_code} updated to {interview.result}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating interview: {str(e)}', 'danger')

    return redirect(request.referrer or url_for('interviews.index'))
