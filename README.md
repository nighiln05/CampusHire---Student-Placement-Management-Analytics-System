# CampusPlacements
### Student Placement Management & Analytics System

---

## Project Overview

**CampusPlacements** is a full-stack, enterprise-grade cloud web application engineered to manage university placement recruitment drives, student career pipelines, corporate partner relationships, interview evaluations, and big data recruitment analytics.

The application is architected specifically to demonstrate modern cloud infrastructure on **Amazon Web Services (AWS)**:
* **EC2 Web Server (Public Subnet):** Runs the Python Flask web application served by Gunicorn.
* **Amazon RDS MySQL (Private Subnet):** Stores all structured relational records in a private database tier.
* **Amazon S3 Object Storage:** Stores binary documents, student resumes, placement offer letters, and analytics datasets.
* **AWS IAM Instance Role:** Grants least-privilege, keyless access from the EC2 application to the S3 bucket.
* **AWS VPC & Security Groups:** Implements isolation with public/private subnet routing and strict firewall packet filtering.

---

## Key Features

1. **Executive Dashboard:** Real-time KPI counters (Total Students, Companies, Open Jobs, Applications, Placed Candidates, and Placement Rate) with 4 dynamic Chart.js time-series and distribution graphs.
2. **Dedicated BDA Analytics Engine:** 10 real-time analytical visualizations calculated on-the-fly from database aggregations with dynamic multi-dimensional filters (Department, Graduation Year, Company, Job Role).
3. **Student Directory:** Academic profiles, CGPAs, skill inventories, application history, and interview feedback for the cohort of students (seeded with the exact 30 students from **AI & DS - B, Batch 2023**, starting with Navya Jain and Nighil Natarajan).
4. **Company & Job Management:** Partner directory with corporate contacts, job opportunity specifications, minimum eligibility cutoffs, and CTC packages.
5. **Multi-Stage Application Pipeline:** Full lifecycle tracking from `Applied` &rarr; `Shortlisted` &rarr; `Assessment` &rarr; `Interview` &rarr; `Selected` &rarr; `Rejected`.
6. **Interview Scheduling:** Multi-round tracking (Aptitude, Technical, HR, Group Discussion, Managerial) with evaluator remarks and results.
7. **Official Placements Ledger:** Enforces business logic ensuring a student holds only **one active primary offer**, preventing duplicate offers.
8. **Amazon S3 Cloud Documents:** Direct file streaming to AWS S3 via `boto3` with presigned download links, coupled with an automatic local storage fallback for zero-configuration local development.

---

## Tech Stack

* **Backend:** Python 3 (Flask, Werkzeug, python-dotenv)
* **Database & ORM:** SQLAlchemy, PyMySQL (MySQL 8.0 & Amazon RDS MySQL, SQLite zero-config local fallback)
* **Cloud Storage:** Amazon S3 via `boto3` SDK
* **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5, Font Awesome 6
* **Visualizations & Charts:** Chart.js 4
* **Production Deployment:** Gunicorn WSGI, systemd, Nginx reverse proxy

---

## Local Development Quickstart (Windows / macOS / Linux)

You can run and test the complete system on your local computer in **under 3 minutes** without needing a local MySQL server or active AWS credentials:

### 1. Prerequisites
* Python 3.9, 3.10, 3.11, or 3.12 installed.
* Pip package manager.

### 2. Navigate to the Project Directory
```bash
cd "c:\Users\Nighil Natarajan\Desktop\BDA_mini_project"
```

### 3. Create and Activate Virtual Environment
```powershell
# Windows PowerShell:
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS:
# python3 -m venv venv
# source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
cp .env.example .env
```
*(By default, `DATABASE_URL=sqlite:///campusplacements.db` is configured, allowing instant local testing. For MySQL or Amazon RDS, simply update `DATABASE_URL` in `.env`).*

### 6. Initialize Database Tables
```bash
python scripts/init_db.py
```

### 7. Seed Sample Data (Exact 30 AI & DS Students)
```bash
python scripts/seed_data.py
```

### 8. Run the Application
```bash
python app.py
```

### 9. Open in Your Browser
Navigate to:  
👉 **`http://localhost:5000`**

### 10. Default Login Credentials
* **Admin Email:** `admin@campusplacements.edu`
* **Admin Password:** `Admin@123`
* *(Coordinator Account:* `coordinator@campusplacements.edu` / `Coord@123`*)*

---

## 14-Step Recommended Demonstration Sequence (Lab Evaluation)

Follow this exact sequence to demonstrate all capabilities to your college lab evaluators:

