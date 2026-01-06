# Phase 4: Local Kubernetes Deployment Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Deploy the AI-powered todo chatbot to a local Kubernetes cluster using Docker, Minikube, and Helm with proper health checks and secrets management.

**Architecture:** Containerize frontend (Next.js) and backend (FastAPI) as separate Docker images. Deploy to Minikube using a Helm chart with ConfigMaps for configuration and Secrets for sensitive data. Use Kubernetes Services for internal communication and Ingress for external access.

**Tech Stack:** Docker, Minikube, Helm 3, kubectl, Next.js 14, FastAPI, PostgreSQL (Neon - external)

---

## Task 1: Verify Prerequisites

**Files:**
- None (system verification only)

**Step 1: Check Docker is installed and running**

Run: `docker --version && docker info | head -5`
Expected: Docker version 20+ and daemon running

**Step 2: Check Minikube is installed**

Run: `minikube version`
Expected: Minikube version v1.30+

If not installed:
```bash
# WSL2/Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

**Step 3: Check kubectl is installed**

Run: `kubectl version --client`
Expected: kubectl version v1.28+

If not installed:
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

**Step 4: Check Helm is installed**

Run: `helm version`
Expected: Helm version v3.12+

If not installed:
```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

**Step 5: Commit prerequisite verification**

No files to commit - verification only.

---

## Task 2: Create Frontend Dockerfile

**Files:**
- Create: `frontend/Dockerfile`
- Test: Manual docker build

**Step 1: Create the Dockerfile**

Create file `frontend/Dockerfile`:

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Build application
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# Production stage
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Copy built assets
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

**Step 2: Update next.config.ts for standalone output**

Modify `frontend/next.config.ts`:

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
};

export default nextConfig;
```

**Step 3: Build image to verify Dockerfile works**

Run: `cd frontend && docker build -t todo-frontend:latest .`
Expected: Build completes successfully

**Step 4: Commit frontend Dockerfile**

```bash
git add frontend/Dockerfile frontend/next.config.ts
git commit -m "feat(docker): add frontend Dockerfile with standalone build"
```

---

## Task 3: Update Backend Dockerfile for Production

**Files:**
- Modify: `backend/Dockerfile`
- Test: Manual docker build

**Step 1: Update Dockerfile with health check**

Modify `backend/Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run application
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Step 2: Build image to verify Dockerfile works**

Run: `cd backend && docker build -t todo-backend:latest .`
Expected: Build completes successfully

**Step 3: Commit backend Dockerfile update**

```bash
git add backend/Dockerfile
git commit -m "feat(docker): update backend Dockerfile with health check and non-root user"
```

---

## Task 4: Create Helm Chart Structure

**Files:**
- Create: `k8s/hackathon-todo/Chart.yaml`
- Create: `k8s/hackathon-todo/values.yaml`
- Create: `k8s/hackathon-todo/.helmignore`

**Step 1: Create chart directory structure**

Run: `mkdir -p k8s/hackathon-todo/templates`

**Step 2: Create Chart.yaml**

Create file `k8s/hackathon-todo/Chart.yaml`:

```yaml
apiVersion: v2
name: hackathon-todo
description: AI-powered todo chatbot with MCP and OpenAI Agents
type: application
version: 1.0.0
appVersion: "1.0.0"
keywords:
  - todo
  - ai
  - chatbot
  - mcp
  - openai
maintainers:
  - name: Hackathon Team
```

**Step 3: Create values.yaml**

Create file `k8s/hackathon-todo/values.yaml`:

```yaml
# Backend configuration
backend:
  name: backend
  replicas: 2
  image:
    repository: todo-backend
    tag: latest
    pullPolicy: Never  # Use local images in Minikube
  service:
    type: ClusterIP
    port: 8000
  resources:
    limits:
      cpu: "500m"
      memory: "512Mi"
    requests:
      cpu: "250m"
      memory: "256Mi"
  env:
    # Non-sensitive config (sensitive values in secrets)
    LOG_LEVEL: "INFO"

# Frontend configuration
frontend:
  name: frontend
  replicas: 2
  image:
    repository: todo-frontend
    tag: latest
    pullPolicy: Never
  service:
    type: ClusterIP
    port: 3000
  resources:
    limits:
      cpu: "300m"
      memory: "256Mi"
    requests:
      cpu: "100m"
      memory: "128Mi"

# Ingress configuration
ingress:
  enabled: true
  className: nginx
  host: todo.local
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /

# Secrets (override in values-secrets.yaml or --set)
secrets:
  databaseUrl: ""
  openaiApiKey: ""
  authSecret: ""
  jwtSecret: ""
```

