# Database Schema & Relational Architecture
## CampusPlacements: Student Placement Management & Analytics System

This document outlines the complete relational database design for the **CampusPlacements** platform. The schema is implemented using **SQLAlchemy ORM** and is 100% compatible with **Amazon RDS MySQL 8.0** and local MySQL/SQLite.

---

### Entity-Relationship Diagram (ERD)

```text
 ┌───────────────────────────┐
 │           USERS           │
 ├───────────────────────────┤
 │ PK  id                    │
 │     email (UQ, Index)     │
 │     password_hash         │
 │     full_name             │
 │     role                  │
 │     created_at            │
 └───────────────────────────┘

 ┌───────────────────────────┐          1:N          ┌───────────────────────────┐
 │         COMPANIES         │──────────────────────<│           JOBS            │
 ├───────────────────────────┤                       ├───────────────────────────┤
 │ PK  id                    │                       │ PK  id                    │
 │     name (UQ, Index)      │                       │     job_code (UQ, Index)  │
 │     industry              │                       │ FK  company_id            │
 │     location              │                       │     title                 │
 │     website               │                       │     job_type              │
 │     hr_contact_name       │                       │     location              │
 │     hr_contact_email      │                       │     min_cgpa              │
 │     hr_contact_phone      │                       │     required_skills       │
 │     description           │                       │     salary_ctc (LPA)      │
 │     created_at            │                       │     deadline              │
 │     updated_at            │                       │     status                │
 └─────────────┬─────────────┘                       └─────────────┬─────────────┘
               │                                                   │
               │ 1:N                                               │ 1:N
               │                                                   │
               ▼                                                   ▼
 ┌───────────────────────────┐          1:N          ┌───────────────────────────┐
 │         STUDENTS          │──────────────────────<│       APPLICATIONS        │
 ├───────────────────────────┤                       ├───────────────────────────┤
 │ PK  id                    │                       │ PK  id                    │
 │     student_id (UQ, Index)│                       │     application_code (UQ) │
 │     name                  │                       │ FK  student_id            │
 │     email (UQ)            │                       │ FK  job_id                │
 │     phone                 │                       │ FK  company_id            │
 │     department            │                       │     application_date      │
 │     batch                 │                       │     status                │
 │     graduation_year       │                       │     remarks               │
 │     cgpa                  │                       └─────────────┬─────────────┘
 │     skills                │                                     │
 │     placement_status      │                                     │ 1:N
 └──────┬──────────────┬─────┘                                     │
        │              │                                           ▼
    1:1 │          1:N │                             ┌───────────────────────────┐
        │              │                             │     INTERVIEW_ROUNDS      │
        ▼              ▼                             ├───────────────────────────┤
 ┌──────────────┐ ┌──────────────┐                   │ PK  id                    │
 │  PLACEMENTS  │ │  DOCUMENTS   │                   │     interview_code (UQ)   │
 ├──────────────┤ ├──────────────┤                   │ FK  application_id        │
 │ PK  id       │ │ PK  id       │                   │     round_number          │
 │     plc_code │ │     doc_code │                   │     round_type            │
 │ FK  student_id │ FK student_id│                   │     round_date            │
 │     (UQ)     │ │     file_name│                   │     interviewer           │
 │ FK  company_id│ │     s3_key   │                   │     result                │
 │ FK  job_id   │ │     file_type│                   │     remarks               │
 │     ctc (LPA)│ │     file_size│                   └───────────────────────────┘
 │     plc_type │ │     doc_type │
 │     status   │ │     storage  │
 └──────────────┘ └──────────────┘
```

---

## Detailed Table Specifications

### 1. `users` (System Administrators & Placement Coordinators)
Stores credential and role data for university staff. Application passwords are encrypted using `werkzeug.security` (PBKDF2-HMAC-SHA256).

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTO_INCREMENT` | Internal user unique identifier |
| `email` | `VARCHAR(120)` | `UNIQUE`, `NOT NULL`, `INDEX` | Login username/email address |
| `password_hash` | `VARCHAR(255)` | `NOT NULL` | Cryptographic PBKDF2 hash of password |
| `full_name` | `VARCHAR(100)` | `NOT NULL` | Name of the staff coordinator |
| `role` | `VARCHAR(30)` | `DEFAULT 'coordinator'` | Authorization role (`admin`, `coordinator`) |
| `created_at` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP` | Account creation timestamp |
| `updated_at` | `DATETIME` | `ON UPDATE CURRENT_TIMESTAMP` | Last profile update timestamp |

---

