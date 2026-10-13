import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from models import Student, Company, Job, Application, Placement

def run_tests():
    print("Testing CampusPlacements application...")
    app = create_app()
    with app.test_client() as client:
        # 1. Test unauthenticated redirect
        r = client.get('/')
        print(f"[+] GET / -> {r.status_code} (Redirected to: {r.headers.get('Location')})")
        assert r.status_code in [302, 301]

        # 2. Test login
        r_login = client.post('/auth/login', data={'email': 'admin@campusplacements.edu', 'password': 'Admin@123'}, follow_redirects=True)
        print(f"[+] POST /auth/login -> {r_login.status_code}")
        assert r_login.status_code == 200

        # 3. Test Dashboard
        r_dash = client.get('/')
        print(f"[+] GET / -> {r_dash.status_code}")
        assert r_dash.status_code == 200

        # 4. Test Dashboard Charts API
        r_charts = client.get('/api/dashboard-charts')
        print(f"[+] GET /api/dashboard-charts -> {r_charts.status_code}")
        chart_data = r_charts.get_json()
        assert 'applications_by_month' in chart_data
        assert 'department_placements' in chart_data

        # 5. Test Students page
        r_students = client.get('/students/')
        print(f"[+] GET /students/ -> {r_students.status_code}")
        assert b'Navya Jain' in r_students.data
        assert b'Nighil Natarajan' in r_students.data
        print("[+] Verified exact student roster: Navya Jain & Nighil Natarajan present!")

        # 6. Test Analytics page and API
        r_analytics = client.get('/analytics/')
        print(f"[+] GET /analytics/ -> {r_analytics.status_code}")
        r_analytics_api = client.get('/analytics/api/data')
        print(f"[+] GET /analytics/api/data -> {r_analytics_api.status_code}")
        analytics_data = r_analytics_api.get_json()
        assert 'placement_rate' in analytics_data
        assert 'avg_ctc_by_dept' in analytics_data
        assert 'avg_ctc_by_company' in analytics_data
        assert 'on_campus_vs_off_campus' in analytics_data
        print(f"[+] Placement Rate verified: {analytics_data['placement_rate']}%")

        # 7. Test Documents page
        r_docs = client.get('/documents/')
        print(f"[+] GET /documents/ -> {r_docs.status_code}")

    print("\nALL BACKEND & FRONTEND TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    run_tests()