**Step 4: Create .helmignore**

Create file `k8s/hackathon-todo/.helmignore`:

```
# Patterns to ignore when building packages
*.md
*.txt
.git/
.gitignore
values-secrets.yaml
```

**Step 5: Commit Helm chart structure**

```bash
git add k8s/
git commit -m "feat(k8s): create Helm chart structure with Chart.yaml and values.yaml"
```

---

## Task 5: Create Backend Kubernetes Templates

**Files:**
- Create: `k8s/hackathon-todo/templates/backend-deployment.yaml`
- Create: `k8s/hackathon-todo/templates/backend-service.yaml`

**Step 1: Create backend deployment template**

Create file `k8s/hackathon-todo/templates/backend-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-{{ .Values.backend.name }}
  labels:
    app: {{ .Release.Name }}
    component: {{ .Values.backend.name }}
spec:
  replicas: {{ .Values.backend.replicas }}
  selector:
    matchLabels:
      app: {{ .Release.Name }}
      component: {{ .Values.backend.name }}
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}
        component: {{ .Values.backend.name }}
    spec:
      containers:
        - name: {{ .Values.backend.name }}
          image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
          imagePullPolicy: {{ .Values.backend.image.pullPolicy }}
          ports:
            - containerPort: {{ .Values.backend.service.port }}
              protocol: TCP
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: {{ .Release.Name }}-secrets
                  key: database-url
            - name: OPENAI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: {{ .Release.Name }}-secrets
                  key: openai-api-key
            - name: BETTER_AUTH_SECRET
              valueFrom:
                secretKeyRef:
                  name: {{ .Release.Name }}-secrets
                  key: auth-secret
            - name: JWT_SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: {{ .Release.Name }}-secrets
                  key: jwt-secret
            - name: LOG_LEVEL
              value: "{{ .Values.backend.env.LOG_LEVEL }}"
          resources:
            {{- toYaml .Values.backend.resources | nindent 12 }}
          livenessProbe:
            httpGet:
              path: /health
              port: {{ .Values.backend.service.port }}
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /health
              port: {{ .Values.backend.service.port }}
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3
```

**Step 2: Create backend service template**

Create file `k8s/hackathon-todo/templates/backend-service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}-{{ .Values.backend.name }}
  labels:
    app: {{ .Release.Name }}
    component: {{ .Values.backend.name }}
spec:
  type: {{ .Values.backend.service.type }}
  ports:
    - port: {{ .Values.backend.service.port }}
      targetPort: {{ .Values.backend.service.port }}
      protocol: TCP
      name: http
  selector:
    app: {{ .Release.Name }}
    component: {{ .Values.backend.name }}
```

**Step 3: Verify templates are valid YAML**

Run: `helm lint k8s/hackathon-todo`
Expected: "0 chart(s) failed" with possible INFO messages

**Step 4: Commit backend templates**

```bash
git add k8s/hackathon-todo/templates/backend-*.yaml
git commit -m "feat(k8s): add backend deployment and service templates"
```

---

## Task 6: Create Frontend Kubernetes Templates

**Files:**
- Create: `k8s/hackathon-todo/templates/frontend-deployment.yaml`
- Create: `k8s/hackathon-todo/templates/frontend-service.yaml`

**Step 1: Create frontend deployment template**

Create file `k8s/hackathon-todo/templates/frontend-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-{{ .Values.frontend.name }}
  labels:
    app: {{ .Release.Name }}
    component: {{ .Values.frontend.name }}
spec:
  replicas: {{ .Values.frontend.replicas }}
  selector:
    matchLabels:
      app: {{ .Release.Name }}
      component: {{ .Values.frontend.name }}
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}
        component: {{ .Values.frontend.name }}
    spec:
      containers:
        - name: {{ .Values.frontend.name }}
          image: "{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag }}"
          imagePullPolicy: {{ .Values.frontend.image.pullPolicy }}
          ports:
            - containerPort: {{ .Values.frontend.service.port }}
              protocol: TCP
          env:
            - name: NEXT_PUBLIC_API_URL
              value: "http://{{ .Release.Name }}-{{ .Values.backend.name }}:{{ .Values.backend.service.port }}"
          resources:
            {{- toYaml .Values.frontend.resources | nindent 12 }}
          livenessProbe:
            httpGet:
              path: /
              port: {{ .Values.frontend.service.port }}
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /
              port: {{ .Values.frontend.service.port }}
            initialDelaySeconds: 5
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 3
```

