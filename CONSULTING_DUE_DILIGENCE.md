# Free Audit Framework — What to Look For

Use this during your free 20-min audits to uncover consulting opportunities.

---

## Questions to Ask (During Call)

### Current State
1. "How many incidents does your team handle monthly?"
2. "What's your average time-to-resolution (MTTR)?"
3. "Who's on-call? How often are they paged?"
4. "What's your deployment frequency? (weekly/daily/hourly)"
5. "Do you have any automated incident response, or is it all manual?"

### Pain Points
6. "What's the most painful part of your incident response workflow?"
7. "Have you had incidents that could've been auto-resolved?"
8. "How much engineering time is spent on ops vs feature development?"
9. "What gaps do you have in your monitoring/observability?"

### Technical Stack
10. "What's your current monitoring stack? (Prometheus, DataDog, CloudWatch, etc.)"
11. "Are you using any AI/ML for anomaly detection?"
12. "Containerized? (What orchestration — K8s, ECS, etc.)"

### Budget/Decision
13. "If you could reduce MTTR by 70%, what would that be worth?"
14. "Who owns DevOps budget in your org?"
15. "Timeline to upgrade your incident response system?"

---

## Red Flags for Easy Sales
✅ **They have:**
- High incident frequency (>5/month)
- Manual incident response (spreadsheets, Slack)
- No LLM/AI in their stack
- On-call fatigue complaints
- AWS/GCP (cloud-native = perfect fit)

---

## Consulting Upsell Opportunities

| Finding | Upsell |
|---------|--------|
| "We handle 30 incidents/month manually" | Full DevSecOps stack + integration = 4-8 weeks, $15-30k |
| "Our MTTR is 2+ hours" | Automated runbooks + AI = 2-4 weeks, $8-15k |
| "We don't have observability at all" | Prometheus + Grafana + Loki setup = 2 weeks, $5-10k |
| "No one wants on-call duty" | Full automation + Slack bot = 3-6 weeks, $12-25k |

---

## Audit Report Structure

After the call, send a 1-page PDF:

```
[Your Logo/Name]
DevSecOps Audit Report — [Company Name]

EXECUTIVE SUMMARY
- Current incident frequency: X per month
- Estimated cost of unresolved incidents: $Y
- Recommended focus areas: [3 bullets]

FINDINGS
1. Monitoring gaps: [specific to their stack]
2. Automation opportunities: [quick wins]
3. AI/ML readiness: [their current state]

RECOMMENDATIONS (Priority Order)
- Quick Win (1-2 weeks): [specific action + ROI]
- Medium (2-4 weeks): [specific action + ROI]
- Strategic (1-3 months): [specific action + ROI]

ESTIMATED IMPACT
- MTTR reduction: X hours → Y hours
- Engineer capacity freed: Z hours/month
- Annual cost savings: $Y

NEXT STEPS + CONTACT
```

---

## Following Up After Audit

Email template (3 days after call):

```
Hi [Name],

Thanks for the call last week. I really liked how [specific compliment].

Attached is your DevSecOps audit. A few highlights:
• You're losing ~[X] engineering hours/month to manual incident response
• Quick win we discussed: [automation opportunity] could save $Y/month
• I think [specific recommendation] is your highest-ROI move

If you'd like help implementing any of these, I'm offering implementation 
packages starting at $[price]. Otherwise, I hope the audit helps you 
prioritize your DevOps roadmap.

Feel free to reach out anytime.

— Qasim
```

**If they go silent:** One follow-up after 5 days. If still no response, move on.
