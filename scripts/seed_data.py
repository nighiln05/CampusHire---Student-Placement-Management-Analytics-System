import sys
import random
from datetime import datetime, date, timedelta
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask
from config import Config
from models import (
    db, User, Student, Company, Job, Application, 
    InterviewRound, Placement, Document
)

def seed_database():
    """Seeds the database with users, companies, jobs, exact 30 students, applications, interviews, and placements."""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        print("[*] Checking existing database tables...")
        db.create_all()

        # Clean existing data to allow idempotent re-seeding
        print("[*] Clearing previous records...")
        Document.query.delete()
        InterviewRound.query.delete()
        Placement.query.delete()
        Application.query.delete()
        Job.query.delete()
        Company.query.delete()
        Student.query.delete()
        User.query.delete()
        db.session.commit()

        # -------------------------------------------------------------
        # 1. Create Default Administrative Users
        # -------------------------------------------------------------
        print("[*] Creating administrative users...")
        admin = User(
            email='admin@campusplacements.edu',
            full_name='Chief Placement Officer',
            role='admin'
        )
        admin.set_password('Admin@123')

        coordinator = User(
            email='coordinator@campusplacements.edu',
            full_name='Placement Coordinator (AI&DS)',
            role='coordinator'
        )
        coordinator.set_password('Coord@123')

        db.session.add_all([admin, coordinator])
        db.session.commit()

        # -------------------------------------------------------------
        # 2. Create 10 Realistic Tech & Consulting Companies
        # -------------------------------------------------------------
        print("[*] Creating partner companies...")
        companies_data = [
            {
                'name': 'Amazon Web Services (AWS)',
                'industry': 'Cloud Computing & AI',
                'location': 'Bangalore, Karnataka',
                'website': 'https://aws.amazon.com',
                'hr_contact_name': 'Meera Sundaram',
                'hr_contact_email': 'meera.sundaram@amazon.com',
                'hr_contact_phone': '+91 98450 11223',
                'description': 'Global cloud platform leader offering compute, storage, databases, and generative AI services.'
            },
            {
                'name': 'Microsoft Corporation',
                'industry': 'Software & Cloud',
                'location': 'Hyderabad, Telangana',
                'website': 'https://www.microsoft.com',
                'hr_contact_name': 'Aditya Varma',
                'hr_contact_email': 'aditya.varma@microsoft.com',
                'hr_contact_phone': '+91 98450 22334',
                'description': 'Multinational technology powerhouse developing enterprise software, Azure cloud, and developer platforms.'
            },
            {
                'name': 'Zoho Corporation',
                'industry': 'SaaS & Enterprise Cloud',
                'location': 'Chennai, Tamil Nadu',
                'website': 'https://www.zoho.com',
                'hr_contact_name': 'Kavitha Ramesh',
                'hr_contact_email': 'kavitha.r@zohocorp.com',
                'hr_contact_phone': '+91 98450 33445',
                'description': 'Pioneering SaaS suite offering 50+ business applications with state-of-the-art engineering culture.'
            },
            {
                'name': 'Tata Consultancy Services (TCS)',
                'industry': 'IT Services & Consulting',
                'location': 'Chennai, Tamil Nadu',
                'website': 'https://www.tcs.com',
                'hr_contact_name': 'Rajesh Narayanan',
                'hr_contact_email': 'rajesh.n@tcs.com',
                'hr_contact_phone': '+91 98450 44556',
                'description': 'Global IT consulting leader offering digital transformation, AI solutions, and enterprise analytics.'
            },
            {
                'name': 'Infosys Limited',
                'industry': 'Digital Services & Consulting',
                'location': 'Bangalore, Karnataka',
                'website': 'https://www.infosys.com',
                'hr_contact_name': 'Sowmya Iyer',
                'hr_contact_email': 'sowmya.iyer@infosys.com',
                'hr_contact_phone': '+91 98450 55667',
                'description': 'Next-generation digital services and consulting enabling clients across 56 countries.'
            },
            {
                'name': 'Cognizant Technology Solutions',
                'industry': 'Enterprise Modernization',
                'location': 'Coimbatore, Tamil Nadu',
                'website': 'https://www.cognizant.com',
                'hr_contact_name': 'Karthik Balaji',
                'hr_contact_email': 'karthik.b@cognizant.com',
                'hr_contact_phone': '+91 98450 66778',
                'description': 'Global technology solutions provider engineering modern businesses and AI-powered workflows.'
            },
            {
                'name': 'Cisco Systems',
                'industry': 'Networking & Cybersecurity',
                'location': 'Bangalore, Karnataka',
                'website': 'https://www.cisco.com',
                'hr_contact_name': 'Priyanka Sen',
                'hr_contact_email': 'priyanka.sen@cisco.com',
                'hr_contact_phone': '+91 98450 77889',
                'description': 'Worldwide leader in networking hardware, cloud infrastructure, and enterprise cybersecurity.'
            },
            {
                'name': 'Thoughtworks',
                'industry': 'Software Consultancy & Agility',
                'location': 'Coimbatore, Tamil Nadu',
                'website': 'https://www.thoughtworks.com',
                'hr_contact_name': 'Arun Swaminathan',
                'hr_contact_email': 'arun.s@thoughtworks.com',
                'hr_contact_phone': '+91 98450 88990',
                'description': 'Global technology consultancy integrating strategy, design and software engineering.'
            },
            {
                'name': 'Accolite Digital',
                'industry': 'Digital Product Engineering',
                'location': 'Hyderabad, Telangana',
                'website': 'https://www.accolitedigital.com',
                'hr_contact_name': 'Deepa Nair',
                'hr_contact_email': 'deepa.nair@accolitedigital.com',
                'hr_contact_phone': '+91 98450 99001',
                'description': 'Best-in-class digital transformation company building high-impact platforms for Fortune 500 enterprises.'
            },
            {
                'name': 'Google Cloud (Alphabet)',
                'industry': 'Internet & Big Data Cloud',
                'location': 'Bangalore, Karnataka',
                'website': 'https://cloud.google.com',
                'hr_contact_name': 'Vikram Malhotra',
                'hr_contact_email': 'vikram.m@google.com',
                'hr_contact_phone': '+91 98450 00112',
                'description': 'World-class hyperscale cloud computing platform providing BigQuery, Vertex AI, and distributed data infrastructure.'
            }
        ]

        companies = []
        for c in companies_data:
            comp = Company(**c)
            db.session.add(comp)
            companies.append(comp)
        db.session.commit()

        # -------------------------------------------------------------
        # 3. Create 15 Realistic Job Postings
        # -------------------------------------------------------------
        print("[*] Creating job opportunities...")
        jobs_data = [
            # Amazon (ID: 1)
            {
                'job_code': 'JOB-AWS-001',
                'company_id': 1,
                'title': 'Cloud Support Associate - Big Data',
                'job_type': 'Full-Time',
                'location': 'Bangalore',
                'min_cgpa': 7.5,
                'required_skills': 'AWS, Linux, SQL, Big Data, Hadoop, Python',
                'salary_ctc': 18.0,
                'deadline': date(2024, 11, 30),
                'description': 'Troubleshoot and architect cloud-native big data pipelines and EMR clusters on AWS.',
                'status': 'Open'
            },
            {
                'job_code': 'JOB-AWS-002',
                'company_id': 1,
                'title': 'Software Development Engineer (SDE I)',
                'job_type': 'Full-Time',
                'location': 'Hyderabad',
                'min_cgpa': 8.0,
                'required_skills': 'Data Structures, Algorithms, Python, Java, Distributed Systems',
                'salary_ctc': 24.5,
                'deadline': date(2024, 11, 15),
                'description': 'Design, develop, test, and deploy resilient multi-tier microservices.',
                'status': 'Open'
            },
            # Microsoft (ID: 2)
            {
                'job_code': 'JOB-MS-001',
                'company_id': 2,
                'title': 'Software Engineer - Azure Cloud Data',
                'job_type': 'Full-Time',
                'location': 'Hyderabad',
                'min_cgpa': 8.0,
                'required_skills': 'C#, Python, Azure, SQL, Spark, Machine Learning',
                'salary_ctc': 22.0,
                'deadline': date(2024, 10, 31),
                'description': 'Scale hyperscale real-time streaming architectures across Azure infrastructure.',
                'status': 'Open'
            },
            {
                'job_code': 'JOB-MS-002',
                'company_id': 2,
                'title': 'Data Science & AI Intern',
                'job_type': 'Internship',
                'location': 'Bangalore',
                'min_cgpa': 8.5,
                'required_skills': 'Python, PyTorch, Statistics, NLP, Deep Learning',
                'salary_ctc': 12.0,
                'deadline': date(2024, 12, 15),
                'description': '6-month intern position focusing on generative AI and transformer models.',
                'status': 'Open'
            },
            # Zoho (ID: 3)
            {
                'job_code': 'JOB-ZOHO-001',
                'company_id': 3,
                'title': 'Member Technical Staff - Analytics',
                'job_type': 'Full-Time',
                'location': 'Chennai',
                'min_cgpa': 7.0,
                'required_skills': 'Java, Python, C++, Data Analytics, Relational DBs',
                'salary_ctc': 8.5,
                'deadline': date(2024, 10, 20),
                'description': 'Build high performance data warehousing and business intelligence engines for Zoho Analytics.',
                'status': 'Open'
            },
            {
                'job_code': 'JOB-ZOHO-002',
                'company_id': 3,
                'title': 'Frontend / Full-Stack Engineer',
                'job_type': 'Full-Time',
                'location': 'Tenkasi / Chennai',
                'min_cgpa': 6.8,
                'required_skills': 'JavaScript, HTML5, CSS3, React, RESTful APIs',
                'salary_ctc': 7.5,
                'deadline': date(2024, 11, 10),
                'description': 'Craft responsive, intuitive user interfaces for modern web applications.',
                'status': 'Open'
            },
            # TCS (ID: 4)
            {
                'job_code': 'JOB-TCS-001',
                'company_id': 4,
                'title': 'TCS Digital - AI & Big Data Engineer',
                'job_type': 'Full-Time',
                'location': 'Chennai / Pan-India',
                'min_cgpa': 7.0,
                'required_skills': 'Python, SQL, Machine Learning, Tableau, Cloud Basics',
                'salary_ctc': 7.2,
                'deadline': date(2024, 10, 25),
                'description': 'Premier tier engineering role working on cutting-edge AI and data modernization initiatives.',
                'status': 'Open'
            },
            {
                'job_code': 'JOB-TCS-002',
                'company_id': 4,
                'title': 'TCS Ninja - Systems Engineer',
                'job_type': 'Full-Time',
                'location': 'Coimbatore / Chennai',
                'min_cgpa': 6.0,
                'required_skills': 'Java, Python, DBMS, Problem Solving',
                'salary_ctc': 3.6,
                'deadline': date(2024, 9, 30),
                'description': 'Entry-level systems engineering role across diverse enterprise client projects.',
                'status': 'Completed'
            },
            # Infosys (ID: 5)
            {
                'job_code': 'JOB-INF-001',
                'company_id': 5,
                'title': 'Specialist Programmer (Power Programmer)',
                'job_type': 'Full-Time',
                'location': 'Bangalore',
                'min_cgpa': 7.5,
                'required_skills': 'Competitive Programming, Algorithms, Python, Spring Boot',
                'salary_ctc': 9.5,
                'deadline': date(2024, 11, 25),
                'description': 'High-performance coding role tackling complex distributed architecture challenges.',
                'status': 'Open'
            },
            # Cognizant (ID: 6)
            {
                'job_code': 'JOB-CTS-001',
                'company_id': 6,
                'title': 'GenC Elevate - Data Specialist',
                'job_type': 'Full-Time',
                'location': 'Coimbatore',
                'min_cgpa': 6.5,
                'required_skills': 'SQL, Python, PowerBI, Cloud Fundamentals',
                'salary_ctc': 4.5,
                'deadline': date(2024, 10, 15),
                'description': 'Hands-on enterprise data transformation and visualization role.',
                'status': 'Closed'
            },
            # Cisco (ID: 7)
            {
                'job_code': 'JOB-CSCO-001',
                'company_id': 7,
                'title': 'Network & Cloud Security Software Engineer',
                'job_type': 'Full-Time',
                'location': 'Bangalore',
                'min_cgpa': 8.0,
                'required_skills': 'Python, Computer Networks, Linux, Go, Cryptography',
                'salary_ctc': 17.5,
                'deadline': date(2024, 12, 1),
                'description': 'Develop automated threat prevention and secure cloud networking protocols.',
                'status': 'Open'
            },
            # Thoughtworks (ID: 8)
            {
                'job_code': 'JOB-TW-001',
                'company_id': 8,
                'title': 'Graduate Consultant - Data Engineering',
                'job_type': 'Full-Time',
                'location': 'Coimbatore',
                'min_cgpa': 7.2,
                'required_skills': 'Clean Code, TDD, Spark, Python, Data Modeling',
                'salary_ctc': 11.5,
                'deadline': date(2024, 11, 20),
                'description': 'Practice extreme programming, clean architecture and modern data engineering.',
                'status': 'Open'
            },
            # Accolite (ID: 9)
            {
                'job_code': 'JOB-ACC-001',
                'company_id': 9,
                'title': 'Associate Software Engineer',
                'job_type': 'Full-Time',
                'location': 'Hyderabad',
                'min_cgpa': 7.0,
                'required_skills': 'C++, Java, Python, SQL, REST APIs',
                'salary_ctc': 6.5,
                'deadline': date(2024, 10, 28),
                'description': 'Build robust financial services and fintech applications.',
                'status': 'Open'
            },
            # Google Cloud (ID: 10)
            {
                'job_code': 'JOB-GCP-001',
                'company_id': 10,
                'title': 'Cloud Solution Associate - AI/ML',
                'job_type': 'Full-Time',
                'location': 'Bangalore',
                'min_cgpa': 8.5,
                'required_skills': 'Google Cloud, TensorFlow, BigQuery, Python, MLOps',
                'salary_ctc': 28.0,
                'deadline': date(2024, 12, 10),
                'description': 'Architect ML pipelines and intelligent analytics on Google Cloud Platform.',
                'status': 'Open'
            },
            {
                'job_code': 'JOB-GCP-002',
                'company_id': 10,
                'title': 'Data Engineering Intern',
                'job_type': 'Internship',
                'location': 'Bangalore',
                'min_cgpa': 8.0,
                'required_skills': 'Python, SQL, Apache Beam, BigQuery, Dataflow',
                'salary_ctc': 15.0,
                'deadline': date(2024, 12, 20),
                'description': 'Design scalable batch and streaming pipelines for real-time analytics.',
                'status': 'Open'
            }
        ]

        jobs = []
        for j in jobs_data:
            job_obj = Job(**j)
            db.session.add(job_obj)
            jobs.append(job_obj)
        db.session.commit()

        # -------------------------------------------------------------
        # 4. Insert Exact 30 Students: AI & DS – B, Batch 2023
        # -------------------------------------------------------------
        print("[*] Seeding the exact 30 student records (AI & DS - B, Batch 2023)...")
        student_names = [
            "Navya Jain",
            "Nighil Natarajan",
            "Nikhilesh H",
            "Nithilan M",
            "Nithyasri Damodaran",
            "Pavithra Rajindra",
            "Pavithra T A",
            "Pradeepaa M",
            "Prahalad M",
            "Prajesh Raam H S",
            "Pranaav A",
            "Pranav B",
            "Prem Danasekaran",
            "R Dhanvanyaa",
            "R Sai Sreya",
            "R Saran Shankar",
            "R Sathya Narayanan",
            "Raghav",
            "Raghunandan A",
            "Ramana K S",
            "Reya Shelena V",
            "Rithani R G",
            "Ritika S",
            "Ritu Nandhan D S",
            "Robin Manuel R",
            "Rohith Kanna S",
            "S K Karisma",
            "S Meghna",
            "S Rahul Karthik",
            "S S Manikanta Suryadevara"
        ]

        # Skill bank for realistic AI & DS students
        skills_pool = [
            "Python, Machine Learning, Deep Learning, SQL, PyTorch",
            "Python, AWS, Big Data, Hadoop, Spark, Tableau",
            "Python, Data Science, NLP, OpenCV, Docker",
            "Java, Python, Data Structures, Flask, PostgreSQL",
            "Python, Statistics, Scikit-learn, PowerBI, Pandas",
            "C++, Python, Cloud Computing, Kubernetes, Linux",
            "Python, Generative AI, LLMs, HuggingFace, FastAPI",
            "Python, R, Data Mining, Apache Kafka, MongoDB"
        ]

        students = []
        for i, name in enumerate(student_names, start=1):
            # Email generation: first name + roll suffix
            clean_first = name.split()[0].lower().replace('.', '')
            roll_code = f"23AD{i:03d}"
            
            # Realistic CGPA distribution between 7.5 and 9.7
            cgpa = round(7.4 + ((i * 7) % 24) / 10.0, 2)
            if cgpa > 9.8:
                cgpa = 9.4
            
            # Initial placement status
            # We will finalize placed/in-process status in the application/placement step
            stu = Student(
                student_id=roll_code,
                name=name,
                email=f"{clean_first}.{roll_code.lower()}@campus.edu",
                phone=f"+91 9840{i:02d} {1000 + i * 111}",
                department='Artificial Intelligence & Data Science',
                batch='2023',
                graduation_year=2025,
                cgpa=cgpa,
                skills=skills_pool[i % len(skills_pool)],
                placement_status='Unplaced'
            )
            db.session.add(stu)
            students.append(stu)
        
        # Add 6 cross-department students for multi-department comparative analytics
        extra_students_data = [
            ("Anand Kumar", "23CS001", "Computer Science & Engineering", 8.8, "Java, Microservices, Spring Boot, MySQL"),
            ("Deepika Venkatesh", "23CS002", "Computer Science & Engineering", 9.1, "C++, Systems Programming, Linux, Docker"),
            ("Gowtham Raj", "23CS003", "Computer Science & Engineering", 7.9, "React, Node.js, TypeScript, AWS"),
            ("Harini S", "23IT001", "Information Technology", 8.4, "Python, Django, AWS Cloud, PostgreSQL"),
            ("Kiran Chandran", "23IT002", "Information Technology", 8.2, "Data Analytics, Tableau, SQL, Spark"),
            ("Monisha P", "23IT003", "Information Technology", 7.8, "Network Security, Python, Cryptography")
        ]
        for name, roll_code, dept, cgpa, skills in extra_students_data:
            clean_first = name.split()[0].lower()
            stu = Student(
                student_id=roll_code,
                name=name,
                email=f"{clean_first}.{roll_code.lower()}@campus.edu",
                phone=f"+91 9789{len(students):02d} 5544",
                department=dept,
                batch='2023',
                graduation_year=2025,
                cgpa=cgpa,
                skills=skills,
                placement_status='Unplaced'
            )
            db.session.add(stu)
            students.append(stu)

        db.session.commit()

        # -------------------------------------------------------------
        # 5. Create 50+ Applications across Students and Jobs
        # -------------------------------------------------------------
        print("[*] Generating student applications and recruitment pipelines...")
        app_counter = 100
        applications = []

        # Handcrafted high-profile applications for top students to ensure realism
        # E.g. Nighil Natarajan (Student 2) applied to AWS, Google, Microsoft
        priority_apps = [
            (students[1], jobs[0], 'Selected'),   # Nighil Natarajan -> AWS Cloud Support
            (students[1], jobs[13], 'Shortlisted'), # Nighil Natarajan -> Google Cloud AI
            (students[0], jobs[2], 'Selected'),   # Navya Jain -> Microsoft Azure
            (students[2], jobs[4], 'Selected'),   # Nikhilesh H -> Zoho MTS
            (students[3], jobs[6], 'Selected'),   # Nithilan M -> TCS Digital
            (students[4], jobs[10], 'Selected'),  # Nithyasri Damodaran -> Cisco Security
            (students[5], jobs[11], 'Selected'),  # Pavithra Rajindra -> Thoughtworks
            (students[6], jobs[8], 'Selected'),   # Pavithra T A -> Infosys Power Programmer
            (students[7], jobs[12], 'Selected'),  # Pradeepaa M -> Accolite
            (students[8], jobs[0], 'Interview'),  # Prahalad M -> AWS
            (students[9], jobs[1], 'Selected'),   # Prajesh Raam H S -> AWS SDE I
            (students[10], jobs[4], 'Selected'),  # Pranaav A -> Zoho MTS
            (students[11], jobs[6], 'Selected'),  # Pranav B -> TCS Digital
            (students[12], jobs[8], 'Selected'),  # Prem Danasekaran -> Infosys
            (students[13], jobs[11], 'Selected'), # R Dhanvanyaa -> Thoughtworks
            (students[14], jobs[2], 'Selected'),  # R Sai Sreya -> Microsoft
            (students[15], jobs[10], 'Interview'),# R Saran Shankar -> Cisco
            (students[16], jobs[6], 'Selected'),  # R Sathya Narayanan -> TCS Digital
            (students[17], jobs[4], 'Selected'),  # Raghav -> Zoho
            (students[18], jobs[12], 'Selected'), # Raghunandan A -> Accolite
            (students[19], jobs[0], 'Assessment'),# Ramana K S -> AWS
            (students[20], jobs[6], 'Selected'),  # Reya Shelena V -> TCS Digital
            (students[21], jobs[8], 'Selected'),  # Rithani R G -> Infosys
            (students[22], jobs[4], 'Selected'),  # Ritika S -> Zoho
            (students[23], jobs[1], 'Interview'), # Ritu Nandhan D S -> AWS SDE
            (students[24], jobs[6], 'Selected'),  # Robin Manuel R -> TCS Digital
            (students[25], jobs[12], 'Selected'), # Rohith Kanna S -> Accolite
            (students[26], jobs[5], 'Selected'),  # S K Karisma -> Zoho Full-Stack
            (students[27], jobs[11], 'Interview'),# S Meghna -> Thoughtworks
            (students[28], jobs[6], 'Selected'),  # S Rahul Karthik -> TCS Digital
            (students[29], jobs[2], 'Selected'),  # S S Manikanta Suryadevara -> Microsoft
            # Extra students
            (students[30], jobs[1], 'Selected'),  # Anand Kumar (CSE) -> AWS SDE
            (students[31], jobs[2], 'Selected'),  # Deepika (CSE) -> Microsoft
            (students[33], jobs[6], 'Selected'),  # Harini (IT) -> TCS
        ]

        created_pairs = set()
        for stu, job_obj, target_status in priority_apps:
            app_counter += 1
            app_date = date(2024, 8, 1) + timedelta(days=(app_counter % 60))
            app = Application(
                application_code=f"APP-2024-{app_counter}",
                student_id=stu.id,
                job_id=job_obj.id,
                company_id=job_obj.company_id,
                application_date=app_date,
                status=target_status,
                remarks=f"Application reviewed and cleared for {target_status} status."
            )
            db.session.add(app)
            applications.append(app)
            created_pairs.add((stu.id, job_obj.id))

        # Fill in secondary applications across students to reach 55+ total applications
        extra_statuses = ['Applied', 'Shortlisted', 'Assessment', 'Interview', 'Rejected', 'Withdrawn']
        random.seed(42)
        for stu in students[:30]:
            # Each student has 1 or 2 more applications to other companies
            candidate_jobs = [j for j in jobs if (stu.id, j.id) not in created_pairs and stu.cgpa >= j.min_cgpa]
            if candidate_jobs:
                selected_sample = random.sample(candidate_jobs, min(2, len(candidate_jobs)))
                for c_job in selected_sample:
                    app_counter += 1
                    stat = random.choice(extra_statuses)
                    app_date = date(2024, 8, 10) + timedelta(days=(app_counter % 50))
                    app = Application(
                        application_code=f"APP-2024-{app_counter}",
                        student_id=stu.id,
                        job_id=c_job.id,
                        company_id=c_job.company_id,
                        application_date=app_date,
                        status=stat,
                        remarks=f"Candidate profile submitted for {c_job.title}."
                    )
                    db.session.add(app)
                    applications.append(app)
                    created_pairs.add((stu.id, c_job.id))

        db.session.commit()

        # -------------------------------------------------------------
        # 6. Create Multi-Round Interviews for Applications
        # -------------------------------------------------------------
        print("[*] Creating multi-stage interview rounds...")
        interview_counter = 100
        for app in applications:
            if app.status in ['Interview', 'Selected']:
                # Round 1: Aptitude or Technical
                interview_counter += 1
                r1 = InterviewRound(
                    interview_code=f"INT-{interview_counter}",
                    application_id=app.id,
                    round_number=1,
                    round_type='Technical' if app.student.cgpa >= 8.5 else 'Aptitude',
                    round_date=datetime.combine(app.application_date + timedelta(days=7), datetime.min.time()),
                    interviewer=f"Senior Evaluator ({app.company.name})",
                    result='Passed',
                    remarks='Excellent problem-solving logic and core algorithmic fundamentals.'
                )
                db.session.add(r1)

                # Round 2: Technical / Coding
                interview_counter += 1
                r2 = InterviewRound(
                    interview_code=f"INT-{interview_counter}",
                    application_id=app.id,
                    round_number=2,
                    round_type='Technical',
                    round_date=datetime.combine(app.application_date + timedelta(days=12), datetime.min.time()),
                    interviewer=f"Engineering Lead ({app.company.name})",
                    result='Passed' if app.status == 'Selected' else 'Pending',
                    remarks='Demonstrated proficiency in Python, databases, and system design.'
                )
                db.session.add(r2)

                # Round 3: HR / Managerial (for Selected candidates)
                if app.status == 'Selected':
                    interview_counter += 1
                    r3 = InterviewRound(
                        interview_code=f"INT-{interview_counter}",
                        application_id=app.id,
                        round_number=3,
                        round_type='HR',
                        round_date=datetime.combine(app.application_date + timedelta(days=16), datetime.min.time()),
                        interviewer=app.company.hr_contact_name or 'Senior HR Manager',
                        result='Passed',
                        remarks='Strong cultural alignment, communication skills, and enthusiasm.'
                    )
                    db.session.add(r3)

            elif app.status == 'Rejected':
                # Rejection interview record
                interview_counter += 1
                r_rej = InterviewRound(
                    interview_code=f"INT-{interview_counter}",
                    application_id=app.id,
                    round_number=1,
                    round_type='Technical',
                    round_date=datetime.combine(app.application_date + timedelta(days=5), datetime.min.time()),
                    interviewer=f"Technical Panel ({app.company.name})",
                    result='Failed',
                    remarks='Requires improvement in distributed system design and data structures.'
                )
                db.session.add(r_rej)

        db.session.commit()

        # -------------------------------------------------------------
        # 7. Create Placement Records for Selected Students
        # -------------------------------------------------------------
        print("[*] Seeding official placement records (preventing duplicates)...")
        plc_counter = 100
        placed_students_set = set()

        for app in applications:
            if app.status == 'Selected' and app.student_id not in placed_students_set:
                plc_counter += 1
                p_date = app.application_date + timedelta(days=20)
                plc_type = 'Off-campus' if plc_counter % 5 == 0 else 'On-campus'
                
                placement = Placement(
                    placement_code=f"PLC-2024-{plc_counter}",
                    student_id=app.student_id,
                    company_id=app.company_id,
                    job_id=app.job_id,
                    placement_date=p_date,
                    ctc=app.job.salary_ctc,
                    placement_type=plc_type,
                    status='Active'
                )
                db.session.add(placement)
                placed_students_set.add(app.student_id)

                # Synchronize student placement status
                stu = Student.query.get(app.student_id)
                stu.placement_status = 'Placed'

        # Update remaining students as 'In-Process' if they have active interviews/shortlisting
        for stu in students:
            if stu.id not in placed_students_set:
                has_active = any(a.status in ['Shortlisted', 'Assessment', 'Interview'] for a in stu.applications)
                stu.placement_status = 'In-Process' if has_active else 'Unplaced'

        db.session.commit()

        # -------------------------------------------------------------
        # 8. Create Sample Document / S3 Records
        # -------------------------------------------------------------
        print("[*] Creating sample S3 documents & dataset metadata...")
        docs_data = [
            {
                'document_code': 'DOC-2024-001',
                'file_name': 'Nighil_Natarajan_Resume.pdf',
                's3_key': 'resumes/nighil_natarajan_23ad002_resume.pdf',
                'file_type': 'pdf',
                'file_size': 425120,
                'document_type': 'Resume',
                'student_id': students[1].id,
                'uploaded_by': 'Nighil Natarajan',
                'storage_backend': 'S3'
            },
            {
                'document_code': 'DOC-2024-002',
                'file_name': 'Nithilan_M_Resume.pdf',
                's3_key': 'resumes/nithilan_m_23ad004_resume.pdf',
                'file_type': 'pdf',
                'file_size': 389200,
                'document_type': 'Resume',
                'student_id': students[3].id,
                'uploaded_by': 'Nithilan M',
                'storage_backend': 'S3'
            },
            {
                'document_code': 'DOC-2024-003',
                'file_name': 'AWS_Cloud_Placement_Offer_Letter.pdf',
                's3_key': 'offers/aws_offer_2024.pdf',
                'file_type': 'pdf',
                'file_size': 812900,
                'document_type': 'Offer Letter',
                'student_id': students[1].id,
                'uploaded_by': 'Placement Coordinator',
                'storage_backend': 'S3'
            },
            {
                'document_code': 'DOC-2024-004',
                'file_name': 'Campus_Placement_Analytics_Report_2024.pdf',
                's3_key': 'reports/placement_annual_report_2024.pdf',
                'file_type': 'pdf',
                'file_size': 1450800,
                'document_type': 'Placement Report',
                'student_id': None,
                'uploaded_by': 'Chief Placement Officer',
                'storage_backend': 'S3'
            },
            {
                'document_code': 'DOC-2024-005',
                'file_name': 'BDA_Placement_Prediction_Dataset.csv',
                's3_key': 'datasets/bda_placement_dataset_2024.csv',
                'file_type': 'csv',
                'file_size': 256000,
                'document_type': 'Dataset',
                'student_id': None,
                'uploaded_by': 'Chief Placement Officer',
                'storage_backend': 'S3'
            }
        ]

        for d in docs_data:
            doc = Document(**d)
            db.session.add(doc)
        db.session.commit()

        # Summary counts
        print("\n==================================================")
        print("SEEDING COMPLETED SUCCESSFULLY!")
        print("==================================================")
        print(f"Users created       : {User.query.count()}")
        print(f"Students created    : {Student.query.count()} (All 30 AI & DS - B students seeded!)")
        print(f"Companies created   : {Company.query.count()}")
        print(f"Jobs created        : {Job.query.count()}")
        print(f"Applications created: {Application.query.count()}")
        print(f"Interviews created  : {InterviewRound.query.count()}")
        print(f"Placements created  : {Placement.query.count()}")
        print(f"Documents created   : {Document.query.count()}")
        print("--------------------------------------------------")
        print("Default Admin Login: admin@campusplacements.edu / Admin@123")
        print("Coordinator Login  : coordinator@campusplacements.edu / Coord@123")
        print("==================================================\n")

if __name__ == '__main__':
    seed_database()