**Step 2: Create frontend service template**

Create file `k8s/hackathon-todo/templates/frontend-service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}-{{ .Values.frontend.name }}
  labels:
    app: {{ .Release.Name }}
    component: {{ .Values.frontend.name }}
spec:
  type: {{ .Values.frontend.service.type }}
  ports:
    - port: {{ .Values.frontend.service.port }}
      targetPort: {{ .Values.frontend.service.port }}
      protocol: TCP
      name: http
  selector:
    app: {{ .Release.Name }}
    component: {{ .Values.frontend.name }}
```

**Step 3: Verify templates are valid**

Run: `helm lint k8s/hackathon-todo`
Expected: No errors

**Step 4: Commit frontend templates**

```bash
git add k8s/hackathon-todo/templates/frontend-*.yaml
git commit -m "feat(k8s): add frontend deployment and service templates"
```

---

## Task 7: Create Secrets and Ingress Templates

**Files:**
- Create: `k8s/hackathon-todo/templates/secrets.yaml`
- Create: `k8s/hackathon-todo/templates/ingress.yaml`

**Step 1: Create secrets template**

Create file `k8s/hackathon-todo/templates/secrets.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ .Release.Name }}-secrets
  labels:
    app: {{ .Release.Name }}
type: Opaque
stringData:
  database-url: {{ .Values.secrets.databaseUrl | quote }}
  openai-api-key: {{ .Values.secrets.openaiApiKey | quote }}
  auth-secret: {{ .Values.secrets.authSecret | quote }}
  jwt-secret: {{ .Values.secrets.jwtSecret | quote }}
```

**Step 2: Create ingress template**

Create file `k8s/hackathon-todo/templates/ingress.yaml`:

```yaml
{{- if .Values.ingress.enabled -}}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ .Release.Name }}-ingress
  labels:
    app: {{ .Release.Name }}
  {{- with .Values.ingress.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  ingressClassName: {{ .Values.ingress.className }}
  rules:
    - host: {{ .Values.ingress.host }}
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: {{ .Release.Name }}-{{ .Values.backend.name }}
                port:
                  number: {{ .Values.backend.service.port }}
          - path: /health
            pathType: Exact
            backend:
              service:
                name: {{ .Release.Name }}-{{ .Values.backend.name }}
                port:
                  number: {{ .Values.backend.service.port }}
          - path: /
            pathType: Prefix
            backend:
              service:
                name: {{ .Release.Name }}-{{ .Values.frontend.name }}
                port:
                  number: {{ .Values.frontend.service.port }}
{{- end }}
```

**Step 3: Verify templates are valid**

Run: `helm lint k8s/hackathon-todo`
Expected: No errors

**Step 4: Commit secrets and ingress templates**

```bash
git add k8s/hackathon-todo/templates/secrets.yaml k8s/hackathon-todo/templates/ingress.yaml
git commit -m "feat(k8s): add secrets and ingress templates"
```

---

## Task 8: Create Deployment Script

**Files:**
- Create: `scripts/deploy-local.sh`
- Create: `k8s/hackathon-todo/values-local.yaml`

**Step 1: Create local values file template**

Create file `k8s/hackathon-todo/values-local.yaml.example`:

```yaml
# Local deployment values - copy to values-local.yaml and fill in
# DO NOT COMMIT values-local.yaml (contains secrets)

secrets:
  databaseUrl: "postgresql://user:pass@your-neon-host/dbname?sslmode=require"
  openaiApiKey: "sk-your-openai-key"
  authSecret: "your-better-auth-secret"
  jwtSecret: "your-jwt-secret"

# Override replicas for local development
backend:
  replicas: 1

frontend:
  replicas: 1
```

**Step 2: Create deployment script**

Create file `scripts/deploy-local.sh`:

