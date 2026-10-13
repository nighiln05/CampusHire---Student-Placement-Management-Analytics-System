import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, session, current_app
from werkzeug.utils import secure_filename
from . import login_required
from models import db, Document, Student
from services import S3Service

documents_bp = Blueprint('documents', __name__, url_prefix='/documents')

def allowed_file(filename):
    allowed_exts = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'docx', 'csv', 'xlsx', 'txt'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_exts

@documents_bp.route('/')
@login_required
def index():
    """List uploaded documents, resumes, and datasets."""
    type_filter = request.args.get('type', '').strip()
    search_query = request.args.get('q', '').strip()

    query = Document.query

    if type_filter:
        query = query.filter(Document.document_type == type_filter)

    if search_query:
        like_pattern = f"%{search_query}%"
        query = query.filter(
            (Document.file_name.ilike(like_pattern)) |
            (Document.document_code.ilike(like_pattern)) |
            (Document.uploaded_by.ilike(like_pattern))
        )

    documents = query.order_by(Document.uploaded_at.desc(), Document.id.desc()).all()
    students = Student.query.order_by(Student.name.asc()).all()
    doc_types = ['Resume', 'Placement Report', 'Company Document', 'Dataset']
    is_s3_ready = S3Service.is_s3_configured()
    s3_bucket = current_app.config.get('S3_BUCKET_NAME', '')

    return render_template(
        'documents/index.html',
        documents=documents,
        students=students,
        doc_types=doc_types,
        selected_type=type_filter,
        search_query=search_query,
        is_s3_ready=is_s3_ready,
        s3_bucket=s3_bucket
    )

@documents_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    """Handle document/resume upload to AWS S3 (or local fallback)."""
    if 'file' not in request.files:
        flash('No file selected for upload.', 'danger')
        return redirect(url_for('documents.index'))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('documents.index'))

    if not allowed_file(file.filename):
        flash('File format not supported. Allowed formats: PDF, DOCX, CSV, XLSX, TXT.', 'warning')
        return redirect(url_for('documents.index'))

    doc_type = request.form.get('document_type', 'Resume')
    student_id = request.form.get('student_id')
    uploaded_by = session.get('user_name', 'Placement Coordinator')

    # Get file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    # Max upload limit check (16MB)
    max_limit = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
    if file_size > max_limit:
        flash(f'File exceeds the maximum upload limit of {max_limit // (1024*1024)}MB.', 'danger')
        return redirect(url_for('documents.index'))

    original_name = secure_filename(file.filename) or 'document'
    extension = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else 'dat'

    # Folder mapping
    folder_map = {
        'Resume': 'resumes',
        'Placement Report': 'reports',
        'Company Document': 'company_docs',
        'Dataset': 'datasets'
    }
    folder = folder_map.get(doc_type, 'documents')

    try:
        # Upload to AWS S3 (or local storage if S3 bucket not configured)
        s3_key, storage_backend = S3Service.upload_file(file, original_name, folder=folder)

        total_docs = Document.query.count() + 101
        doc_code = f"DOC-2024-{total_docs}"

        doc_record = Document(
            document_code=doc_code,
            file_name=original_name,
            s3_key=s3_key,
            file_type=extension,
            file_size=file_size,
            document_type=doc_type,
            student_id=int(student_id) if student_id and student_id != '' else None,
            uploaded_by=uploaded_by,
            storage_backend=storage_backend
        )
        db.session.add(doc_record)
        db.session.commit()

        if storage_backend == 'S3':
            flash(f'File "{original_name}" successfully uploaded to Amazon S3 ({s3_key})! Reference saved in database.', 'success')
        else:
            flash(f'File "{original_name}" saved to Local Storage ({s3_key}). Configure S3_BUCKET_NAME in .env to stream directly to AWS S3.', 'info')

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error uploading file: {e}")
        flash(f'Upload failed: {str(e)}', 'danger')

    return redirect(request.referrer or url_for('documents.index'))

@documents_bp.route('/<int:doc_id>/download')
@login_required
def download(doc_id):
    """Download document via Amazon S3 Presigned URL or local file stream."""
    doc = Document.query.get_or_404(doc_id)

    if doc.storage_backend == 'S3':
        presigned_url = S3Service.generate_download_url(doc.s3_key, storage_backend='S3')
        if presigned_url:
            return redirect(presigned_url)

    # Local fallback
    local_path = S3Service.get_local_file_path(doc.s3_key)
    if local_path.exists():
        return send_file(str(local_path), as_attachment=True, download_name=doc.file_name)

    flash('The requested file is currently unavailable or was not found in storage.', 'danger')
    return redirect(url_for('documents.index'))

@documents_bp.route('/<int:doc_id>/delete', methods=['POST'])
@login_required
def delete(doc_id):
    """Delete document and remove object from storage."""
    doc = Document.query.get_or_404(doc_id)
    file_name = doc.file_name
    s3_key = doc.s3_key
    storage = doc.storage_backend

    try:
        S3Service.delete_file(s3_key, storage_backend=storage)
        db.session.delete(doc)
        db.session.commit()
        flash(f'Document "{file_name}" removed from database and storage.', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting document: {str(e)}', 'danger')

    return redirect(url_for('documents.index'))