### 2. `students` (University Student Cohort)
Maintains academic records, skill inventories, and current placement standing for students.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTO_INCREMENT` | Internal database surrogate key |
| `student_id` | `VARCHAR(50)` | `UNIQUE`, `NOT NULL`, `INDEX` | Official University Roll ID (e.g. `23AD001`) |
| `name` | `VARCHAR(120)` | `NOT NULL` | Candidate full name |
| `email` | `VARCHAR(120)` | `UNIQUE`, `NOT NULL` | University email address |
| `phone` | `VARCHAR(20)` | `NULLABLE` | Candidate contact telephone |
| `department` | `VARCHAR(100)` | `NOT NULL` | Academic major (e.g. `AI & DS`) |
| `batch` | `VARCHAR(20)` | `NOT NULL`, `DEFAULT '2023'` | University class/batch identifier |
| `graduation_year` | `INTEGER` | `NOT NULL`, `DEFAULT 2025` | Expected year of degree completion |
| `cgpa` | `FLOAT` | `NOT NULL` | Cumulative Grade Point Average (scale: 10.0) |
| `skills` | `TEXT` | `NULLABLE` | Comma-delimited technical competencies |
| `placement_status`| `VARCHAR(30)` | `DEFAULT 'Unplaced'` | Pipeline state (`Placed`, `Unplaced`, `In-Process`) |
| `created_at` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP` | Registration timestamp |
| `updated_at` | `DATETIME` | `ON UPDATE CURRENT_TIMESTAMP` | Last modification timestamp |

---

### 3. `companies` (Corporate Recruitment Partners)
Stores profile information and point-of-contact details for visiting recruiters.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTO_INCREMENT` | Internal company identifier |
| `name` | `VARCHAR(150)` | `UNIQUE`, `NOT NULL`, `INDEX` | Registered legal corporate name |
| `industry` | `VARCHAR(100)` | `NOT NULL` | Industry sector (e.g. `Cloud Computing`, `SaaS`) |
| `location` | `VARCHAR(100)` | `NOT NULL` | City/State of office or headquarters |
| `website` | `VARCHAR(255)` | `NULLABLE` | Corporate URL |
| `hr_contact_name` | `VARCHAR(100)` | `NULLABLE` | Campus Talent Acquisition Lead |
| `hr_contact_email`| `VARCHAR(120)` | `NULLABLE` | Official HR email address |
| `hr_contact_phone`| `VARCHAR(20)` | `NULLABLE` | HR contact phone number |
| `description` | `TEXT` | `NULLABLE` | Business overview & engineering culture |
| `created_at` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP` | Registration timestamp |

---

### 4. `jobs` (Placement Job Openings)
Details specific employment and internship drives posted by corporate partners.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTO_INCREMENT` | Internal opening identifier |
| `job_code` | `VARCHAR(50)` | `UNIQUE`, `NOT NULL`, `INDEX` | University job code (e.g. `JOB-AWS-001`) |
| `company_id` | `INTEGER` | `FOREIGN KEY (companies.id)` | Recruiting company reference |
| `title` | `VARCHAR(150)` | `NOT NULL` | Job role title |
| `job_type` | `VARCHAR(50)` | `DEFAULT 'Full-Time'` | Contract category (`Full-Time`, `Internship`) |
| `location` | `VARCHAR(100)` | `NOT NULL` | Job work location |
| `min_cgpa` | `FLOAT` | `DEFAULT 6.5` | Minimum cutoff CGPA required to apply |
| `required_skills` | `TEXT` | `NULLABLE` | Mandatory skill qualifications |
| `salary_ctc` | `FLOAT` | `NOT NULL` | Annual Cost-to-Company package in Lakhs (LPA) |
| `deadline` | `DATE` | `NULLABLE` | Final date for accepting applications |
| `description` | `TEXT` | `NULLABLE` | Responsibilities and candidate specifications |
| `status` | `VARCHAR(30)` | `DEFAULT 'Open'` | Drive availability (`Open`, `Closed`, `Completed`) |

---

### 5. `applications` (Recruitment Submissions)
Tracks student candidates through various stages of the hiring funnel.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTO_INCREMENT` | Internal application record ID |
| `application_code`| `VARCHAR(50)` | `UNIQUE`, `NOT NULL`, `INDEX` | Application reference code (e.g. `APP-2024-101`) |
| `student_id` | `INTEGER` | `FOREIGN KEY (students.id)` | Applying candidate ID |
| `job_id` | `INTEGER` | `FOREIGN KEY (jobs.id)` | Target job posting ID |
| `company_id` | `INTEGER` | `FOREIGN KEY (companies.id)` | Company ID |
| `application_date`| `DATE` | `DEFAULT CURRENT_DATE` | Date application was lodged |
| `status` | `VARCHAR(50)` | `DEFAULT 'Applied'` | Funnel stage (`Applied`, `Shortlisted`, `Assessment`, `Interview`, `Selected`, `Rejected`, `Withdrawn`) |
| `remarks` | `TEXT` | `NULLABLE` | Coordinator notes or reviewer feedback |

