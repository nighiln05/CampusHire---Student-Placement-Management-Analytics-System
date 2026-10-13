# AWS Configuration and Deployment Guide
## CampusPlacements: Student Placement Management & Analytics System
**Big Data Analytics Lab Mini Project**

This guide provides the complete, step-by-step manual instructions to architect, configure, and deploy the **CampusPlacements** web application on **Amazon Web Services (AWS)**.

---

### Cloud Architecture Diagram

```text
                                INTERNET (University Users / Recruiters)
                                                   │
                                                   ▼
                                         [ INTERNET GATEWAY ]
                                                   │
┌──────────────────────────────────────────────────┼──────────────────────────────────────────────────┐
│ AWS VPC (CIDR: 10.0.0.0/16)                      │                                                  │
│                                                  ▼                                                  │
│  ┌───────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ PUBLIC SUBNET (CIDR: 10.0.1.0/24 | AZ: us-east-1a)                                            │  │
│  │                                                                                               │  │
│  │   ┌────────────────────────────────────────────────────────┐                                  │  │
│  │   │ AMAZON EC2 INSTANCE (t2.micro / Ubuntu 22.04 LTS)       │                                  │  │
│  │   │                                                        │                                  │  │
│  │   │  • Gunicorn WSGI Server + Flask Application            │                                  │  │
│  │   │  • Systemd Service: campusplacements.service           │                                  │  │
│  │   │  • EC2 Security Group: Port 22 (My IP), Port 80 (Any)  │                                  │  │
│  │   │  • Attached IAM Role: EC2-S3-CampusPlacements-Role     │                                  │  │
│  │   └──────────────────────┬───────────────────────────┬─────┘                                  │  │
│  └──────────────────────────┼───────────────────────────┼────────────────────────────────────────┘  │
│                             │                           │                                           │
│   SQL Queries (Port 3306)   │                           │ Boto3 S3 API (HTTPS 443 via IAM Role)     │
│   (Private Network Only)    ▼                           ▼                                           │
│  ┌─────────────────────────────────────────┐   ┌────────────────────────────────────────────────┐   │
│  │ PRIVATE SUBNETS (DB Subnet Group)       │   │ AMAZON S3 BUCKET                               │   │
│  │                                         │   │ (campusplacements-data-storage-<unique-id>)    │   │
│  │  • Private Subnet 1 (10.0.2.0/24 in 1a) │   │                                                │   │
│  │  • Private Subnet 2 (10.0.3.0/24 in 1b) │   │  • Student Resumes (/resumes/)                 │   │
│  │                                         │   │  • Placement Reports (/reports/)               │   │
│  │   ┌──────────────────────────────────┐  │   │  • Company Documents (/company_docs/)          │   │
│  │   │ AMAZON RDS MYSQL (db.t3.micro)   │  │   │  • BDA Analytics Datasets (/datasets/)         │   │
│  │   │                                  │  │   │                                                │   │
│  │   │  • No Public Accessibility       │  │   │  • Block All Public Access: ENABLED            │   │
│  │   │  • RDS Security Group:           │  │   │  • Server-Side Encryption: AES-256 (SSE-S3)    │   │
│  │   │    Accepts 3306 ONLY from EC2 SG │  │   │  • Presigned URL Downloads                     │   │
│  │   └──────────────────────────────────┘  │   └────────────────────────────────────────────────┘   │
│  └─────────────────────────────────────────┘                                                        │
└─────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 16-Step Step-by-Step AWS Configuration

Every step includes the exact commands and navigation, clearly designated by execution environment:
* `[AWS CONSOLE]` — Actions taken within the AWS Management Console web UI.
* `[AWS CLI]` — Optional commands if using AWS Command Line Interface.
* `[LOCAL MACHINE]` — Commands executed in your local terminal (Windows PowerShell or macOS/Linux).
* `[EC2 TERMINAL]` — Commands executed after SSHing into the EC2 virtual machine.

---

### Step 1 – Create the VPC (Virtual Private Cloud)
The VPC serves as your private, isolated virtual data center in the AWS cloud.

* **CIDR Block:** `10.0.0.0/16` (Provides 65,536 private IP addresses)
* **Name Tag:** `CampusPlacements-VPC`
* **DNS Settings:** Enable DNS resolution and DNS hostnames so EC2 and RDS endpoints resolve properly.

#### [AWS CONSOLE]
1. Open the AWS Management Console and navigate to **VPC**.
2. Click **Create VPC**.
3. Under **Resources to create**, select **VPC only**.
4. **Name tag:** `CampusPlacements-VPC`
5. **IPv4 CIDR block:** `10.0.0.0/16`
6. Leave IPv6 as *No IPv6 CIDR block*.
7. **Tenancy:** *Default*.
8. Click **Create VPC**.
9. Once created, select your VPC, click **Actions** &rarr; **Edit VPC settings**.
10. Under **DNS settings**, check **Enable DNS resolution** and **Enable DNS hostnames**. Click **Save changes**.

#### [AWS CLI]
```bash
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=CampusPlacements-VPC}]"
# Note the VpcId from the output (e.g. vpc-0a1b2c3d4e5f)
aws ec2 modify-vpc-attribute --vpc-id <YOUR_VPC_ID> --enable-dns-hostnames "{\"Value\":true}"
aws ec2 modify-vpc-attribute --vpc-id <YOUR_VPC_ID> --enable-dns-support "{\"Value\":true}"
```

---

### Step 2 – Create the Public Subnet
This subnet holds the internet-facing EC2 instance running our Flask application.

* **CIDR Block:** `10.0.1.0/24` (256 IP addresses)
* **Availability Zone:** `us-east-1a`
* **Name Tag:** `CampusPlacements-Public-Subnet`
* **Auto-assign Public IP:** Enabled (So the EC2 web server receives a public IPv4 address).

#### [AWS CONSOLE]
1. In the VPC Console, click **Subnets** in the left sidebar.
2. Click **Create subnet**.
3. **VPC ID:** Select `CampusPlacements-VPC`.
4. **Subnet name:** `CampusPlacements-Public-Subnet`
5. **Availability Zone:** Select `us-east-1a` (or your primary region's zone `a`).
6. **IPv4 CIDR block:** `10.0.1.0/24`
7. Click **Create subnet**.
8. Select the newly created subnet, click **Actions** &rarr; **Edit subnet settings**.
9. Under **Auto-assign IP settings**, check **Enable auto-assign public IPv4 address**. Click **Save**.

---

### Step 3 – Create the Private Subnets
Amazon RDS requires a **DB Subnet Group** spanning **at least two Availability Zones** to ensure high availability and redundancy, even for single-instance deployments. These subnets have no direct route to the Internet, keeping MySQL database storage isolated.

* **Private Subnet 1:** CIDR `10.0.2.0/24` in `us-east-1a` (Name: `CampusPlacements-Private-Subnet-1`)
* **Private Subnet 2:** CIDR `10.0.3.0/24` in `us-east-1b` (Name: `CampusPlacements-Private-Subnet-2`)

#### [AWS CONSOLE]
1. In the VPC Console &rarr; **Subnets**, click **Create subnet**.
2. **VPC ID:** `CampusPlacements-VPC`
3. **Subnet 1:**
   - **Subnet name:** `CampusPlacements-Private-Subnet-1`
   - **Availability Zone:** `us-east-1a`
   - **IPv4 CIDR block:** `10.0.2.0/24`
4. Click **Add new subnet** below it:
   - **Subnet name:** `CampusPlacements-Private-Subnet-2`
   - **Availability Zone:** `us-east-1b` (Must be a different AZ from Subnet 1)
   - **IPv4 CIDR block:** `10.0.3.0/24`
5. Click **Create subnet**.
*(Note: Do NOT enable auto-assign public IP on private subnets).*

---

### Step 4 – Create Internet Gateway and Attach to VPC
The Internet Gateway (IGW) enables bidirectional communication between instances in the public subnet and the Internet.

#### [AWS CONSOLE]
1. In the VPC Console, click **Internet Gateways** in the left sidebar.
2. Click **Create internet gateway**.
3. **Name tag:** `CampusPlacements-IGW`
4. Click **Create internet gateway**.
5. On the gateway details page, click **Actions** &rarr; **Attach to VPC**.
6. Select `CampusPlacements-VPC` and click **Attach internet gateway**.

#### [AWS CLI]
```bash
aws ec2 create-internet-gateway --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=Name,Value=CampusPlacements-IGW}]"
aws ec2 attach-internet-gateway --internet-gateway-id <YOUR_IGW_ID> --vpc-id <YOUR_VPC_ID>
```

---

### Step 5 – Configure Public Route Table
Routes determine where network traffic is directed. We create a route table directing internet traffic (`0.0.0.0/0`) to the Internet Gateway, and associate it with our Public Subnet.

#### [AWS CONSOLE]
1. In the VPC Console, click **Route Tables**.
2. Click **Create route table**.
3. **Name:** `CampusPlacements-Public-RT`
4. **VPC:** Select `CampusPlacements-VPC`.
5. Click **Create route table**.
6. Select the newly created route table and choose the **Routes** tab &rarr; **Edit routes**.
7. Click **Add route**:
   - **Destination:** `0.0.0.0/0`
   - **Target:** Select **Internet Gateway** and pick `CampusPlacements-IGW`.
8. Click **Save changes**.
9. Click the **Subnet associations** tab &rarr; **Edit subnet associations**.
10. Check the box for `CampusPlacements-Public-Subnet` (`10.0.1.0/24`).
11. Click **Save associations**.

---

### Step 6 – Create Security Groups
Security groups act as stateful virtual firewalls.

#### A. EC2 Web Security Group (`CampusPlacements-EC2-SG`)
* **Inbound Rules:**
  * `SSH (Port 22)`: Source: **My IP** (Restricts shell access strictly to your current workstation for security).
  * `HTTP (Port 80)`: Source: `0.0.0.0/0` (Allows students and recruiters to view the website from any browser).
  * `Custom TCP (Port 5000)`: Source: `0.0.0.0/0` (Allows direct access to Flask development server during testing).

#### B. RDS Database Security Group (`CampusPlacements-RDS-SG`)
* **Inbound Rules:**
  * `MySQL/Aurora (Port 3306)`: Source: **Select the `CampusPlacements-EC2-SG` Security Group ID**.

> [!CRITICAL]
> **Why is 3306 &rarr; 0.0.0.0/0 strictly forbidden?**
> Exposing port 3306 to the entire internet exposes your database to brute-force credential dictionary attacks, automated bot scanners, and SQL injection vulnerability probes. By locking the RDS Security Group source strictly to `CampusPlacements-EC2-SG`, **only the EC2 server inside your VPC can establish a network socket with MySQL**. Even if someone discovers the RDS endpoint hostname, all external connection attempts are dropped at the AWS hypervisor packet filter.

#### [AWS CONSOLE]
1. In VPC Console &rarr; **Security Groups**, click **Create security group**.
2. **EC2 SG:**
   - **Name:** `CampusPlacements-EC2-SG`
   - **Description:** Allow SSH from My IP and HTTP from Internet
   - **VPC:** `CampusPlacements-VPC`
   - **Inbound rules:**
     - Rule 1: Type `SSH`, Port `22`, Source: `My IP`
     - Rule 2: Type `HTTP`, Port `80`, Source: `Anywhere-IPv4` (`0.0.0.0/0`)
     - Rule 3: Type `Custom TCP`, Port `5000`, Source: `Anywhere-IPv4` (`0.0.0.0/0`)
   - Click **Create security group**. (Copy the generated Security Group ID, e.g. `sg-0123456789abcdef0`).
3. Click **Create security group** again for RDS:
   - **Name:** `CampusPlacements-RDS-SG`
   - **Description:** Allow MySQL traffic exclusively from EC2 instance
   - **VPC:** `CampusPlacements-VPC`
   - **Inbound rules:**
     - Rule 1: Type `MySQL/Aurora`, Port `3306`, Source: In the search box, select `CampusPlacements-EC2-SG`.
   - Click **Create security group**.

---

### Step 7 – Launch the EC2 Web Application Instance

* **AMI:** Ubuntu Server 22.04 LTS (HVM), SSD Volume Type (64-bit x86)
* **Instance Type:** `t2.micro` (AWS Free Tier eligible)
* **Key Pair:** Create a new key pair (e.g. `campusplacements-key.pem`) and save it locally.
* **Network:** `CampusPlacements-VPC` &rarr; `CampusPlacements-Public-Subnet`
* **Auto-assign Public IP:** Enable
* **Security Group:** Select existing &rarr; `CampusPlacements-EC2-SG`
* **Storage:** 15 GB General Purpose SSD (gp3)

#### [AWS CONSOLE]
1. Open the **EC2** Console &rarr; click **Launch instance**.
2. **Name:** `CampusPlacements-WebServer`
3. **Application and OS Images:** Select **Ubuntu** (Ubuntu Server 22.04 LTS 64-bit).
4. **Instance type:** `t2.micro`.
5. **Key pair:** Click **Create new key pair**:
   - Key pair name: `campusplacements-key`
   - Key pair type: `RSA`
   - Private key file format: `.pem` (for OpenSSH / Linux / macOS / Windows PowerShell)
   - Click **Create key pair** (The file `campusplacements-key.pem` downloads to your computer).
6. Under **Network settings**, click **Edit**:
   - **VPC:** Select `CampusPlacements-VPC`.
   - **Subnet:** Select `CampusPlacements-Public-Subnet`.
   - **Auto-assign public IP:** Select **Enable**.
   - **Firewall (security groups):** Choose **Select existing security group** and pick `CampusPlacements-EC2-SG`.
7. **Configure storage:** Change 8 GiB to `15 GiB` gp3.
8. Click **Launch instance**.
9. In EC2 Instances list, wait until **Instance state** is `Running` and copy the **Public IPv4 address** (e.g. `54.210.45.120`).

---

### Step 8 – Connect to EC2 via SSH

#### [LOCAL MACHINE]
Open PowerShell or Command Prompt on your computer where `campusplacements-key.pem` is located:

```bash
# If on Linux/macOS, set secure file permissions:
chmod 400 campusplacements-key.pem

