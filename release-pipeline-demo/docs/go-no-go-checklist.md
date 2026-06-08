# Go / No-Go Checklist — Production Release

**Release:** payment-service v{VERSION}  
**Date:** {DATE}  
**Release Manager:** Tayyab Karem  
**Change Ref:** CHG{NUMBER}

---

## GO criteria — ALL must be ✅ before proceeding

| # | Criteria                                         | Status   | Notes |
|---|--------------------------------------------------|----------|-------|
| 1 | All unit tests passing (0 failures)              | [ ] ✅ / ❌ |       |
| 2 | Code coverage ≥ 80%                              | [ ] ✅ / ❌ |       |
| 3 | Staging deployment successful                    | [ ] ✅ / ❌ |       |
| 4 | Staging smoke tests all passed                   | [ ] ✅ / ❌ |       |
| 5 | Change Request in APPROVED state                 | [ ] ✅ / ❌ |       |
| 6 | No active P1/P2 incidents in Production          | [ ] ✅ / ❌ |       |
| 7 | On-call engineer confirmed and available         | [ ] ✅ / ❌ |       |
| 8 | Rollback plan documented and tested              | [ ] ✅ / ❌ |       |
| 9 | Stakeholder sign-off received                    | [ ] ✅ / ❌ |       |
|10 | Deployment window confirmed (no conflicts)       | [ ] ✅ / ❌ |       |

**Decision:**  
☐ **GO** — All criteria met. Proceeding with deployment.  
☐ **NO-GO** — One or more criteria not met. Deployment postponed.  

**Approved by:** _______________________  **Time:** _______

---
*Any single NO-GO criterion blocks the deployment. No exceptions without CAB escalation.*