---

### 6. `interview_rounds` (Multi-Stage Evaluations)
Logs individual assessment rounds (coding tests, technical interviews, HR rounds) per application.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTO_INCREMENT` | Internal interview round ID |
| `interview_code` | `VARCHAR(50)` | `UNIQUE`, `NOT NULL`, `INDEX` | Round reference code (e.g. `INT-101`) |
| `application_id` | `INTEGER` | `FOREIGN KEY (applications.id)`| Parent application reference |
| `round_number` | `INTEGER` | `DEFAULT 1` | Sequential order (1, 2, 3...) |
| `round_type` | `VARCHAR(50)` | `NOT NULL` | Category (`Aptitude`, `Technical`, `HR`, `Group Discussion`, `Managerial`) |
| `round_date` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP` | Date and time interview occurred |
| `interviewer` | `VARCHAR(100)` | `NULLABLE` | Interviewer name or panel designation |
| `result` | `VARCHAR(30)` | `DEFAULT 'Pending'` | Evaluation result (`Pending`, `Passed`, `Failed`) |
| `remarks` | `TEXT` | `NULLABLE` | Technical feedback and evaluation score |

---

### 7. `placements` (Official Offers & Placed Records)
Records official verified placement offers. A critical business rule is enforced: **a student can hold only one active primary placement**, preventing duplicate offers.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTO_INCREMENT` | Internal placement offer ID |
| `placement_code` | `VARCHAR(50)` | `UNIQUE`, `NOT NULL`, `INDEX` | Offer code (e.g. `PLC-2024-101`) |
| `student_id` | `INTEGER` | `FOREIGN KEY (students.id)`, `UNIQUE` | Candidate ID (**Unique constraint blocks duplicate active offers**) |
| `company_id` | `INTEGER` | `FOREIGN KEY (companies.id)` | Hiring company |
| `job_id` | `INTEGER` | `FOREIGN KEY (jobs.id)` | Role offered |
| `placement_date` | `DATE` | `DEFAULT CURRENT_DATE` | Date offer was extended |
| `ctc` | `FLOAT` | `NOT NULL` | Final compensation package in LPA |
| `placement_type` | `VARCHAR(50)` | `DEFAULT 'On-campus'` | Hiring category (`On-campus`, `Off-campus`) |
| `status` | `VARCHAR(30)` | `DEFAULT 'Active'` | Offer status (`Active`, `Declined`) |

---

### 8. `documents` (Amazon S3 Object Metadata)
Catalogs file objects stored in **Amazon S3**. **The binary files are NOT stored in RDS**; only object keys, sizes, types, and metadata are persisted in MySQL.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY`, `AUTO_INCREMENT` | Metadata record identifier |
| `document_code` | `VARCHAR(50)` | `UNIQUE`, `NOT NULL`, `INDEX` | Document code (e.g. `DOC-2024-101`) |
| `file_name` | `VARCHAR(255)` | `NOT NULL` | Original uploaded filename |
| `s3_key` | `VARCHAR(500)` | `NOT NULL`, `INDEX` | Full object key path in Amazon S3 (e.g. `resumes/abc_resume.pdf`) |
| `file_type` | `VARCHAR(50)` | `NOT NULL` | Extension/MIME (`pdf`, `csv`, `docx`) |
| `file_size` | `INTEGER` | `NOT NULL` | Exact size in bytes |
| `document_type` | `VARCHAR(50)` | `DEFAULT 'Resume'` | Classification (`Resume`, `Placement Report`, `Company Document`, `Dataset`) |
| `student_id` | `INTEGER` | `FOREIGN KEY (students.id)` | Associated student (optional) |
| `uploaded_by` | `VARCHAR(100)` | `DEFAULT 'Coordinator'` | Name of uploader |
| `storage_backend`| `VARCHAR(20)` | `DEFAULT 'S3'` | Target storage system (`S3` or `Local`) |
| `uploaded_at` | `DATETIME` | `DEFAULT CURRENT_TIMESTAMP` | Upload timestamp |

---

## Architectural Indexes & Query Optimization

1. **Analytical Groupings:**
   - `students(department)` and `students(placement_status)` are indexed for sub-millisecond aggregations on the BDA Analytics dashboard.
   - `placements(ctc)` and `placements(company_id)` optimize high-speed computation of average CTC packages across branches and firms.
2. **Audit & Search:**
   - `students(student_id)` and `jobs(job_code)` carry unique B-Tree indexes allowing instant $O(1)$ lookups during application submission.
   - `documents(s3_key)` is indexed to maintain atomic synchronization between S3 bucket operations and database records.