# SSH into the EC2 instance using its Public IP:
ssh -i "campusplacements-key.pem" ubuntu@<YOUR_EC2_PUBLIC_IP>
```

*(Type `yes` when prompted to accept host key fingerprint).*

---

### Step 9 – Install Web Application on EC2

#### [EC2 TERMINAL]
Run the following commands inside the EC2 SSH session:

```bash
# 1. Update Ubuntu system packages
sudo apt update && sudo apt upgrade -y

# 2. Install Python 3, pip, python3-venv, git, and MySQL development libraries
sudo apt install -y python3 python3-pip python3-venv git default-mysql-client libmysqlclient-dev pkg-config nginx

# 3. Create project directory under /var/www/ or home folder
cd /home/ubuntu
mkdir -p campusplacements
cd campusplacements

# 4. Copy or clone project code into this directory
# Option A: If using Git:
# git clone <YOUR_REPO_URL> .
# Option B: Or copy files from local machine using scp (see below)

# 5. Create Python Virtual Environment
python3 -m venv venv
source venv/bin/activate

# 6. Install all Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 7. Create .env configuration file
cp .env.example .env
nano .env
```

*(Edit `.env` using nano: set `SECRET_KEY`, and leave `DATABASE_URL` for Step 11 after RDS is provisioned. Press `Ctrl+O` & `Enter` to save, `Ctrl+X` to exit).*

> [!TIP]
> **How to copy project files from your local machine to EC2 via SCP:**
> Run this command on your **[LOCAL MACHINE]**:
> ```bash
> scp -i "campusplacements-key.pem" -r "c:\Users\Nighil Natarajan\Desktop\BDA_mini_project\*" ubuntu@<YOUR_EC2_PUBLIC_IP>:/home/ubuntu/campusplacements/
> ```

---

### Step 10 – Create the Amazon RDS MySQL Database

* **Engine:** MySQL Community 8.0
* **Template:** Free Tier
* **Instance Class:** `db.t3.micro` or `db.t4g.micro`
* **VPC:** `CampusPlacements-VPC`
* **Subnet Group:** Spanning `CampusPlacements-Private-Subnet-1` and `CampusPlacements-Private-Subnet-2`
* **Public Access:** **NO** (Disabled)
* **VPC Security Group:** `CampusPlacements-RDS-SG`
* **Master Username:** `admin`
* **Master Password:** `PlacementSecure2024!`
* **Initial Database Name:** `campusplacements_db`

#### [AWS CONSOLE]
1. Open the **Amazon RDS** Console.
2. In the left navigation, click **Subnet groups** &rarr; **Create DB Subnet Group**:
   - **Name:** `campusplacements-db-subnet-group`
   - **Description:** Subnet group for RDS MySQL in private subnets
   - **VPC:** `CampusPlacements-VPC`
   - **Add subnets:**
     - Select Availability Zones: `us-east-1a` and `us-east-1b`
     - Select Subnets: Check `10.0.2.0/24` and `10.0.3.0/24`
   - Click **Create**.
3. Click **Databases** &rarr; **Create database**:
   - **Database creation method:** *Standard create*
   - **Engine options:** *MySQL* (Version: MySQL 8.0.x)
   - **Templates:** Select **Free Tier**
   - **DB instance identifier:** `campusplacements-rds`
   - **Master username:** `admin`
   - **Master password:** `PlacementSecure2024!` (Choose a strong password and record it)
   - **DB instance class:** `db.t3.micro` (or `db.t4g.micro`)
   - **Storage:** 20 GiB gp3, leave storage autoscaling enabled
   - **Connectivity:**
     - **VPC:** Select `CampusPlacements-VPC`
     - **DB subnet group:** `campusplacements-db-subnet-group`
     - **Public access:** **No** (Ensures private database isolation)
     - **VPC security group:** Select **Choose existing** &rarr; pick `CampusPlacements-RDS-SG` (Deselect `default`)
     - **Availability Zone:** No preference
     - **Database port:** `3306`
   - **Additional configuration** (Expand this section):
     - **Initial database name:** `campusplacements_db`
     - Uncheck *Enable automated backups* if you want to avoid extra charges in lab demo
     - Leave encryption enabled
   - Click **Create database**.
4. The database takes about 5–8 minutes to create. When status is `Available`, click the database name and copy the **Endpoint** (e.g. `campusplacements-rds.c7xxxxxxx.us-east-1.rds.amazonaws.com`).

---

### Step 11 – Connect EC2 to RDS & Test Connectivity

#### [EC2 TERMINAL]
Test network connection and MySQL port connectivity directly from your EC2 prompt:

```bash
# 1. Test network reachability on port 3306
nc -zv <YOUR_RDS_ENDPOINT> 3306
# Expected output: Connection to <YOUR_RDS_ENDPOINT> 3306 port [tcp/mysql] succeeded!

