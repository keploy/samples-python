FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
# pip's fetches follow keploy's CI fetch rule (keploy/integrations'
# .ci/scripts/pip-fetch-rule_test.sh says why), written inline because a
# build context cannot reach a script: at most 5 attempts, waiting
# attempt x 10 s between them. ARG, not ENV: RUN sees it, the image does
# not keep it; pip 25.1 and later resume a cut download with it.
ARG PIP_RESUME_RETRIES=5
RUN n=0; until pip install --no-cache-dir -r requirements.txt; do rc=$?; n=$((n+1)); [ "$n" -lt 5 ] || { echo "pip install failed after 5 attempts (exit $rc)"; exit 1; }; echo "pip install failed (attempt $n of 5, exit $rc), retrying in $((n*10))s"; sleep $((n*10)); done

COPY main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