```bash
#!/bin/bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Hackathon Todo: Local Kubernetes Deployment ===${NC}"

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

command -v docker >/dev/null 2>&1 || { echo -e "${RED}Docker not installed${NC}"; exit 1; }
command -v minikube >/dev/null 2>&1 || { echo -e "${RED}Minikube not installed${NC}"; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo -e "${RED}kubectl not installed${NC}"; exit 1; }
command -v helm >/dev/null 2>&1 || { echo -e "${RED}Helm not installed${NC}"; exit 1; }

echo -e "${GREEN}Prerequisites OK${NC}"

# Check for values-local.yaml
if [ ! -f "k8s/hackathon-todo/values-local.yaml" ]; then
    echo -e "${RED}Missing k8s/hackathon-todo/values-local.yaml${NC}"
    echo "Copy values-local.yaml.example and fill in your secrets"
    exit 1
fi

# Start Minikube if not running
if ! minikube status | grep -q "Running"; then
    echo -e "${YELLOW}Starting Minikube...${NC}"
    minikube start --cpus=4 --memory=4096 --driver=docker
fi

# Enable ingress addon
echo -e "${YELLOW}Enabling ingress addon...${NC}"
minikube addons enable ingress

# Build Docker images
echo -e "${YELLOW}Building Docker images...${NC}"

echo "Building backend..."
docker build -t todo-backend:latest ./backend

echo "Building frontend..."
docker build -t todo-frontend:latest ./frontend

# Load images into Minikube
echo -e "${YELLOW}Loading images into Minikube...${NC}"
minikube image load todo-backend:latest
minikube image load todo-frontend:latest

# Deploy with Helm
echo -e "${YELLOW}Deploying with Helm...${NC}"

# Uninstall if exists
helm uninstall hackathon-todo 2>/dev/null || true

# Install
helm install hackathon-todo ./k8s/hackathon-todo \
    -f ./k8s/hackathon-todo/values-local.yaml

# Wait for pods
echo -e "${YELLOW}Waiting for pods to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=hackathon-todo --timeout=120s

# Show status
echo -e "${GREEN}=== Deployment Status ===${NC}"
kubectl get pods -l app=hackathon-todo
kubectl get services -l app=hackathon-todo
kubectl get ingress

# Add hosts entry reminder
MINIKUBE_IP=$(minikube ip)
echo ""
echo -e "${YELLOW}Add this to /etc/hosts:${NC}"
echo "$MINIKUBE_IP todo.local"
echo ""
echo -e "${GREEN}Access the application at: http://todo.local${NC}"
echo -e "${GREEN}Or use: minikube service hackathon-todo-frontend --url${NC}"
```

**Step 3: Make script executable**

Run: `chmod +x scripts/deploy-local.sh`

**Step 4: Add values-local.yaml to .gitignore**

Run: `echo "k8s/hackathon-todo/values-local.yaml" >> .gitignore`

**Step 5: Commit deployment script**

```bash
git add scripts/deploy-local.sh k8s/hackathon-todo/values-local.yaml.example .gitignore
git commit -m "feat(k8s): add local deployment script and values template"
```

---

## Task 9: Test Docker Builds

**Files:**
- None (testing only)

**Step 1: Build backend image**

Run: `cd /home/asadullahshafique/hackathon-todo/hackathon-todo && docker build -t todo-backend:latest ./backend`
Expected: Successfully built

**Step 2: Build frontend image**

Run: `docker build -t todo-frontend:latest ./frontend`
Expected: Successfully built

**Step 3: Test backend container locally**

Run:
```bash
docker run --rm -p 8001:8000 \
  -e DATABASE_URL="$DATABASE_URL" \
  -e JWT_SECRET_KEY="test-secret" \
  todo-backend:latest &
sleep 5
curl http://localhost:8001/health
docker stop $(docker ps -q --filter ancestor=todo-backend:latest)
```
Expected: `{"status":"healthy"}`

**Step 4: No commit needed (testing only)**

---

## Task 10: Deploy to Minikube

**Files:**
- Create: `k8s/hackathon-todo/values-local.yaml` (from template, not committed)

**Step 1: Create values-local.yaml with your secrets**

Run: `cp k8s/hackathon-todo/values-local.yaml.example k8s/hackathon-todo/values-local.yaml`