# 2. Test MySQL client connection
mysql -h <YOUR_RDS_ENDPOINT> -u admin -p -e "SHOW DATABASES;"
# Enter your Master Password when prompted: PlacementSecure2024!
# Output should display:
# +--------------------+
# | Database           |
# +--------------------+
# | campusplacements_db|
# | information_schema |
# | performance_schema |
# +--------------------+
```

Now configure your application's `.env` on EC2:

```bash
cd /home/ubuntu/campusplacements
nano .env
```

Update `DATABASE_URL` with your RDS credentials and endpoint:
```env
SECRET_KEY=prod_placement_cloud_key_778899aabbcc
DATABASE_URL=mysql+pymysql://admin:PlacementSecure2024!@<YOUR_RDS_ENDPOINT>:3306/campusplacements_db
AWS_REGION=us-east-1
S3_BUCKET_NAME=
```
*(Save and exit nano with `Ctrl+O` & `Ctrl+X`).*

---

### Step 12 – Initialize RDS Database and Seed Records

#### [EC2 TERMINAL]
With the `.env` pointing to Amazon RDS MySQL, run the initialization and seeding scripts:

```bash
cd /home/ubuntu/campusplacements
source venv/bin/activate

# 1. Create all relational tables in Amazon RDS MySQL
python3 scripts/init_db.py

