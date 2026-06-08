# Rollback Runbook — payment-service

**Trigger this runbook when:** Post-deployment health checks fail, error rate spikes,
P1 alert fires, or Release Manager decides to abort the release.

---

## Rollback Decision Criteria

| Metric              | Threshold            | Action if breached      |
|---------------------|----------------------|-------------------------|
| Health check        | HTTP 200             | Rollback if non-200 >2m |
| Error rate          | < 1% baseline        | Rollback if > 5%        |
| Response time (p95) | Within 10% baseline  | Rollback if > 50% rise  |
| P1 alert            | None                 | Immediate rollback      |

---

## Rollback Steps

| Step | Action                                                   | Time    | Owner        |
|------|----------------------------------------------------------|---------|--------------|
| 1    | Declare rollback — notify #releases channel              | 0 min   | Release Mgr  |
| 2    | Trigger `bash scripts/rollback.sh production`            | 1 min   | Ops / DevOps |
| 3    | Monitor rollback — watch health endpoint                 | 1–5 min | Ops Team     |
| 4    | Confirm previous version is live (`/version` endpoint)   | 6 min   | Release Mgr  |
| 5    | Run smoke tests against rolled-back version              | 8 min   | Ops Team     |
| 6    | Confirm production is stable                             | 10 min  | Release Mgr  |
| 7    | Raise incident ticket in ServiceNow (P1 or P2)           | 10 min  | Release Mgr  |
| 8    | Send "Rollback complete" comms to stakeholders           | 12 min  | Release Mgr  |
| 9    | Update Change Request to FAILED with notes               | 15 min  | Release Mgr  |

**Target rollback time: < 15 minutes**

---

## Post-Rollback Actions (within 24 hours)

- [ ] Root cause analysis (RCA) completed
- [ ] RCA shared with engineering and leadership
- [ ] Corrective actions logged in incident ticket
- [ ] Fix implemented, tested on staging, and re-scheduled for next window
- [ ] Post-Incident Review (PIR) meeting scheduled
