# Phase 5: Dapr + Redpanda Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add event-driven architecture with Dapr and Redpanda on Minikube, enabling recurring tasks, due dates, and reminders.

**Architecture:** Backend publishes events to Redpanda via Dapr sidecar. Notification Service consumes events and writes to notifications table. Dapr Jobs API schedules reminders at specific times.

**Tech Stack:** Dapr 1.12+, Redpanda (Kafka-compatible), FastAPI, PostgreSQL, Helm, Minikube

---

## Prerequisites Check

### Task 0: Verify Environment

**Step 1: Check Minikube is running**

Run: `minikube status`
Expected: Shows "Running" for host, kubelet, apiserver

**Step 2: Check kubectl access**

Run: `kubectl get nodes`
Expected: Shows minikube node in "Ready" state

**Step 3: Check Helm version**

Run: `helm version --short`
Expected: v3.x.x

---

## Part 1: Dapr Installation

### Task 1: Install Dapr CLI

**Step 1: Download and install Dapr CLI**

Run:
```bash
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
```
Expected: "Dapr CLI is installed successfully"

**Step 2: Verify Dapr CLI**

Run: `dapr version`
Expected: Shows CLI version (1.12+)

**Step 3: Commit (no code changes, just documentation)**

```bash
echo "# Dapr installed: $(dapr version --output json | jq -r .Cli)" >> docs/phase5-setup-log.md
git add docs/phase5-setup-log.md
git commit -m "docs: Log Dapr CLI installation"
```

---

### Task 2: Initialize Dapr on Kubernetes

**Step 1: Install Dapr on Minikube**

Run:
```bash
dapr init -k --wait
```
Expected: "Dapr control plane installed successfully"

**Step 2: Verify Dapr pods**

Run: `kubectl get pods -n dapr-system`
Expected: 4 pods running (operator, sentry, sidecar-injector, placement)

**Step 3: Verify Dapr status**

Run: `dapr status -k`
Expected: All components showing "Running"

---

## Part 2: Redpanda Deployment

### Task 3: Create Redpanda Helm Template

**Files:**
- Create: `helm/hackathon-todo/templates/redpanda-statefulset.yaml`
- Create: `helm/hackathon-todo/templates/redpanda-service.yaml`

**Step 1: Create Redpanda StatefulSet**

Create file `helm/hackathon-todo/templates/redpanda-statefulset.yaml`:

```yaml
{{- if .Values.redpanda.enabled }}
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redpanda
  labels:
    app: redpanda
spec:
  serviceName: redpanda
  replicas: 1
  selector:
    matchLabels:
      app: redpanda
  template:
    metadata:
      labels:
        app: redpanda
    spec:
      containers:
        - name: redpanda
          image: docker.redpanda.com/redpandadata/redpanda:v23.3.5
          args:
            - redpanda
            - start
            - --smp=1
            - --memory=512M
            - --overprovisioned
            - --node-id=0
            - --kafka-addr=PLAINTEXT://0.0.0.0:9092
            - --advertise-kafka-addr=PLAINTEXT://redpanda.default.svc.cluster.local:9092
          ports:
            - containerPort: 9092
              name: kafka
            - containerPort: 8081
              name: schema-registry
            - containerPort: 8082
              name: http-proxy
            - containerPort: 9644
              name: admin
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
          volumeMounts:
            - name: data
              mountPath: /var/lib/redpanda/data
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: {{ .Values.redpanda.storage | default "1Gi" }}
{{- end }}
```

**Step 2: Create Redpanda Service**

Create file `helm/hackathon-todo/templates/redpanda-service.yaml`:

```yaml
{{- if .Values.redpanda.enabled }}
apiVersion: v1
kind: Service
metadata:
  name: redpanda
  labels:
    app: redpanda
spec:
  type: ClusterIP
  ports:
    - port: 9092
      targetPort: 9092
      name: kafka
    - port: 8081
      targetPort: 8081
      name: schema-registry
    - port: 8082
      targetPort: 8082
      name: http-proxy
    - port: 9644
      targetPort: 9644
      name: admin
  selector:
    app: redpanda
{{- end }}
```

**Step 3: Commit**