# 2. Seed database with the exact 30 AI & DS students, companies, jobs, applications, and placements
python3 scripts/seed_data.py
```

Verify that all tables and the 30 student records were written to RDS MySQL:
```bash
mysql -h <YOUR_RDS_ENDPOINT> -u admin -p -D campusplacements_db -e "SELECT student_id, name, department, cgpa, placement_status FROM students LIMIT 5;"
```

---

### Step 13 – Create S3 Bucket for Files and Datasets

Amazon S3 stores student resumes, company offer letters, and BDA datasets.

* **Bucket Name:** Globally unique (e.g., `campusplacements-bda-storage-<your-roll-no>`)
* **Region:** Same as EC2/RDS (e.g., `us-east-1`)
* **Block Public Access:** **ON** (Enabled – no public internet leaks)
* **Default Encryption:** SSE-S3 (Server-Side Encryption with Amazon S3 managed keys)

#### [AWS CONSOLE]
1. Open the **Amazon S3** Console &rarr; click **Create bucket**.
2. **Bucket name:** `campusplacements-bda-storage-23ad002` (Must be lowercase, unique across all AWS accounts).
3. **AWS Region:** `US East (N. Virginia) us-east-1` (Match your VPC region).
4. **Block Public Access settings for this bucket:** Leave **Block *all* public access** checked!
5. **Bucket Versioning:** Optional / Disable.
6. **Default encryption:** Server-side encryption with Amazon S3 managed keys (SSE-S3).
7. Click **Create bucket**.

#### [AWS CLI]
```bash
aws s3api create-bucket --bucket campusplacements-bda-storage-23ad002 --region us-east-1
```

---

### Step 14 – Give EC2 Access to S3 via IAM Role (Least Privilege)

Instead of hard-coding secret access keys, the EC2 instance automatically fetches temporary security credentials via an **IAM Instance Profile**.

#### A. Create the Least-Privilege IAM Policy
This policy grants access *only* to our specific project bucket.

#### [AWS CONSOLE]
1. Open the **IAM** Console &rarr; click **Policies** &rarr; **Create policy**.
2. Switch to the **JSON** tab and paste the following least-privilege policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "CampusPlacementsS3BucketAccess",
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::campusplacements-bda-storage-23ad002"
            ]
        },
        {
            "Sid": "CampusPlacementsS3ObjectAccess",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::campusplacements-bda-storage-23ad002/*"
            ]
        }
    ]
}
```
*(Replace `campusplacements-bda-storage-23ad002` with your exact bucket name).*
3. Click **Next** &rarr; Name the policy: `CampusPlacements-S3-Access-Policy` &rarr; click **Create policy**.

