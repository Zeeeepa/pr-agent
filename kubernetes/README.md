# PR-Agent Kubernetes Deployment

This directory contains Kubernetes manifests for deploying PR-Agent components.

## Components

1. **GitHub App**: Handles GitHub webhooks and interactions
2. **ExecServer**: Provides execution services for GitHub workflows and actions

## Prerequisites

- Kubernetes cluster
- kubectl configured to access your cluster
- Cert-manager installed for TLS certificates
- Nginx Ingress Controller

## Deployment Steps

### 1. Create Secrets

First, create the necessary secrets:

```bash
# Copy the template and fill in your values
cp secrets-template.yaml secrets.yaml

# Edit the secrets file with your actual values
nano secrets.yaml

# Apply the secrets
kubectl apply -f secrets.yaml
```

### 2. Deploy the Applications

Deploy the GitHub App and ExecServer:

```bash
# Deploy GitHub App
kubectl apply -f github-app-deployment.yaml

# Deploy ExecServer
kubectl apply -f execserver-deployment.yaml
```

### 3. Verify Deployment

Check that the pods are running:

```bash
kubectl get pods -l app=pr-agent-github-app
kubectl get pods -l app=pr-agent-execserver
```

Check the services:

```bash
kubectl get svc
```

Check the ingress:

```bash
kubectl get ingress
```

## Configuration

### GitHub App Configuration

After deployment, you need to configure your GitHub App with the correct webhook URL:

1. Go to your GitHub App settings
2. Set the webhook URL to `https://github-app.pr-agent.example.com/webhook`
3. Ensure the webhook secret matches the one in your secrets

### ExecServer Configuration

The ExecServer requires Supabase for database storage:

1. Create a Supabase project
2. Set up the necessary tables (refer to the ExecServer documentation)
3. Update the Supabase URL and anon key in your secrets

## Scaling

You can scale the deployments as needed:

```bash
kubectl scale deployment/pr-agent-github-app --replicas=3
kubectl scale deployment/pr-agent-execserver --replicas=3
```

## Troubleshooting

### Check Logs

```bash
# GitHub App logs
kubectl logs -l app=pr-agent-github-app

# ExecServer logs
kubectl logs -l app=pr-agent-execserver
```

### Check Events

```bash
kubectl describe pod -l app=pr-agent-github-app
kubectl describe pod -l app=pr-agent-execserver
```

### Restart Deployments

```bash
kubectl rollout restart deployment/pr-agent-github-app
kubectl rollout restart deployment/pr-agent-execserver
```