```bash
git add helm/hackathon-todo/templates/redpanda-*.yaml
git commit -m "feat(phase5): Add Redpanda Helm templates"
```

---

### Task 4: Update Helm Values for Redpanda

**Files:**
- Modify: `helm/hackathon-todo/values.yaml`

**Step 1: Add Redpanda configuration**

Add to end of `helm/hackathon-todo/values.yaml`:

```yaml

redpanda:
  enabled: true
  storage: 1Gi
```

**Step 2: Commit**

```bash
git add helm/hackathon-todo/values.yaml
git commit -m "feat(phase5): Enable Redpanda in Helm values"
```

---

### Task 5: Deploy Redpanda

**Step 1: Deploy with Helm**

Run:
```bash
helm upgrade --install hackathon-todo ./helm/hackathon-todo
```
Expected: "Release hackathon-todo has been upgraded"

**Step 2: Wait for Redpanda pod**

Run:
```bash
kubectl wait --for=condition=ready pod -l app=redpanda --timeout=120s
```
Expected: "pod/redpanda-0 condition met"

**Step 3: Create Kafka topics**

Run:
```bash
kubectl exec -it redpanda-0 -- rpk topic create task-events --brokers localhost:9092
kubectl exec -it redpanda-0 -- rpk topic create reminders --brokers localhost:9092
```
Expected: "Created topic 'task-events'" and "Created topic 'reminders'"

**Step 4: Verify topics**

Run:
```bash
kubectl exec -it redpanda-0 -- rpk topic list --brokers localhost:9092
```
Expected: Shows task-events and reminders topics

---

## Part 3: Dapr Components

### Task 6: Create Dapr Components Directory

**Files:**
- Create: `dapr-components/pubsub.yaml`
- Create: `dapr-components/subscription.yaml`

**Step 1: Create pubsub component**

Create file `dapr-components/pubsub.yaml`:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "redpanda.default.svc.cluster.local:9092"
    - name: consumerGroup
      value: "todo-app"
    - name: authType
      value: "none"
    - name: disableTls
      value: "true"
```

**Step 2: Create subscriptions**

Create file `dapr-components/subscription.yaml`:

```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: task-events-sub
  namespace: default
spec:
  pubsubname: pubsub
  topic: task-events
  routes:
    default: /api/events/task-events
  scopes:
    - notification-service
---
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: reminders-sub
  namespace: default
spec:
  pubsubname: pubsub
  topic: reminders
  routes:
    default: /api/events/reminders
  scopes:
    - notification-service
```

**Step 3: Commit**

```bash
git add dapr-components/
git commit -m "feat(phase5): Add Dapr pubsub and subscription components"
```

---

### Task 7: Apply Dapr Components

**Step 1: Apply components to cluster**

Run:
```bash
kubectl apply -f dapr-components/
```
Expected: "component.dapr.io/pubsub created", subscriptions created

**Step 2: Verify components**

Run:
```bash
kubectl get components.dapr.io
```
Expected: Shows "pubsub" component

---

## Part 4: Database Migration

### Task 8: Create Migration for Advanced Features

**Files:**
- Create: `backend/alembic/versions/003_add_advanced_task_features.py`

**Step 1: Create migration file**

Create file `backend/alembic/versions/003_add_advanced_task_features.py`:

```python
"""Add advanced task features and notifications

Revision ID: 003_advanced_features
Revises: (previous revision)
Create Date: 2026-01-04
"""
from alembic import op
import sqlalchemy as sa