#### B. Create IAM Role and Attach to EC2
1. In the IAM Console &rarr; click **Roles** &rarr; **Create role**.
2. **Trusted entity type:** Select **AWS service**.
3. **Use case:** Select **EC2**. Click **Next**.
4. In the permissions search box, search for `CampusPlacements-S3-Access-Policy` and check the box. Click **Next**.
5. **Role name:** `EC2-S3-CampusPlacements-Role`.
6. Click **Create role**.
7. Now go to the **EC2 Console** &rarr; click **Instances**.
8. Select your `CampusPlacements-WebServer` instance.
9. Click **Actions** &rarr; **Security** &rarr; **Modify IAM role**.
10. In the dropdown, select `EC2-S3-CampusPlacements-Role` and click **Update IAM role**.

#### [EC2 TERMINAL]
Update your `/home/ubuntu/campusplacements/.env` file with the bucket name:
```env
S3_BUCKET_NAME=campusplacements-bda-storage-23ad002
AWS_REGION=us-east-1
```

Verify EC2 can interact with S3 without any credentials:
```bash
aws s3 ls s3://campusplacements-bda-storage-23ad002/
# If AWS CLI is installed, this will execute successfully using the attached IAM role!
```

---

### Step 15 – Upload Dataset/File to S3

You can test S3 upload directly through the web UI or via command line.