1. **System Launch & Security:** Open `http://localhost:5000`. Show that unauthenticated requests are intercepted and redirected to `/auth/login`.
2. **Login:** Enter `admin@campusplacements.edu` and `Admin@123`. Click **Sign In**.
3. **Executive Dashboard:** Point out the 6 real-time KPI cards (Total Students, Companies, Jobs, Applications, Placed, Placement Rate: 77.8%) and the AWS architecture status banner.
4. **Live Charts:** Scroll down to the 4 dashboard charts (Monthly Applications Trend, Placements by Department, Top Recruiters, Application Pipeline).
5. **Student Directory:** Click **Students** in the sidebar. Highlight the exact 30 students from **AI & DS - B, Batch 2023** (e.g. Navya Jain, Nighil Natarajan, etc.).
6. **Student Profile:** Click the eye icon next to **Nighil Natarajan** (Roll: `23AD002`). Review academic info, skills, placement offer, applications, and interview records.
7. **Add Student:** Click **Register Student**, enter a new student, and verify that the record saves.
8. **Company Management:** Click **Companies** to display the 10 tech partners (Amazon, Microsoft, Zoho, Google, TCS, Infosys, Cisco, etc.).
9. **Job Openings:** Click **Job Openings** to view active drives, minimum CGPA requirements, and salary packages (e.g. ₹24.5 LPA AWS SDE, ₹8.5 LPA Zoho MTS).
10. **Application Lifecycle:** Click **Applications**, open an application, and click **Update Stage** to move a candidate from `Interview` to `Selected`.
11. **Interview Evaluation:** Click **Interview Rounds** to display multi-stage evaluations (Aptitude, Technical, HR) with interviewer remarks and scores.
12. **Placement Duplicate Prevention:** Click **Placements Record**. Demonstrate adding an offer, and highlight how the database prevents duplicate active placement offers for the same student.
13. **Cloud S3 Documents:** Click **Documents & S3**. Upload a sample resume PDF. Point out that the file is stored in S3/storage and only metadata is cataloged in RDS. Test downloading via presigned link.
14. **Big Data Analytics Lab Page:** Click **BDA Lab Analytics**. Show the 10 deep analytics charts. Change the **Department** or **Company** dropdown and observe all 10 charts recalculating dynamically from live database queries!

---

## Project Structure

```
BDA_mini_project/
├── app.py                      # Flask Application Factory & Entrypoint
├── config.py                   # Environment & Application Configuration
├── requirements.txt            # Python Dependencies
├── .env.example                # Environment Variable Template
├── README.md                   # Project Overview & Setup Instructions
├── AWS_DEPLOYMENT_GUIDE.md     # 16-Step Manual AWS Configuration Guide
├── DATABASE_SCHEMA.md          # Full Relational DB Architecture & ERD
│
├── models/                     # SQLAlchemy Relational Models
│   ├── __init__.py
│   ├── user.py                 # Users & Password Hashing
│   ├── student.py              # Students (Exact 30 AI&DS Roster)
│   ├── company.py              # Corporate Recruiters
│   ├── job.py                  # Job Openings
│   ├── application.py          # Student Applications Pipeline
│   ├── interview.py            # Multi-Round Interview Evaluations
│   ├── placement.py            # Official Offers (Unique constraint)
│   └── document.py             # S3 Document Metadata
│
├── routes/                     # Modular Blueprints
│   ├── __init__.py             # Session Authentication Guard
│   ├── auth.py                 # Login / Logout
│   ├── dashboard.py            # Executive Overview & Chart APIs
│   ├── students.py             # Student CRUD & Filtering
│   ├── companies.py            # Company Directory & Details
│   ├── jobs.py                 # Job Postings & Eligibility
│   ├── applications.py         # Application Funnel & Status Updates
│   ├── interviews.py           # Interview Scheduling & Results
│   ├── placements.py           # Placement Records & Duplicate Check
│   ├── documents.py            # S3 File Uploads & Presigned URLs
│   └── analytics.py            # BDA Analytics Dashboard & APIs
│
├── services/                   # Business & Cloud Integrations
│   ├── __init__.py
│   ├── s3_service.py           # Boto3 AWS S3 Engine + Local Fallback
│   └── analytics_service.py    # SQL Aggregations for 10 BDA Metrics
│
├── templates/                  # Jinja2 HTML5 Templates (Bootstrap 5)
│   ├── base.html               # Main Navigation & Cloud Status Layout
│   ├── auth/login.html         # Login Portal
│   ├── dashboard/index.html    # Executive Dashboard
│   ├── students/               # Student Index, Detail, and Form
│   ├── companies/              # Company Index, Detail, and Form
│   ├── jobs/                   # Job Index, Detail, and Form
│   ├── applications/           # Application Tracker, Detail, and Form
│   ├── interviews/             # Interview Schedule & Evaluation Form
│   ├── placements/             # Placements Ledger & Record Form
│   ├── documents/index.html    # S3 Object Storage Center
│   ├── analytics/index.html    # BDA Lab Analytics (10 Charts)
│   └── errors/                 # 404 & 500 Error Pages
│
├── static/                     # Frontend Assets
│   ├── css/style.css           # Modern Enterprise Design System
│   ├── js/main.js              # UI Interactivity & Modals
│   ├── js/charts.js            # Dashboard Chart.js Visualizations
│   └── js/analytics.js         # Dynamic Analytics Chart Engine
│
└── scripts/                    # Automation & Seeding
    ├── init_db.py              # Database Table Creation Script
    ├── seed_data.py            # Exact 30 Student Seed Script
    └── test_app.py             # Automated Endpoint & Data Verification
```

---

## AWS Cloud Deployment

For the complete 16-step manual AWS infrastructure deployment manual, refer to [AWS_DEPLOYMENT_GUIDE.md](file:///c:/Users/Nighil%20Natarajan/Desktop/BDA_mini_project/AWS_DEPLOYMENT_GUIDE.md).