revision = '003_advanced_features'
down_revision = None  # Update this to actual previous revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add columns to tasks table
    op.add_column('tasks', sa.Column('due_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tasks', sa.Column('reminder_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tasks', sa.Column('recurrence_type', sa.String(20), nullable=True))
    op.add_column('tasks', sa.Column('recurrence_interval', sa.Integer(), nullable=True, server_default='1'))
    op.add_column('tasks', sa.Column('recurrence_end_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tasks', sa.Column('parent_task_id', sa.Integer(), nullable=True))

    # Add foreign key for parent_task_id
    op.create_foreign_key(
        'fk_tasks_parent_task',
        'tasks', 'tasks',
        ['parent_task_id'], ['id'],
        ondelete='SET NULL'
    )

    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('read', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='SET NULL'),
    )

    # Create index for unread notifications
    op.create_index(
        'idx_notifications_user_unread',
        'notifications',
        ['user_id', 'read'],
        postgresql_where=sa.text('read = false')
    )


def downgrade() -> None:
    op.drop_index('idx_notifications_user_unread')
    op.drop_table('notifications')
    op.drop_constraint('fk_tasks_parent_task', 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'parent_task_id')
    op.drop_column('tasks', 'recurrence_end_date')
    op.drop_column('tasks', 'recurrence_interval')
    op.drop_column('tasks', 'recurrence_type')
    op.drop_column('tasks', 'reminder_at')
    op.drop_column('tasks', 'due_date')
```

**Step 2: Commit**

```bash
git add backend/alembic/versions/003_add_advanced_task_features.py
git commit -m "feat(phase5): Add migration for advanced features and notifications"
```

---

### Task 9: Update SQLAlchemy Models

**Files:**
- Modify: `backend/src/models/task.py`
- Create: `backend/src/models/notification.py`

**Step 1: Update Task model**

Add to `backend/src/models/task.py` Task class:

```python
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class Task(Base):
    __tablename__ = "tasks"

    # ... existing columns ...

    # Phase 5: Advanced features
    due_date: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    reminder_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    recurrence_type: Optional[str] = Column(String(20), nullable=True)  # daily/weekly/monthly/none
    recurrence_interval: int = Column(Integer, default=1)
    recurrence_end_date: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    parent_task_id: Optional[int] = Column(Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    parent_task = relationship("Task", remote_side="Task.id", backref="child_tasks")
```

**Step 2: Create Notification model**

Create file `backend/src/models/notification.py`:

```python
"""Notification model for in-app notifications."""
from datetime import datetime
from uuid import UUID
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from src.database import Base


class Notification(Base):
    """In-app notification for users."""

    __tablename__ = "notifications"

    id: int = Column(Integer, primary_key=True, index=True)
    user_id: UUID = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    task_id: int | None = Column(Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    message: str = Column(Text, nullable=False)
    type: str = Column(String(20), nullable=False)  # reminder, task_created, etc.
    read: bool = Column(Boolean, default=False)
    created_at: datetime = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    task = relationship("Task", backref="notifications")
```

**Step 3: Update models __init__.py**

Add to `backend/src/models/__init__.py`:

```python
from .notification import Notification
```

**Step 4: Commit**

```bash
git add backend/src/models/
git commit -m "feat(phase5): Add Notification model and update Task model"
```

---

## Part 5: Event Publisher (Backend)

### Task 10: Create Event Publisher Module

**Files:**
- Create: `backend/src/events/__init__.py`
- Create: `backend/src/events/publisher.py`

**Step 1: Create events package**

Create file `backend/src/events/__init__.py`:

```python
"""Event publishing module for Dapr integration."""
from .publisher import EventPublisher

__all__ = ["EventPublisher"]
```

**Step 2: Create EventPublisher**

Create file `backend/src/events/publisher.py`:

```python
"""Publish events via Dapr sidecar to Redpanda/Kafka."""
import os
import httpx
from datetime import datetime
from typing import Any
import logging

logger = logging.getLogger(__name__)

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_URL = f"http://localhost:{DAPR_HTTP_PORT}"
PUBSUB_NAME = "pubsub"


class EventPublisher:
    """Publish events to Kafka via Dapr Pub/Sub."""

    @staticmethod
    async def publish(topic: str, event_type: str, data: dict[str, Any]) -> bool:
        """
        Publish an event to a topic via Dapr.

        Args:
            topic: Kafka topic name (task-events, reminders)
            event_type: Event type (task.created, task.completed, etc.)
            data: Event payload

        Returns:
            True if published successfully, False otherwise
        """
        event = {
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{DAPR_URL}/v1.0/publish/{PUBSUB_NAME}/{topic}",
                    json=event,
                )
                response.raise_for_status()
                logger.info(f"Published {event_type} to {topic}")
                return True
        except httpx.HTTPError as e:
            logger.warning(f"Failed to publish event: {e}")
            return False

    @staticmethod
    async def schedule_reminder(
        task_id: int,
        user_id: str,
        task_title: str,
        remind_at: datetime,
    ) -> bool:
        """
        Schedule a reminder via Dapr Jobs API.

        Args:
            task_id: Task ID to remind about
            user_id: User to notify
            task_title: Task title for notification message
            remind_at: When to trigger the reminder

        Returns:
            True if scheduled successfully, False otherwise
        """
        job_name = f"reminder-{task_id}"

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    f"{DAPR_URL}/v1.0-alpha1/jobs/{job_name}",
                    json={
                        "dueTime": remind_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "data": {
                            "task_id": task_id,
                            "user_id": user_id,
                            "task_title": task_title,
                        },
                    },
                )
                response.raise_for_status()
                logger.info(f"Scheduled reminder for task {task_id} at {remind_at}")
                return True
        except httpx.HTTPError as e:
            logger.warning(f"Failed to schedule reminder: {e}")
            return False

    @staticmethod
    async def cancel_reminder(task_id: int) -> bool:
        """Cancel a scheduled reminder."""
        job_name = f"reminder-{task_id}"

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.delete(
                    f"{DAPR_URL}/v1.0-alpha1/jobs/{job_name}",
                )
                # 404 is OK - job may not exist
                if response.status_code not in (200, 204, 404):
                    response.raise_for_status()
                logger.info(f"Cancelled reminder for task {task_id}")
                return True
        except httpx.HTTPError as e:
            logger.warning(f"Failed to cancel reminder: {e}")
            return False
```

**Step 3: Commit**

```bash
git add backend/src/events/
git commit -m "feat(phase5): Add EventPublisher for Dapr integration"
```

---

### Task 11: Add Jobs Trigger Endpoint

**Files:**
- Modify: `backend/src/main.py` (or create new router)

**Step 1: Add jobs trigger endpoint**

Add to backend main.py or create `backend/src/routers/jobs.py`:

```python
from fastapi import APIRouter, Request
from src.events import EventPublisher

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/trigger")
async def handle_job_trigger(request: Request):
    """
    Dapr Jobs callback endpoint.
    Called when a scheduled job (reminder) is due.
    """
    job_data = await request.json()
    data = job_data.get("data", {})

    # Publish reminder event to be consumed by notification service
    await EventPublisher.publish(
        topic="reminders",
        event_type="reminder.due",
        data=data,
    )

    return {"status": "SUCCESS"}
```

**Step 2: Register router in main.py**

Add to `backend/src/main.py`:

```python
from src.routers import jobs
app.include_router(jobs.router)
```

**Step 3: Commit**

```bash
git add backend/src/routers/jobs.py backend/src/main.py
git commit -m "feat(phase5): Add Dapr Jobs trigger endpoint"
```

---

## Part 6: Notification Service

### Task 12: Create Notification Service Structure

**Files:**
- Create: `notification-service/pyproject.toml`
- Create: `notification-service/Dockerfile`
- Create: `notification-service/src/__init__.py`
- Create: `notification-service/src/main.py`

**Step 1: Create pyproject.toml**

Create file `notification-service/pyproject.toml`:

```toml
[project]
name = "notification-service"
version = "0.1.0"
description = "Event consumer service for todo app notifications"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "sqlalchemy>=2.0.0",
    "psycopg2-binary>=2.9.9",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Step 2: Create Dockerfile**

Create file `notification-service/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv for fast dependency management
RUN pip install uv

# Copy project files
COPY pyproject.toml .
RUN uv pip install --system -e .

COPY src/ src/

EXPOSE 8001

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

**Step 3: Create main.py**

Create file `notification-service/src/__init__.py`:
```python
"""Notification service package."""
```

Create file `notification-service/src/main.py`:

```python
"""Notification Service - Consumes events from Dapr Pub/Sub."""
import os
import logging
from datetime import datetime
from typing import Any

from fastapi import FastAPI, Request, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Notification Service", version="1.0.0")

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "")
engine = create_engine(DATABASE_URL) if DATABASE_URL else None
SessionLocal = sessionmaker(bind=engine) if engine else None


def get_db():
    """Get database session."""
    if SessionLocal is None:
        raise RuntimeError("Database not configured")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class CloudEvent(BaseModel):
    """Dapr CloudEvent format."""
    id: str
    source: str
    type: str
    specversion: str
    datacontenttype: str
    data: dict[str, Any]


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/events/task-events")
async def handle_task_event(request: Request, db: Session = Depends(get_db)):
    """Handle task lifecycle events from Kafka via Dapr."""
    body = await request.json()
    event_type = body.get("data", {}).get("event_type", "")
    data = body.get("data", {}).get("data", {})

    logger.info(f"Received task event: {event_type}")

    if event_type == "task.completed":
        await handle_task_completed(data, db)
    elif event_type == "task.created":
        await handle_task_created(data, db)

    return {"status": "SUCCESS"}


@app.post("/api/events/reminders")
async def handle_reminder(request: Request, db: Session = Depends(get_db)):
    """Handle reminder events - create in-app notification."""
    body = await request.json()
    data = body.get("data", {}).get("data", {})

    logger.info(f"Received reminder for task: {data.get('task_id')}")

    # Create notification record
    db.execute(
        """
        INSERT INTO notifications (user_id, task_id, message, type, created_at)
        VALUES (:user_id, :task_id, :message, 'reminder', NOW())
        """,
        {
            "user_id": data["user_id"],
            "task_id": data["task_id"],
            "message": f"Reminder: {data.get('task_title', 'Task')} is due soon!",
        },
    )
    db.commit()

    return {"status": "SUCCESS"}


async def handle_task_completed(data: dict, db: Session):
    """Handle task.completed - spawn next recurring task if applicable."""
    task_id = data.get("task_id")
    logger.info(f"Task {task_id} completed, checking for recurrence")

    # Query task for recurrence info
    result = db.execute(
        "SELECT * FROM tasks WHERE id = :id",
        {"id": task_id},
    ).fetchone()

    if result and result.recurrence_type and result.recurrence_type != "none":
        # Calculate next due date and create new task instance
        # (Implementation depends on recurrence_type)
        logger.info(f"Would spawn next occurrence for recurring task {task_id}")


async def handle_task_created(data: dict, db: Session):
    """Handle task.created - log for audit purposes."""
    logger.info(f"Task created: {data.get('title')} for user {data.get('user_id')}")
```

**Step 4: Commit**

```bash
git add notification-service/
git commit -m "feat(phase5): Add Notification Service"
```

---

### Task 13: Create Notification Service Helm Templates

**Files:**
- Create: `helm/hackathon-todo/templates/notification-deployment.yaml`
- Create: `helm/hackathon-todo/templates/notification-service.yaml`

**Step 1: Create deployment**

Create file `helm/hackathon-todo/templates/notification-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notification-service
  labels:
    app: notification-service
spec:
  replicas: {{ .Values.notification.replicas | default 1 }}
  selector:
    matchLabels:
      app: notification-service
  template:
    metadata:
      labels:
        app: notification-service
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "notification-service"
        dapr.io/app-port: "8001"
        dapr.io/enable-api-logging: "true"
    spec:
      containers:
        - name: notification-service
          image: "{{ .Values.notification.image.repository }}:{{ .Values.notification.image.tag }}"
          imagePullPolicy: {{ .Values.notification.image.pullPolicy | default "Never" }}
          ports:
            - containerPort: 8001
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: hackathon-todo-secrets
                  key: database-url
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "200m"
```

**Step 2: Create service**

Create file `helm/hackathon-todo/templates/notification-service.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: notification-service
  labels:
    app: notification-service
spec:
  type: ClusterIP
  ports:
    - port: 8001
      targetPort: 8001
      protocol: TCP
  selector:
    app: notification-service
```

**Step 3: Update values.yaml**

Add to `helm/hackathon-todo/values.yaml`:

```yaml

notification:
  image:
    repository: notification-service
    tag: latest
    pullPolicy: Never
  replicas: 1
  port: 8001
```

**Step 4: Commit**

```bash
git add helm/hackathon-todo/templates/notification-*.yaml helm/hackathon-todo/values.yaml
git commit -m "feat(phase5): Add Notification Service Helm templates"
```

---

## Part 7: Backend Dapr Integration

### Task 14: Add Dapr Annotations to Backend

**Files:**
- Modify: `helm/hackathon-todo/templates/backend-deployment.yaml`

**Step 1: Add Dapr annotations**

Update `helm/hackathon-todo/templates/backend-deployment.yaml` pod template metadata:

```yaml
    metadata:
      labels:
        app: backend
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend-service"
        dapr.io/app-port: "8000"
        dapr.io/enable-api-logging: "true"
```

**Step 2: Commit**

```bash
git add helm/hackathon-todo/templates/backend-deployment.yaml
git commit -m "feat(phase5): Add Dapr annotations to backend deployment"
```

---

### Task 15: Add Dapr Annotations to Frontend

**Files:**
- Modify: `helm/hackathon-todo/templates/frontend-deployment.yaml`

**Step 1: Add Dapr annotations**

Update `helm/hackathon-todo/templates/frontend-deployment.yaml` pod template metadata:

```yaml
    metadata:
      labels:
        app: frontend
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "frontend-service"
        dapr.io/app-port: "3000"
```

**Step 2: Commit**

```bash
git add helm/hackathon-todo/templates/frontend-deployment.yaml
git commit -m "feat(phase5): Add Dapr annotations to frontend deployment"
```

---

## Part 8: Build and Deploy

### Task 16: Build Docker Images

**Step 1: Build backend image**

Run:
```bash
docker build -t todo-backend:latest ./backend
```
Expected: Successfully built

**Step 2: Build notification service image**

Run:
```bash
docker build -t notification-service:latest ./notification-service
```
Expected: Successfully built

**Step 3: Load images into Minikube**

Run:
```bash
minikube image load todo-backend:latest
minikube image load notification-service:latest
```
Expected: Images loaded

---

### Task 17: Deploy Everything

**Step 1: Upgrade Helm release**

Run:
```bash
helm upgrade --install hackathon-todo ./helm/hackathon-todo
```
Expected: Release upgraded

**Step 2: Wait for pods**

Run:
```bash
kubectl wait --for=condition=ready pod -l app=backend --timeout=120s
kubectl wait --for=condition=ready pod -l app=notification-service --timeout=120s
```
Expected: Pods ready

**Step 3: Verify Dapr sidecars**

Run:
```bash
kubectl get pods -o wide
```
Expected: Each pod shows 2/2 or 3/3 containers (app + dapr sidecar)

---

## Part 9: Validation

### Task 18: Test Event Flow

**Step 1: Port forward backend**

Run:
```bash
kubectl port-forward svc/backend-service 8000:8000 &
```

**Step 2: Create a task (should publish event)**

Run:
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"title": "Test task", "due_date": "2026-01-05T10:00:00Z"}'
```
Expected: Task created

**Step 3: Check notification service logs**

Run:
```bash
kubectl logs -l app=notification-service -c notification-service --tail=50
```
Expected: Shows "Received task event: task.created"

---

### Task 19: Final Commit

**Step 1: Commit all remaining changes**

```bash
git add -A
git commit -m "feat(phase5): Complete Dapr + Redpanda integration

- Dapr installed on Minikube
- Redpanda deployed for Kafka-compatible messaging
- Event publisher in backend for task lifecycle events
- Notification service consuming events
- Database migration for advanced features
- Helm templates updated with Dapr annotations"
```

---

## Summary

**Files Created:**
- `dapr-components/pubsub.yaml`
- `dapr-components/subscription.yaml`
- `notification-service/` (full service)
- `helm/hackathon-todo/templates/redpanda-*.yaml`
- `helm/hackathon-todo/templates/notification-*.yaml`
- `backend/src/events/publisher.py`
- `backend/src/routers/jobs.py`
- `backend/src/models/notification.py`
- `backend/alembic/versions/003_add_advanced_task_features.py`

**Files Modified:**
- `helm/hackathon-todo/values.yaml`
- `helm/hackathon-todo/templates/backend-deployment.yaml`
- `helm/hackathon-todo/templates/frontend-deployment.yaml`
- `backend/src/models/task.py`
- `backend/src/main.py`

**Validation Checklist:**
- [ ] Dapr running on Minikube (4 pods in dapr-system)
- [ ] Redpanda pod running
- [ ] Kafka topics created (task-events, reminders)
- [ ] All app pods have Dapr sidecars
- [ ] Events publishing to Redpanda
- [ ] Notification service consuming events
- [ ] Notifications appearing in database
