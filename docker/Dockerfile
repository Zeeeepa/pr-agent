FROM python:3.12.10-slim AS base

RUN apt update && apt install --no-install-recommends -y git curl && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ADD pyproject.toml .
ADD requirements.txt .
ADD docs docs
RUN pip install --no-cache-dir . && rm pyproject.toml requirements.txt
ENV PYTHONPATH=/app

FROM base AS github_app
ADD pr_agent pr_agent
CMD ["python", "-m", "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-c", "pr_agent/servers/gunicorn_config.py", "--forwarded-allow-ips", "*", "pr_agent.servers.github_app:app"]

FROM base AS bitbucket_app
ADD pr_agent pr_agent
CMD ["python", "pr_agent/servers/bitbucket_app.py"]

FROM base AS bitbucket_server_webhook
ADD pr_agent pr_agent
CMD ["python", "pr_agent/servers/bitbucket_server_webhook.py"]

FROM base AS github_polling
ADD pr_agent pr_agent
CMD ["python", "pr_agent/servers/github_polling.py"]

FROM base AS gitlab_webhook
ADD pr_agent pr_agent
CMD ["python", "pr_agent/servers/gitlab_webhook.py"]

FROM base AS azure_devops_webhook
ADD pr_agent pr_agent
CMD ["python", "pr_agent/servers/azuredevops_server_webhook.py"]

FROM base AS test
ADD requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt && rm requirements-dev.txt
ADD pr_agent pr_agent
ADD tests tests

FROM base AS cli
ADD pr_agent pr_agent
ENTRYPOINT ["python", "pr_agent/cli.py"]

FROM node:18 AS ui-builder
WORKDIR /app
COPY pr_agent/execserver/ui /app
RUN npm ci && npm run build

FROM base AS ui
COPY --from=ui-builder /app/dist /app/pr_agent/execserver/ui/static
ADD pr_agent pr_agent
EXPOSE 8000
CMD ["python", "-m", "pr_agent.execserver.app"]
