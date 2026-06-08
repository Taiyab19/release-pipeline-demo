# Deployment Runbook — payment-service

**Document owner:** Release Management Team  
**Version:** 1.0  
**Last updated:** 2025-01-01  
**Applies to:** All production deployments of `payment-service`

---

## Overview

This runbook defines the end-to-end procedure for deploying `payment-service` to the
Production environment. It must be followed for every production deployment to ensure
consistency, traceability, and rollback readiness.

---

## Pre-Deployment Checklist (T-24 hours)

Complete all items before raising the Change Request.

- [ ] All feature work merged to `release/*` branch
- [ ] Code review approved by at least 2 engineers
- [ ] Unit test coverage ≥ 80% confirmed in pipeline
- [ ] Staging deployment completed successfully
- [ ] Staging smoke tests passed (all green)
- [ ] Performance test results reviewed — no regression
- [ ] Database migration scripts reviewed and tested on staging
- [ ] Rollback plan documented (see [Rollback Runbook](rollback-runbook.md))
- [ ] On-call engineer confirmed for deployment window
- [ ] Release notes drafted and reviewed
- [ ] Change Request raised in ServiceNow and in APPROVED state
- [ ] Deployment window confirmed with stakeholders
- [ ] Monitoring dashboards bookmarked and alerts set

---

## Change Request Details

| Field                | Value                                      |
|----------------------|--------------------------------------------|
| Change type          | Standard / Normal                          |
| Risk rating          | Medium                                     |
| Deployment window    | As per agreed maintenance window           |
| Estimated duration   | 45–60 minutes (including validation)       |
| Rollback time        | < 15 minutes                               |
| Approver             | Change Advisory Board (CAB)                |
| Communication owner  | Release Manager                            |

---

## Deployment Window Communication

Send to all stakeholders **2 hours before** the deployment window:

```
Subject: [PLANNED] payment-service v{VERSION} Production Deployment — {DATE} {TIME}

Hi Team,

We are deploying payment-service v{VERSION} to Production on {DATE} between {START} and {END}.

Impact      : Minimal — zero-downtime deployment expected
Rollback    : Available within 15 minutes if needed
Change ref  : CHG{TICKET_NUMBER}

Please report any issues to #releases or contact {RELEASE_MANAGER_NAME}.

— Release Management Team
```

---

## Step-by-Step Deployment Procedure

### Phase 1: Pre-Deploy (T-30 min)

| Step | Action                                              | Owner          | Status |
|------|-----------------------------------------------------|----------------|--------|
| 1.1  | Confirm deployment window is still clear            | Release Mgr    | [ ]    |
| 1.2  | Verify Change Request is in APPROVED state          | Release Mgr    | [ ]    |
| 1.3  | Confirm on-call engineer is available               | Release Mgr    | [ ]    |
| 1.4  | Open monitoring dashboards (Splunk / Dynatrace)     | Ops Team       | [ ]    |
| 1.5  | Note current baseline metrics (response time, rpm)  | Ops Team       | [ ]    |
| 1.6  | Confirm artifact version in Artifactory             | Release Mgr    | [ ]    |
| 1.7  | Send "Deployment starting" comms to stakeholders    | Release Mgr    | [ ]    |

**Baseline metrics (fill before deploy):**
- Current response time (p95): _________ ms
- Current error rate: _________ %
- Current RPM: _________

---

### Phase 2: Deployment Execution

| Step | Action                                              | Command / Notes                          | Status |
|------|-----------------------------------------------------|------------------------------------------|--------|
| 2.1  | Trigger Jenkins pipeline                            | Jenkins → `payment-service` → Build Now  | [ ]    |
| 2.2  | Monitor Build stage                                 | Expected: ~2 min                         | [ ]    |
| 2.3  | Monitor Test stage                                  | Expected: ~3 min, all tests green        | [ ]    |
| 2.4  | Confirm Quality Gate passed                         | Coverage ≥ 80%                           | [ ]    |
| 2.5  | Approve Production stage in Jenkins                 | Input: GO / NO-GO + Change ticket ref    | [ ]    |
| 2.6  | Monitor deploy to Production                        | Expected: ~5 min                         | [ ]    |

**GO / NO-GO Decision Criteria:**

| Condition                       | GO if...                   | NO-GO if...              |
|---------------------------------|----------------------------|--------------------------|
| All tests passing               | ✅ All green                | ❌ Any test failing       |
| Quality gate                    | ✅ Coverage ≥ 80%           | ❌ Below threshold        |
| Staging smoke tests             | ✅ All passed               | ❌ Any failure            |
| Change request status           | ✅ APPROVED                 | ❌ Not approved           |
| On-call confirmed               | ✅ Confirmed                | ❌ No coverage            |
| Production incident in progress | ✅ No active incidents      | ❌ Active P1/P2           |

---

### Phase 3: Post-Deployment Validation (first 30 min)

| Step | Action                                              | Expected result                | Status |
|------|-----------------------------------------------------|--------------------------------|--------|
| 3.1  | Verify smoke tests pass in pipeline                 | All green                      | [ ]    |
| 3.2  | Check health endpoint                               | HTTP 200, status: healthy      | [ ]    |
| 3.3  | Check readiness endpoint                            | HTTP 200, ready: true          | [ ]    |
| 3.4  | Verify version endpoint shows new version           | version: {NEW_VERSION}         | [ ]    |
| 3.5  | Check response time (p95 vs baseline)               | Within 10% of baseline         | [ ]    |
| 3.6  | Check error rate (vs baseline)                      | < 1% error rate                | [ ]    |
| 3.7  | Check Splunk / Dynatrace for anomalies              | No alerts fired                | [ ]    |
| 3.8  | Confirm transaction processing working (if testable)| Sample transaction succeeds    | [ ]    |
| 3.9  | Send "Deployment complete" comms to stakeholders    | Email / Slack #releases        | [ ]    |
| 3.10 | Update Change Request to CLOSED                     | CHG{TICKET_NUMBER} → Closed    | [ ]    |

---

## Escalation Contacts

| Role                    | Name         | Contact                   |
|-------------------------|--------------|---------------------------|
| Release Manager         | Tayyab Karem | tayyab.karem@example.com  |
| On-call Engineer        | TBD          | PagerDuty                 |
| Infrastructure Lead     | TBD          | Slack: #infra             |
| Application Owner       | TBD          | Slack: #payment-service   |

---

## Rollback Trigger Criteria

Initiate rollback **immediately** if any of the following occur:

- Health endpoint returns non-200 for > 2 consecutive minutes
- Error rate exceeds 5% post-deployment
- Response time (p95) increases > 50% vs baseline
- Any P1 alert fires in Splunk / Dynatrace within 30 min of deployment
- Business reports payment processing failures

→ See [Rollback Runbook](rollback-runbook.md) for rollback procedure.

---

## Post-Deployment Review

Within 24 hours of a successful deployment, complete the following:

- [ ] Deployment retrospective notes captured
- [ ] Any issues encountered documented with resolution
- [ ] Release notes published to team wiki
- [ ] Metrics comparison (before vs after) recorded
- [ ] Lessons learned shared with the team
