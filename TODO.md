# DevSecOps Critical Fixes TODO
Completed: 0/8 ✅

## Planned Steps (from approved audit plan)

1. [✅] Fix imports in backend/routes/api.py (cost_anomaly, cve_scanner)
2. [✅] Fix import in backend/routes/audit.py (pdf_generator)
3. [✅] Add asyncpg==0.29.0 to backend/requirements.txt
4. [✅] Fix PDF recommendations to dicts in backend/routes/audit.py
5. [✅] Remove fake /incidents route from backend/routes/api.py
6. [✅] Update Dockerfile.backend HEALTHCHECK to /health/status
7. [✅] Update Dockerfile.backend CMD: remove --reload, add --workers 2
8. [✅] Test deployment: docker-compose up, verify endpoints

## Post-Edit
- Manual: Regenerate SECRET_KEY, fix .env duplicates, change docker-compose passwords
- Run: docker-compose down -v &amp;&amp; docker-compose build --no-cache &amp;&amp; docker-compose up
- Verify: curl -f http://localhost:8000/health/status