#### [EC2 TERMINAL]
```bash
# Upload a sample dataset file directly to S3
echo "student_id,name,cgpa,placed_company,ctc_lpa" > sample_bda_dataset.csv
echo "23AD002,Nighil Natarajan,9.1,Amazon Web Services,18.0" >> sample_bda_dataset.csv
aws s3 cp sample_bda_dataset.csv s3://campusplacements-bda-storage-23ad002/datasets/sample_bda_dataset.csv

# Verify file exists in S3
aws s3 ls s3://campusplacements-bda-storage-23ad002/datasets/
```

Or open the web application &rarr; navigate to **Documents & S3** &rarr; click **Upload to S3** &rarr; choose a resume PDF. The file is uploaded to your S3 bucket via `boto3`, and its reference is recorded in RDS MySQL!

---

### Step 16 – Production Deployment on EC2 with Gunicorn & Systemd

To ensure the web application runs continuously in the background, restarts on instance reboot, and recovers from errors, we configure **Gunicorn** managed by Linux **systemd**.

#### [EC2 TERMINAL]

#### 1. Create the Systemd Service File
```bash
sudo nano /etc/systemd/system/campusplacements.service
```

Paste the following service configuration:
```ini
[Unit]
Description=CampusPlacements Gunicorn Application Service
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/campusplacements
Environment="PATH=/home/ubuntu/campusplacements/venv/bin"
ExecStart=/home/ubuntu/campusplacements/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

#### 2. Start and Enable the Service
```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Start CampusPlacements service
sudo systemctl start campusplacements

