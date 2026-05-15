# Policy-as-Code Checker

A Terraform security scanner with a live React dashboard, paste any Terraform HCL code and get an instant policy compliance report showing which resources violate security best practices, with severity ratings (Critical/High/Medium/Low), specific remediation advice per finding, and syntax-highlighted code review. The backend runs a custom policy engine written in Python, stores scan history in DynamoDB, and exposes a REST API via Lambda and API Gateway. The entire stack deploys automatically via GitHub Actions CI/CD on every push.
> **Note on CloudFront:** This project was originally designed to use **AWS CloudFront** as a CDN layer in front of the S3 static website, providing HTTPS, global edge caching, and cache invalidation on every CI/CD deployment. However, new AWS accounts require manual verification before CloudFront distributions can be created. While awaiting approval, the React frontend is served directly from S3 static website hosting over HTTP. Once CloudFront access is granted, re-enabling it requires only uncommenting the CloudFront resource block in `terraform/main.tf` and adding a cache invalidation step to the GitHub Actions workflow — all other infrastructure remains unchanged.

---

## Live Demo

**[Open Policy-as-Code Checker →](http://pac-checker-frontend-b1dec6ad.s3-website.us-east-2.amazonaws.com/)**
> **Note:** The custom HCL parser handles common Terraform patterns, nested blocks, boolean attributes, string values, and CIDR lists. Full HCL compliance would use the official HashiCorp HCL parser via a Go Lambda layer or the `python-hcl2` library. The custom parser was chosen to demonstrate parsing fundamentals without external dependencies.

---

## What It Does

- **Paste and scan** — submit any Terraform HCL through the UI and get results in seconds
- **Policy engine** — custom Python rules check S3, RDS, Security Groups, and general resources against security best practices
- **Severity classification** — findings rated Critical, High, Medium, or Low with specific remediation advice per violation
- **Scan history** — full history of all scans with scores, severity breakdowns, and drill-down detail views
- **Syntax highlighted code** — scanned Terraform code displayed with syntax highlighting in the scan detail view
- **Example configs** — built-in insecure and secure Terraform examples for immediate demo without writing code
- **CI/CD pipeline** — GitHub Actions deploys backend via Terraform and frontend via S3 sync on every push

---

## Architecture

```
Developer pushes to GitHub
        │
        ▼
GitHub Actions CI/CD
        │
        ├── Job 1: Deploy Backend (Terraform)
        │   ├── terraform init (S3 remote state)
        │   ├── terraform apply
        │   └── outputs: api_url, frontend_bucket
        │
        └── Job 2: Deploy Frontend (React + Vite)
            ├── npm ci
            ├── npm run build (injects api_url at build time)
            └── aws s3 sync → S3 static website

                    ┌──────────────────────────────────────────────┐
                    │                    AWS                       │
                    │                                              │
  Browser ─────────► S3 Static Website (React + Vite)             │
                    │         │                                    │
                    │         │ POST /scan, GET /scans, GET /dash  │
                    │         ▼                                    │
                    │  API Gateway (REST)                          │
                    │         │                                    │
                    │         ▼                                    │
                    │  Lambda — scan_api                           │
                    │  Routes requests, invokes scanner            │
                    │         │                                    │
                    │         ▼                                    │
                    │  Lambda — scanner                            │
                    │  ├── Parses HCL (brace-counting parser)     │
                    │  ├── Runs S3 policy rules                   │
                    │  ├── Runs RDS policy rules                  │
                    │  ├── Runs Security Group rules              │
                    │  └── Runs General (tagging) rules           │
                    │         │                                    │
                    │         ▼                                    │
                    │  DynamoDB                                    │
                    │  SCAN#{id} METADATA — scan summary           │
                    │  SCAN#{id} FINDING#{n} — individual rules   │
                    │                                              │
                    │  CloudWatch Alarm — API error rate           │
                    │  Terraform State → S3 Backend               │
                    └──────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS, React Query, React Syntax Highlighter |
| API | AWS API Gateway (REST) |
| Compute | AWS Lambda (Python 3.11) |
| Database | AWS DynamoDB (PAY_PER_REQUEST) |
| Hosting | AWS S3 (static website) |
| Observability | AWS CloudWatch Alarms |
| Infrastructure as Code | Terraform (S3 remote state) |
| CI/CD | GitHub Actions |

---

## Project Structure

```
policy-as-code-checker/
├── .github/
│   └── workflows/
│       └── deploy.yml              # CI/CD — Terraform backend + React frontend
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx       # Overview stats + recent scans
│   │   │   ├── ScanHistory.jsx     # All scans with severity indicators
│   │   │   ├── ScanDetail.jsx      # Full findings + syntax highlighted code
│   │   │   └── NewScan.jsx         # Submit Terraform code for scanning
│   │   ├── components/
│   │   │   ├── StatusBadge.jsx     # PASS/FAIL/status colored badge
│   │   │   └── SeverityBadge.jsx   # CRITICAL/HIGH/MEDIUM/LOW badge
│   │   ├── App.jsx                 # Router + navbar
│   │   ├── main.jsx                # React Query provider
│   │   └── index.css               # Tailwind directives
│   └── .env.production             # VITE_API_URL injected by CI/CD
├── lambda/
│   ├── scanner.py                  # HCL parser + policy engine + DynamoDB storage
│   └── scan_api.py                 # REST API handler — routes, dashboard, history
├── policies/
│   ├── s3_rules.py                 # S3 bucket security checks
│   ├── rds_rules.py                # RDS instance security checks
│   ├── security_group_rules.py     # Security group ingress checks
│   └── general_rules.py            # Tagging and general compliance checks
├── terraform/
│   ├── main.tf                     # All AWS resources + S3 remote backend
│   ├── variables.tf
│   └── outputs.tf
├── .gitignore
└── README.md
```

---

## Policy Rules

### S3 Rules
| Rule ID | Rule | Severity |
|---|---|---|
| S3-001 | S3 Bucket Public ACL | Critical |
| S3-002 | S3 Bucket Versioning Disabled | Medium |
| S3-003 | S3 Bucket Force Destroy Enabled | High |

### RDS Rules
| Rule ID | Rule | Severity |
|---|---|---|
| RDS-001 | RDS Encryption at Rest Disabled | High |
| RDS-002 | RDS Multi-AZ Disabled | Medium |
| RDS-003 | RDS Publicly Accessible | Critical |
| RDS-004 | RDS Deletion Protection Disabled | Medium |

### Security Group Rules
| Rule ID | Rule | Severity |
|---|---|---|
| SG-001 | SSH Open to World (0.0.0.0/0) | Critical |
| SG-002 | RDP Open to World (0.0.0.0/0) | Critical |
| SG-003 | All Traffic Open to World | Critical |

### General Rules
| Rule ID | Rule | Severity |
|---|---|---|
| GEN-001 | Missing Required Tags (Name, Environment) | Low |

---

## Example Scans

### Insecure Configuration (built into UI)
Triggers multiple critical and high findings:
- Public S3 ACL → **S3-001 Critical**
- RDS publicly accessible → **RDS-003 Critical**
- SSH open to 0.0.0.0/0 → **SG-001 Critical**
- RDP open to 0.0.0.0/0 → **SG-002 Critical**
- RDS encryption disabled → **RDS-001 High**
- Missing tags → **GEN-001 Low**

### Secure Configuration (100% pass)
```hcl
resource "aws_s3_bucket" "good" {
  bucket        = "my-secure-bucket"
  acl           = "private"
  force_destroy = false
  versioning {
    enabled = true
  }
  tags = {
    Name = "secure-bucket"
    Environment = "production"
  }
}

resource "aws_db_instance" "good" {
  identifier          = "my-secure-db"
  engine              = "postgres"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  username            = "admin"
  password            = "SecurePass123!"
  storage_encrypted   = true
  publicly_accessible = false
  deletion_protection = true
  multi_az            = true
  tags = {
    Name = "secure-db"
    Environment = "production"
  }
}
```

---

## API Reference

### POST /scan
Submit Terraform code for scanning. Returns full findings synchronously.
```json
{
  "scan_name": "Production review",
  "terraform_code": "resource \"aws_s3_bucket\" ..."
}
```

### GET /dashboard
Returns aggregate stats — total scans, average score, total failures, critical findings count, and 5 most recent scans.

### GET /scans
Returns all scans ordered by most recent with severity breakdown per scan.

### GET /scans/{scan_id}
Returns full scan detail including all findings and the original scanned code.

### GET /health
Health check endpoint.

---

## How to Deploy

### Prerequisites
- AWS account with CLI configured
- Terraform installed
- Node.js 20+ installed

### Steps

**1. Create Terraform state bucket**
```bash
aws s3 mb s3://pac-tfstate-ahnaf --region us-east-2
```

**2. Update bucket name in terraform/main.tf**
```hcl
terraform {
  backend "s3" {
    bucket = "pac-tfstate-ahnaf"
    key    = "pac/terraform.tfstate"
    region = "us-east-2"
  }
}
```

**3. Create GitHub repo and add secrets**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

**4. Initialize Terraform**
```bash
cd terraform
terraform init
cd ..
```

**5. Push — CI/CD handles the rest**
```bash
git add .
git commit -m "Initial commit"
git branch -M master
git remote add origin http://pac-checker-frontend-b1dec6ad.s3-website.us-east-2.amazonaws.com/
git push -u origin master
```

**6. Get your live URL**
```bash
cd terraform
terraform output frontend_url
```

---

## Screenshots

**Dashboard — scan overview with aggregate statistics:**

<img width="1055" height="586" alt="Dashboard" src="https://github.com/user-attachments/assets/f4a8c4f8-4c04-4d53-a4aa-491badf79463" />

**New Scan — insecure Terraform config loaded and ready to scan:**

<img width="1167" height="766" alt="New Scan page" src="https://github.com/user-attachments/assets/8b30259d-93c7-49a4-8c45-45d7cb1656aa" />

**Scan Detail — critical findings with severity badges and remediation advice:**

<img width="1183" height="820" alt="Scan Detail page" src="https://github.com/user-attachments/assets/71174ed4-d6b3-4dcf-85fe-ffeb956bab2c" />

**Scan Detail — 100% passing secure configuration:**

<img width="1053" height="425" alt="Scan Detail page 3" src="https://github.com/user-attachments/assets/18ede7c8-6151-4c03-a3c6-afc76128bfb5" />

**GitHub Actions — both jobs green:**

<img width="757" height="213" alt="CICD pipeline" src="https://github.com/user-attachments/assets/227abbe5-21a6-4685-a8f9-d42311e7480b" />

---

## Key Concepts Demonstrated

- **Policy-as-code** — security rules defined as code, version controlled, and automatically enforced on every scan
- **Custom HCL parser** — brace-counting parser correctly handles nested Terraform blocks (versioning, tags, ingress) without external dependencies
- **Serverless architecture** — Lambda + API Gateway + DynamoDB with no servers to manage or scale
- **CI/CD pipeline** — two-job GitHub Actions workflow where Terraform backend outputs feed directly into the React frontend build via job outputs
- **CORS** — API Lambda returns correct preflight and response headers for cross-origin browser requests
- **DynamoDB data modeling** — composite key design separating scan metadata from individual findings for efficient querying
- **React Query** — client-side data fetching with loading states, error handling, and automatic retry
- **Infrastructure as code** — all AWS resources provisioned via Terraform with S3 remote state shared between local and CI/CD environments
