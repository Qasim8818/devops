# TODO - Deploy-Readiness & Correctness Review

## Step 1 — Import/packaging correctness (backend)
- Inspect backend package structure.
- Fix imports across backend to use `backend.*` or relative imports so `uvicorn main:app` and `python -m backend.main` work.
- Ensure entrypoint/WORKDIR remains consistent with Dockerfile.backend.

## Step 2 — API smoke tests
- Add a lightweight local smoke test script that calls each API endpoint on a running backend.
- Validate HTTP 200 and basic response shape (keys existence).
- Integrate the script into verify.sh.

## Step 3 — Production readiness gaps
- Review verify.sh + documentation for missing prerequisites (.env example, migrations, auth assumptions).
- Add checklist items for client handoff.

## Step 4 — Run verification (local)
- Run py_compile + smoke tests in CI-like mode.
- If Docker unavailable, validate by running backend via uvicorn in-process and executing smoke tests.

## Step 5 — Final report / completion
- Produce a final deployability report with exact commands to run on client infra.
- List any remaining items that require client environment changes.