# Enable service to start automatically on system reboot
sudo systemctl enable campusplacements

# Check real-time service status
sudo systemctl status campusplacements
```

#### 3. View Application Logs
```bash
journalctl -u campusplacements -f
```

---

### (Optional) Step 16B – Configure Nginx as Reverse Proxy (Port 80)
If you wish to serve the web application directly on standard HTTP port 80 (without appending `:5000` to the URL):

#### [EC2 TERMINAL]
```bash
sudo nano /etc/nginx/sites-available/campusplacements
```

Paste the Nginx reverse proxy configuration:
```nginx
server {
    listen 80;
    server_name _;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/ubuntu/campusplacements/static/;
        expires 30d;
    }
}
```

Enable the site and restart Nginx:
```bash
sudo ln -sf /etc/nginx/sites-available/campusplacements /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

Now you can open `http://<YOUR_EC2_PUBLIC_IP>` directly in your browser!

---

## Complete Application End-to-End Workflow

```text
Browser User (Evaluator / Coordinator)
      │
      │ 1. Navigates to http://<EC2-Public-IP> (HTTP Port 80)
      ▼
Internet Gateway (IGW)
      │
      │ 2. Routes packet to Public Subnet
      ▼
EC2 Virtual Machine (Ubuntu 22.04 LTS)
      ├──> Nginx Reverse Proxy (Port 80)
      └──> Gunicorn WSGI + Flask App (Port 5000)
            │
            ├──> 3. Reads/Writes Structured Data (MySQL Port 3306)
            │    └──> AWS Security Group Packet Filter (Only EC2 SG allowed)
            │         └──> Amazon RDS MySQL (Private Subnet)
            │              - Users, Students, Companies, Jobs
            │              - Applications, Interview Rounds, Placements
            │              - S3 Document Metadata Catalog
            │
            └──> 4. Streams Resumes & Datasets (HTTPS Port 443 via Boto3)
                 └──> IAM Instance Role: EC2-S3-CampusPlacements-Role
                      └──> Amazon S3 Bucket
                           - /resumes/
                           - /datasets/
                           - /reports/
```

