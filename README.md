# Release Pipeline Demo 🚀

> A production-grade CI/CD release pipeline built to demonstrate end-to-end release management,
> environment promotion, approval gates, rollback procedures, and deployment governance —
> the same practices used in enterprise FinTech environments.

---

## About This Project

This project simulates a real-world software release pipeline for a payment-processing web service.
It covers the full release lifecycle: build → test → code quality → artifact packaging →
environment promotion (Dev → Staging → Production) → post-deployment validation → rollback.

Built by **Tayyab Karem** — Release Management Specialist with 10+ years in FinTech and
Healthcare IT (Mastercard, CME). This repo is a practical demonstration of the release
engineering and DevOps skills applied in enterprise delivery.

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        RELEASE PIPELINE                             │
│                                                                     │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌────────────────┐  │
│  │  Build   │──▶│   Test   │──▶│  Quality │──▶│ Package/       │  │
│  │  Stage   │   │  Stage   │   │   Gate   │   │ Artifact Push  │  │
│  └──────────┘   └──────────┘   └──────────┘   └───────┬────────┘  │
│                                                         │           │
│  ┌──────────────────────────────────────────────────────▼────────┐ │
│  │                   ENVIRONMENT PROMOTION                       │ │
│  │                                                               │ │
│  │  ┌─────────┐  auto  ┌──────────┐  approval ┌─────────────┐  │ │
│  │  │   DEV   │───────▶│ STAGING  │──────────▶│  PRODUCTION │  │ │
│  │  │ (auto)  │        │ (smoke   │  (manual  │  (canary +  │  │ │
│  │  │         │        │  tests)  │  gate)    │  full roll) │  │ │
│  │  └─────────┘        └──────────┘           └─────────────┘  │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  POST-DEPLOY: Health checks → Smoke tests → SLA validation   │  │
│  │              → Rollback trigger if thresholds breached        │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## What This Demonstrates

| Release Management Skill         | Where It's Implemented                          |
|----------------------------------|-------------------------------------------------|
| CI/CD pipeline design            | `Jenkinsfile` — full multi-stage pipeline       |
| Environment promotion            | Dev → Staging → Prod stages with gates          |
| Manual approval gate (CAB)       | Jenkins `input` step before Production deploy   |
| Rollback procedure               | `scripts/rollback.sh` + automated trigger       |
| Post-deployment validation       | `scripts/smoke-test.sh` + health checks         |
| Artifact management              | Versioned builds, artifact archiving            |
| Release notes generation         | `scripts/generate-release-notes.sh`             |
| Code quality gate (SonarQube)    | Quality threshold enforcement in pipeline       |
| GitHub Actions alternative       | `.github/workflows/` — same logic, no Jenkins  |
| Deployment runbook               | `docs/deployment-runbook.md`                    |
| Go/No-Go checklist               | `docs/go-no-go-checklist.md`                    |
| Incident / rollback runbook      | `docs/rollback-runbook.md`                      |

---

## Repository Structure

```
release-pipeline-demo/
├── Jenkinsfile                        # Main Jenkins declarative pipeline
├── app/
│   ├── app.py                         # Sample Python web service
│   ├── requirements.txt               # Dependencies
│   └── test_app.py                    # Unit tests
├── jenkins/
│   ├── Jenkinsfile.multibranch        # Multi-branch pipeline variant
│   └── shared-library-example.groovy # Shared library pattern
├── scripts/
│   ├── deploy.sh                      # Deployment script (env-aware)
│   ├── smoke-test.sh                  # Post-deployment smoke tests
│   ├── rollback.sh                    # Automated rollback script
│   ├── health-check.sh                # SLA health monitoring
│   └── generate-release-notes.sh     # Auto release notes from Git log
├── docs/
│   ├── deployment-runbook.md          # Step-by-step deployment guide
│   ├── go-no-go-checklist.md          # Pre-release approval checklist
│   └── rollback-runbook.md            # Incident rollback procedure
├── .github/
│   ├── workflows/
│   │   └── ci-cd.yml                  # GitHub Actions equivalent
│   ├── ISSUE_TEMPLATE/
│   │   └── change-request.md          # Change request template
│   └── pull_request_template.md       # PR template with release gates
└── README.md
```

---

## Key Pipeline Features

### 1. Multi-Environment Promotion
- **Dev**: Triggered on every commit to `develop` branch — fully automatic
- **Staging**: Triggered on merge to `release/*` branch — includes smoke tests
- **Production**: Requires manual approval (simulates CAB gate) + canary validation

### 2. Quality Gate (SonarQube-style)
Pipeline fails automatically if:
- Unit test coverage drops below **80%**
- Any critical code vulnerabilities detected
- Build lint errors present

### 3. Approval Gate Before Production
```groovy
stage('Production Approval') {
    input message: 'Deploy to Production?',
          submitter: 'release-manager,cab-approvers'
}
```
Simulates the CAB (Change Advisory Board) approval process used at Mastercard.

### 4. Automated Rollback
If post-deployment health checks fail:
- Pipeline triggers `rollback.sh` automatically
- Previous artifact version is redeployed
- Incident ticket is raised via webhook
- Stakeholder notification is sent

---

## How to Run Locally

### Prerequisites
- Docker Desktop installed
- Git

### Quick Start
```bash
# Clone the repo
git clone https://github.com/tayyab-karem/release-pipeline-demo.git
cd release-pipeline-demo

# Run Jenkins locally via Docker
docker run -d \
  --name jenkins-demo \
  -p 8080:8080 \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts

# Open Jenkins at http://localhost:8080
# Create a Pipeline job pointing to this repo's Jenkinsfile
```

### Run the App Directly
```bash
cd app
pip install -r requirements.txt
python app.py
# App runs at http://localhost:5000
```

### Run Tests
```bash
cd app
pip install pytest pytest-cov
pytest test_app.py -v --cov=app --cov-report=term-missing
```

---

## Branching Strategy

```
main          ──────────────────────────────────── (production-ready)
                  ↑ merge via PR + approval
release/1.2   ────────────────────
                  ↑ cut from develop
develop       ──────────────────────────────────── (integration)
                  ↑ feature merges
feature/*     ────  ────  ────                     (short-lived)
hotfix/*      ────                                 (emergency fixes → main)
```

---

## Tools & Technologies

`Jenkins` · `GitHub Actions` · `Python` · `pytest` · `Docker` · `SonarQube` (quality gate pattern) ·
`Git` · `Bash` · `ITSM/ITIL practices` · `ServiceNow` (webhook pattern)

---

## Author

**Tayyab Karem** — Release Management Specialist | DevOps & Production Support | ITSM  
📍 Pune, India | 🔗 [LinkedIn](https://www.linkedin.com/in/tayyab-karem/) | Available immediately

> *"Good releases are invisible. Great release engineers make them that way."*
