from sqlalchemy import func, case, extract
from models import db, Student, Company, Job, Application, Placement, InterviewRound

class AnalyticsService:
    """Computes placement and recruitment metrics for the BDA analytics engine."""

    @staticmethod
    def get_dashboard_summary():
        """Returns key KPI counts for the executive dashboard."""
        total_students = db.session.query(func.count(Student.id)).scalar() or 0
        total_companies = db.session.query(func.count(Company.id)).scalar() or 0
        active_jobs = db.session.query(func.count(Job.id)).filter(Job.status == 'Open').scalar() or 0
        total_applications = db.session.query(func.count(Application.id)).scalar() or 0
        
        placed_students = db.session.query(func.count(Student.id)).filter(
            Student.placement_status == 'Placed'
        ).scalar() or 0
        
        placement_rate = round((placed_students / total_students * 100), 1) if total_students > 0 else 0.0
        
        avg_ctc = db.session.query(func.avg(Placement.ctc)).filter(
            Placement.status == 'Active'
        ).scalar()
        avg_ctc = round(float(avg_ctc), 2) if avg_ctc else 0.0

        highest_ctc = db.session.query(func.max(Placement.ctc)).filter(
            Placement.status == 'Active'
        ).scalar()
        highest_ctc = round(float(highest_ctc), 2) if highest_ctc else 0.0

        return {
            'total_students': total_students,
            'total_companies': total_companies,
            'active_jobs': active_jobs,
            'total_applications': total_applications,
            'placed_students': placed_students,
            'placement_rate': placement_rate,
            'avg_ctc': avg_ctc,
            'highest_ctc': highest_ctc
        }

    @staticmethod
    def get_analytics_metrics(filters=None):
        """
        Executes real-time analytical queries with optional multi-dimensional filters:
        filters = {'department': '...', 'graduation_year': '...', 'company_id': '...', 'job_id': '...'}
        Returns all 10 Big Data Analytics metrics.
        """
        filters = filters or {}
        dept_filter = filters.get('department')
        year_filter = filters.get('graduation_year')
        company_id_filter = filters.get('company_id')
        job_id_filter = filters.get('job_id')

        # -------------------------------------------------------------
        # 1. & 9. Overall Placement Status & Rate (Placed vs Unplaced)
        # -------------------------------------------------------------
        student_query = db.session.query(
            Student.placement_status, 
            func.count(Student.id)
        )
        if dept_filter:
            student_query = student_query.filter(Student.department == dept_filter)
        if year_filter:
            try:
                student_query = student_query.filter(Student.graduation_year == int(year_filter))
            except (ValueError, TypeError):
                pass
        
        status_counts = dict(student_query.group_by(Student.placement_status).all())
        placed_count = status_counts.get('Placed', 0)
        unplaced_count = status_counts.get('Unplaced', 0)
        in_process_count = status_counts.get('In-Process', 0)
        total_students = placed_count + unplaced_count + in_process_count
        placement_rate = round((placed_count / total_students * 100), 1) if total_students > 0 else 0.0

        placed_vs_unplaced = {
            'labels': ['Placed', 'In-Process', 'Unplaced'],
            'data': [placed_count, in_process_count, unplaced_count]
        }

        # -------------------------------------------------------------
        # 2. Department-wise Placement
        # -------------------------------------------------------------
        dept_query = db.session.query(
            Student.department,
            func.count(Student.id).label('total'),
            func.sum(case((Student.placement_status == 'Placed', 1), else_=0)).label('placed')
        )
        if year_filter:
            try:
                dept_query = dept_query.filter(Student.graduation_year == int(year_filter))
            except (ValueError, TypeError):
                pass
        
        dept_results = dept_query.group_by(Student.department).all()
        dept_labels = [r[0] for r in dept_results]
        dept_total = [int(r[1]) for r in dept_results]
        dept_placed = [int(r[2] or 0) for r in dept_results]

        department_placements = {
            'labels': dept_labels,
            'total': dept_total,
            'placed': dept_placed
        }

        # -------------------------------------------------------------
        # 3. Company-wise Placements
        # -------------------------------------------------------------
        comp_plc_query = db.session.query(
            Company.name,
            func.count(Placement.id).label('placements_count')
        ).join(Placement, Company.id == Placement.company_id)

        if dept_filter:
            comp_plc_query = comp_plc_query.join(Student, Placement.student_id == Student.id).filter(
                Student.department == dept_filter
            )
        if year_filter:
            comp_plc_query = comp_plc_query.join(Student, Placement.student_id == Student.id).filter(
                Student.graduation_year == int(year_filter)
            )
        if company_id_filter:
            try:
                comp_plc_query = comp_plc_query.filter(Company.id == int(company_id_filter))
            except (ValueError, TypeError):
                pass

        comp_plc_results = comp_plc_query.group_by(Company.name).order_by(
            func.count(Placement.id).desc()
        ).limit(10).all()

        company_placements = {
            'labels': [r[0] for r in comp_plc_results],
            'data': [int(r[1]) for r in comp_plc_results]
        }

        # -------------------------------------------------------------
        # 4. Applications by Company
        # -------------------------------------------------------------
        app_comp_query = db.session.query(
            Company.name,
            func.count(Application.id).label('apps_count')
        ).join(Application, Company.id == Application.company_id)

        if dept_filter:
            app_comp_query = app_comp_query.join(Student, Application.student_id == Student.id).filter(
                Student.department == dept_filter
            )
        if year_filter:
            app_comp_query = app_comp_query.join(Student, Application.student_id == Student.id).filter(
                Student.graduation_year == int(year_filter)
            )

        app_comp_results = app_comp_query.group_by(Company.name).order_by(
            func.count(Application.id).desc()
        ).limit(10).all()

        applications_by_company = {
            'labels': [r[0] for r in app_comp_results],
            'data': [int(r[1]) for r in app_comp_results]
        }

        # -------------------------------------------------------------
        # 5. Applications by Month (Time-series Trend)
        # -------------------------------------------------------------
        # Works universally across SQLite and MySQL
        app_date_query = db.session.query(
            Application.application_date,
            func.count(Application.id)
        )
        if dept_filter:
            app_date_query = app_date_query.join(Student, Application.student_id == Student.id).filter(
                Student.department == dept_filter
            )
        if company_id_filter:
            try:
                app_date_query = app_date_query.filter(Application.company_id == int(company_id_filter))
            except (ValueError, TypeError):
                pass

        app_dates = app_date_query.group_by(Application.application_date).all()
        # Group by YYYY-MM in python for portability
        month_map = {}
        for dt, count in app_dates:
            if dt:
                m_key = dt.strftime('%b %Y')
                month_map[m_key] = month_map.get(m_key, 0) + count

        applications_by_month = {
            'labels': list(month_map.keys()) if month_map else ['No Data'],
            'data': list(month_map.values()) if month_map else [0]
        }

        # -------------------------------------------------------------
        # 6. Application Status Distribution
        # -------------------------------------------------------------
        status_query = db.session.query(
            Application.status,
            func.count(Application.id)
        )
        if dept_filter:
            status_query = status_query.join(Student, Application.student_id == Student.id).filter(
                Student.department == dept_filter
            )
        if company_id_filter:
            try:
                status_query = status_query.filter(Application.company_id == int(company_id_filter))
            except (ValueError, TypeError):
                pass
        
        app_status_res = status_query.group_by(Application.status).all()
        application_status_dist = {
            'labels': [r[0] for r in app_status_res],
            'data': [int(r[1]) for r in app_status_res]
        }

        # -------------------------------------------------------------
        # 7. Average CTC by Department
        # -------------------------------------------------------------
        avg_ctc_dept_query = db.session.query(
            Student.department,
            func.avg(Placement.ctc).label('avg_ctc')
        ).join(Placement, Student.id == Placement.student_id).filter(
            Placement.status == 'Active'
        )
        if year_filter:
            try:
                avg_ctc_dept_query = avg_ctc_dept_query.filter(Student.graduation_year == int(year_filter))
            except (ValueError, TypeError):
                pass

        avg_ctc_dept_res = avg_ctc_dept_query.group_by(Student.department).all()
        avg_ctc_by_dept = {
            'labels': [r[0] for r in avg_ctc_dept_res],
            'data': [round(float(r[1]), 2) for r in avg_ctc_dept_res]
        }

        # -------------------------------------------------------------
        # 8. Average CTC by Company
        # -------------------------------------------------------------
        avg_ctc_comp_query = db.session.query(
            Company.name,
            func.avg(Placement.ctc).label('avg_ctc')
        ).join(Placement, Company.id == Placement.company_id).filter(
            Placement.status == 'Active'
        )
        if dept_filter:
            avg_ctc_comp_query = avg_ctc_comp_query.join(Student, Placement.student_id == Student.id).filter(
                Student.department == dept_filter
            )

        avg_ctc_comp_res = avg_ctc_comp_query.group_by(Company.name).order_by(
            func.avg(Placement.ctc).desc()
        ).limit(10).all()

        avg_ctc_by_company = {
            'labels': [r[0] for r in avg_ctc_comp_res],
            'data': [round(float(r[1]), 2) for r in avg_ctc_comp_res]
        }

        # -------------------------------------------------------------
        # 10. On-Campus vs Off-Campus Placements
        # -------------------------------------------------------------
        type_query = db.session.query(
            Placement.placement_type,
            func.count(Placement.id)
        ).filter(Placement.status == 'Active')

        if dept_filter:
            type_query = type_query.join(Student, Placement.student_id == Student.id).filter(
                Student.department == dept_filter
            )

        type_res = type_query.group_by(Placement.placement_type).all()
        type_dict = dict(type_res)
        on_campus_vs_off_campus = {
            'labels': ['On-campus', 'Off-campus'],
            'data': [type_dict.get('On-campus', 0), type_dict.get('Off-campus', 0)]
        }

        return {
            'placement_rate': placement_rate,
            'total_students': total_students,
            'placed_students': placed_count,
            'unplaced_students': unplaced_count,
            'department_placements': department_placements,
            'company_placements': company_placements,
            'applications_by_company': applications_by_company,
            'applications_by_month': applications_by_month,
            'application_status_dist': application_status_dist,
            'avg_ctc_by_dept': avg_ctc_by_dept,
            'avg_ctc_by_company': avg_ctc_by_company,
            'placed_vs_unplaced': placed_vs_unplaced,
            'on_campus_vs_off_campus': on_campus_vs_off_campus
        }
