from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import login_required
from models import db, Company, Job, Application, Placement

companies_bp = Blueprint('companies', __name__, url_prefix='/companies')

@companies_bp.route('/')
@login_required
def index():
    """List and search partner companies."""
    search_query = request.args.get('q', '').strip()
    query = Company.query

    if search_query:
        like_pattern = f"%{search_query}%"
        query = query.filter(
            (Company.name.ilike(like_pattern)) |
            (Company.industry.ilike(like_pattern)) |
            (Company.location.ilike(like_pattern))
        )

    companies = query.order_by(Company.name.asc()).all()
    return render_template('companies/index.html', companies=companies, search_query=search_query)

@companies_bp.route('/<int:company_id>')
@login_required
def detail(company_id):
    """View company profile with active jobs, applications, and placements."""
    company = Company.query.get_or_404(company_id)
    jobs = Job.query.filter_by(company_id=company.id).order_by(Job.created_at.desc()).all()
    applications = Application.query.filter_by(company_id=company.id).order_by(Application.application_date.desc()).all()
    placements = Placement.query.filter_by(company_id=company.id).order_by(Placement.placement_date.desc()).all()
    selected_count = sum(1 for a in applications if a.status == 'Selected')

    return render_template(
        'companies/detail.html',
        company=company,
        jobs=jobs,
        applications=applications,
        placements=placements,
        selected_count=selected_count
    )

@companies_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Register a new partner company."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        industry = request.form.get('industry', '').strip()
        location = request.form.get('location', '').strip()
        website = request.form.get('website', '').strip()
        hr_name = request.form.get('hr_contact_name', '').strip()
        hr_email = request.form.get('hr_contact_email', '').strip()
        hr_phone = request.form.get('hr_contact_phone', '').strip()
        description = request.form.get('description', '').strip()

        if not name or not industry or not location:
            flash('Please provide Company Name, Industry, and Location.', 'danger')
            return render_template('companies/form.html', company=None)

        if Company.query.filter_by(name=name).first():
            flash(f'Company "{name}" is already registered.', 'warning')
            return render_template('companies/form.html', company=None)

        try:
            company = Company(
                name=name,
                industry=industry,
                location=location,
                website=website,
                hr_contact_name=hr_name,
                hr_contact_email=hr_email,
                hr_contact_phone=hr_phone,
                description=description
            )
            db.session.add(company)
            db.session.commit()
            flash(f'Company {name} registered successfully!', 'success')
            return redirect(url_for('companies.detail', company_id=company.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Failed to register company: {str(e)}', 'danger')

    return render_template('companies/form.html', company=None)

@companies_bp.route('/<int:company_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(company_id):
    """Update company profile."""
    company = Company.query.get_or_404(company_id)

    if request.method == 'POST':
        company.industry = request.form.get('industry', '').strip()
        company.location = request.form.get('location', '').strip()
        company.website = request.form.get('website', '').strip()
        company.hr_contact_name = request.form.get('hr_contact_name', '').strip()
        company.hr_contact_email = request.form.get('hr_contact_email', '').strip()
        company.hr_contact_phone = request.form.get('hr_contact_phone', '').strip()
        company.description = request.form.get('description', '').strip()

        try:
            db.session.commit()
            flash(f'Company {company.name} profile updated!', 'success')
            return redirect(url_for('companies.detail', company_id=company.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Failed to update company: {str(e)}', 'danger')

    return render_template('companies/form.html', company=company)

@companies_bp.route('/<int:company_id>/delete', methods=['POST'])
@login_required
def delete(company_id):
    """Delete company record."""
    company = Company.query.get_or_404(company_id)
    name = company.name
    try:
        db.session.delete(company)
        db.session.commit()
        flash(f'Company {name} deleted.', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to delete company: {str(e)}', 'danger')

    return redirect(url_for('companies.index'))