Then edit `k8s/hackathon-todo/values-local.yaml` with your actual secrets from backend/.env

**Step 2: Run the deployment script**

Run: `./scripts/deploy-local.sh`
Expected: All pods running, services created, ingress configured

**Step 3: Verify deployment**

Run:
```bash
kubectl get pods -l app=hackathon-todo
kubectl get services -l app=hackathon-todo
kubectl logs -l component=backend --tail=20
```
Expected: 2 backend pods, 2 frontend pods all Running/Ready

**Step 4: Test the application**

Run:
```bash
# Add hosts entry (one-time)
echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts

# Test health endpoint through ingress
curl http://todo.local/health

# Or use port-forward
kubectl port-forward svc/hackathon-todo-backend 8080:8000 &
curl http://localhost:8080/health
```
Expected: `{"status":"healthy"}`

**Step 5: Final commit**

```bash
git add -A
git commit -m "feat(phase4): complete Kubernetes deployment with Helm

- Docker images for frontend and backend
- Helm chart with secrets management
- Health checks and resource limits
- Ingress configuration
- Local deployment script"
```

---

## Task 11: Update Documentation

**Files:**
- Create: `docs/KUBERNETES.md`

**Step 1: Create Kubernetes documentation**

Create file `docs/KUBERNETES.md`:

```markdown
# Kubernetes Deployment Guide

## Prerequisites

- Docker Desktop or Docker Engine
- Minikube v1.30+
- kubectl v1.28+
- Helm v3.12+

## Quick Start

1. Copy secrets template:
   ```bash
   cp k8s/hackathon-todo/values-local.yaml.example k8s/hackathon-todo/values-local.yaml
   ```

2. Edit `values-local.yaml` with your secrets

3. Run deployment:
   ```bash
   ./scripts/deploy-local.sh
   ```

4. Add to /etc/hosts:
   ```
   <minikube-ip> todo.local
   ```

5. Access: http://todo.local

## Commands

```bash
# View pods
kubectl get pods -l app=hackathon-todo

# View logs
kubectl logs -l component=backend -f

# Port forward (alternative to ingress)
kubectl port-forward svc/hackathon-todo-frontend 3000:3000

# Scale
kubectl scale deployment hackathon-todo-backend --replicas=3

# Cleanup
helm uninstall hackathon-todo
minikube stop
```

## Architecture

- **Backend**: FastAPI with health checks, 2 replicas
- **Frontend**: Next.js standalone, 2 replicas
- **Ingress**: NGINX routing /api to backend, / to frontend
- **Secrets**: Kubernetes secrets for database, API keys
```

**Step 2: Commit documentation**

```bash
git add docs/KUBERNETES.md
git commit -m "docs: add Kubernetes deployment guide"
```

---

## Summary

| Task | Description | Time Est. |
|------|-------------|-----------|
| 1 | Verify prerequisites | 3 min |
| 2 | Create frontend Dockerfile | 5 min |
| 3 | Update backend Dockerfile | 3 min |
| 4 | Create Helm chart structure | 5 min |
| 5 | Backend K8s templates | 5 min |
| 6 | Frontend K8s templates | 5 min |
| 7 | Secrets and Ingress templates | 5 min |
| 8 | Deployment script | 5 min |
| 9 | Test Docker builds | 5 min |
| 10 | Deploy to Minikube | 10 min |
| 11 | Update documentation | 5 min |
| **Total** | | **~56 min** |

## Files Created/Modified

**New Files:**
- `frontend/Dockerfile`
- `k8s/hackathon-todo/Chart.yaml`
- `k8s/hackathon-todo/values.yaml`
- `k8s/hackathon-todo/.helmignore`
- `k8s/hackathon-todo/templates/backend-deployment.yaml`
- `k8s/hackathon-todo/templates/backend-service.yaml`
- `k8s/hackathon-todo/templates/frontend-deployment.yaml`
- `k8s/hackathon-todo/templates/frontend-service.yaml`
- `k8s/hackathon-todo/templates/secrets.yaml`
- `k8s/hackathon-todo/templates/ingress.yaml`
- `k8s/hackathon-todo/values-local.yaml.example`
- `scripts/deploy-local.sh`
- `docs/KUBERNETES.md`

**Modified Files:**
- `backend/Dockerfile`
- `frontend/next.config.ts`
- `.gitignore`