---

## AWS Setup Verification Checklist

Use this checklist to track your manual AWS infrastructure deployment:

- [ ] **VPC created** (`CampusPlacements-VPC`, CIDR `10.0.0.0/16`, DNS hostnames enabled)
- [ ] **Public subnet created** (`CampusPlacements-Public-Subnet`, CIDR `10.0.1.0/24`, AZ `us-east-1a`, Auto-assign Public IP enabled)
- [ ] **Private subnet 1 created** (`CampusPlacements-Private-Subnet-1`, CIDR `10.0.2.0/24`, AZ `us-east-1a`)
- [ ] **Private subnet 2 created** (`CampusPlacements-Private-Subnet-2`, CIDR `10.0.3.0/24`, AZ `us-east-1b`)
- [ ] **Internet Gateway attached** (`CampusPlacements-IGW` attached to VPC)
- [ ] **Public route table configured** (`0.0.0.0/0` &rarr; `CampusPlacements-IGW`, associated with Public Subnet)
- [ ] **EC2 security group created** (`CampusPlacements-EC2-SG`: SSH port 22 from My IP, HTTP port 80 from `0.0.0.0/0`, TCP 5000)
- [ ] **RDS security group created** (`CampusPlacements-RDS-SG`: MySQL port 3306 ONLY from `CampusPlacements-EC2-SG`)
- [ ] **EC2 launched** (`t2.micro`, Ubuntu 22.04 LTS, Key pair saved, in Public Subnet)
- [ ] **EC2 SSH connection tested** (`ssh -i key.pem ubuntu@<Public-IP>`)
- [ ] **Web application installed** (Python 3, venv, requirements.txt, .env configured)
- [ ] **RDS created** (MySQL 8.0, `db.t3.micro`, DB Subnet Group across private subnets, Public access disabled)
- [ ] **EC2 &rarr; RDS connectivity tested** (`nc -zv <RDS-Endpoint> 3306` succeeds, MySQL client connects)
- [ ] **Database created** (`python3 scripts/init_db.py` and `python3 scripts/seed_data.py` executed successfully)
- [ ] **S3 bucket created** (`campusplacements-bda-storage-...`, Block All Public Access ON)
- [ ] **IAM role created** (`EC2-S3-CampusPlacements-Role` attached to EC2 with least-privilege S3 policy)
- [ ] **EC2 &rarr; S3 access tested** (`aws s3 ls` or application document upload verified)
- [ ] **Dataset uploaded to S3** (`bda_placement_dataset_2024.csv` visible in S3 bucket)
- [ ] **Application running on EC2** (Gunicorn + Systemd active and enabled)
- [ ] **Complete application workflow tested** (Browser &rarr; EC2 &rarr; RDS & S3 confirmed working)
