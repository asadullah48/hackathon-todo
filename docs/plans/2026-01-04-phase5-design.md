# Phase 5 Design: Local Kubernetes with Dapr & Redpanda

**Date:** 2026-01-04
**Status:** Approved
**Author:** Brainstorming Session

## Overview

Phase 5 implements production-grade distributed architecture on local Minikube with:
- **Dapr** for distributed application runtime
- **Redpanda** for Kafka-compatible event streaming
- **Advanced features**: Recurring tasks, due dates, reminders

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Cloud Provider | Minikube (local) | Zero cost, same architecture patterns |
| Event Streaming | Redpanda | Kafka-compatible, 75% less memory than Kafka |
| Dapr Features | Full stack | Pub/Sub, State Store, Secrets, Jobs API |
| Advanced Features | All three | Recurring tasks, due dates, reminders |
| Architecture | Separate Notification Service | Clean separation, scalable |
| Reminder Delivery | In-app only | Self-contained, no external deps |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MINIKUBE CLUSTER                              │
│                                                                  │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────────┐  │
│  │ Frontend     │   │ Backend      │   │ Notification       │  │
│  │ (Next.js)    │   │ (FastAPI)    │   │ Service (FastAPI)  │  │
│  │ + Dapr       │   │ + Dapr       │   │ + Dapr             │  │
│  └──────┬───────┘   └──────┬───────┘   └─────────┬──────────┘  │
│         │                  │                      │              │
│         └──────────────────┼──────────────────────┘              │
│                            ▼                                     │
│              ┌─────────────────────────┐                        │
│              │     Dapr Components      │                        │
│              │  • Pub/Sub (Redpanda)   │                        │
│              │  • State Store (Postgres)│                        │
│              │  • Secrets (K8s)         │                        │
│              │  • Jobs API              │                        │
│              └─────────────────────────┘                        │
│                            │                                     │
│              ┌─────────────┴─────────────┐                      │
│              ▼                           ▼                      │
│     ┌─────────────┐             ┌─────────────┐                │
│     │  Redpanda   │             │  PostgreSQL │                │
│     │  (Kafka)    │             │  (existing) │                │
│     └─────────────┘             └─────────────┘                │
└─────────────────────────────────────────────────────────────────┘
```

**Components:**
- **3 Pods**: Frontend, Backend, Notification Service (each with Dapr sidecar)
- **Redpanda**: Single-node Kafka-compatible broker
- **PostgreSQL**: Existing database (reused)
- **Dapr**: Injected as sidecars, manages inter-service communication

## Event Flow Design

### Topics (Redpanda/Kafka)

| Topic | Publisher | Consumer | Purpose |
|-------|-----------|----------|---------|
| `task-events` | Backend | Notification Service | Task lifecycle events |
| `reminders` | Backend (via Jobs) | Notification Service | Due reminder triggers |

### Event Types

```
task-events:
  ├── task.created    → Log new task, check if has due date
  ├── task.completed  → Spawn next occurrence (if recurring)
  ├── task.updated    → Reschedule reminders if due date changed
  └── task.deleted    → Cancel pending reminders

reminders:
  └── reminder.due    → Store notification in DB for UI display
```

### Flow Example - Task with Reminder

1. User creates task with due_date via chat
2. Backend:
   - Saves task to PostgreSQL
   - Publishes "task.created" to task-events topic
   - Schedules reminder via Dapr Jobs API (15 min before due)
3. Dapr Jobs triggers at scheduled time:
   - Calls backend endpoint /api/jobs/trigger
   - Backend publishes "reminder.due" to reminders topic
4. Notification Service:
   - Consumes "reminder.due"
   - Writes notification record to DB
5. Frontend:
   - Polls/fetches notifications
   - Displays reminder to user

## Database Schema Changes

### Tasks table additions

```sql
ALTER TABLE tasks ADD COLUMN due_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE tasks ADD COLUMN reminder_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE tasks ADD COLUMN recurrence_type VARCHAR(20);  -- daily/weekly/monthly/none
ALTER TABLE tasks ADD COLUMN recurrence_interval INTEGER DEFAULT 1;
ALTER TABLE tasks ADD COLUMN recurrence_end_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE tasks ADD COLUMN parent_task_id INTEGER REFERENCES tasks(id);
```

### Notifications table (new)

```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    task_id INTEGER REFERENCES tasks(id),
    message TEXT NOT NULL,
    type VARCHAR(20) NOT NULL,  -- 'reminder', 'task_created', etc.
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_notifications_user_unread
    ON notifications(user_id, read) WHERE read = FALSE;
```

## Dapr Components Configuration

### Directory Structure

```
dapr-components/
├── pubsub.yaml       # Redpanda connection
├── statestore.yaml   # PostgreSQL state store
├── secrets.yaml      # Kubernetes secrets
└── subscription.yaml # Topic subscriptions
```

### Pub/Sub Component (Redpanda)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
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
```

### Subscription (Notification Service)

```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: task-events-sub
spec:
  pubsubname: pubsub
  topic: task-events
  routes:
    default: /api/events/task-events
---
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: reminders-sub
spec:
  pubsubname: pubsub
  topic: reminders
  routes:
    default: /api/events/reminders
```

## Notification Service Implementation

### Structure

```
notification-service/
├── Dockerfile
├── pyproject.toml
├── src/
│   ├── __init__.py
│   ├── main.py           # FastAPI app with Dapr event handlers
│   ├── models.py         # Notification model
│   ├── database.py       # DB connection
│   └── handlers/
│       ├── task_events.py
│       └── reminders.py
```

### Core Event Handlers

```python
@app.post("/api/events/task-events")
async def handle_task_event(event: CloudEvent, db: Session):
    event_type = event.data.get("event_type")

    if event_type == "task.completed":
        await handle_task_completed(event.data, db)
    elif event_type == "task.created":
        await handle_task_created(event.data, db)

    return {"status": "SUCCESS"}

@app.post("/api/events/reminders")
async def handle_reminder(event: CloudEvent, db: Session):
    notification = Notification(
        user_id=event.data["user_id"],
        task_id=event.data["task_id"],
        message=f"Reminder: {event.data['task_title']} is due soon!",
        type="reminder"
    )
    db.add(notification)
    db.commit()
    return {"status": "SUCCESS"}
```

## Backend Changes (Event Publisher)

### New Event Publisher Module

```python
# backend/src/events/publisher.py
import httpx
from datetime import datetime

DAPR_URL = "http://localhost:3500"

class EventPublisher:
    @staticmethod
    async def publish(topic: str, event_type: str, data: dict):
        event = {
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{DAPR_URL}/v1.0/publish/pubsub/{topic}",
                json=event
            )

    @staticmethod
    async def schedule_reminder(task_id: int, user_id: str,
                                 task_title: str, remind_at: datetime):
        job_name = f"reminder-{task_id}"
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{DAPR_URL}/v1.0-alpha1/jobs/{job_name}",
                json={
                    "dueTime": remind_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "data": {
                        "task_id": task_id,
                        "user_id": user_id,
                        "task_title": task_title
                    }
                }
            )
```

## Kubernetes/Helm Updates

### New Helm Structure

```
helm/hackathon-todo/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── backend-deployment.yaml      # + Dapr annotations
│   ├── frontend-deployment.yaml     # + Dapr annotations
│   ├── notification-deployment.yaml # NEW
│   ├── notification-service.yaml    # NEW
│   ├── redpanda-statefulset.yaml    # NEW
│   ├── redpanda-service.yaml        # NEW
│   └── dapr-components.yaml         # NEW
```

### Dapr Annotations

```yaml
metadata:
  annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "backend-service"
    dapr.io/app-port: "8000"
    dapr.io/enable-api-logging: "true"
```

### Updated values.yaml

```yaml
backend:
  dapr:
    enabled: true
    appId: backend-service

frontend:
  dapr:
    enabled: true
    appId: frontend-service

notification:
  image:
    repository: notification-service
    tag: latest
  replicas: 1
  port: 8001
  dapr:
    enabled: true
    appId: notification-service

redpanda:
  enabled: true
  storage: 1Gi
```

## Implementation Steps

| Step | Description | Commands |
|------|-------------|----------|
| 1 | Install Dapr on Minikube | `dapr init -k` |
| 2 | Deploy Redpanda | Helm install |
| 3 | Create Kafka topics | kubectl exec into Redpanda |
| 4 | Apply Dapr components | `kubectl apply -f dapr-components/` |
| 5 | Run DB migration | Add columns + notifications table |
| 6 | Build notification-service | docker build + minikube image load |
| 7 | Update backend | Add event publisher code |
| 8 | Deploy with Helm | `helm upgrade hackathon-todo` |
| 9 | Verify Dapr sidecars | kubectl get pods (3 containers) |
| 10 | Test event flow | Create task, check notifications |

## Files to Create/Modify

### New Files (~17)
- `notification-service/` (8 files)
- `dapr-components/` (4 files)
- New Helm templates (5 files)

### Modified Files (~5)
- `helm/hackathon-todo/values.yaml`
- `helm/hackathon-todo/templates/backend-deployment.yaml`
- `helm/hackathon-todo/templates/frontend-deployment.yaml`
- `backend/src/` (event publisher integration)
- Database migration file

## Validation Checklist

- [ ] Dapr installed and running on Minikube
- [ ] Redpanda deployed and accessible
- [ ] Kafka topics created (task-events, reminders)
- [ ] Dapr components applied
- [ ] Database migration successful
- [ ] All pods have Dapr sidecars (3 containers each)
- [ ] Events publishing to Redpanda
- [ ] Notification service consuming events
- [ ] Recurring tasks spawning correctly
- [ ] Reminders triggering at scheduled times
- [ ] Notifications appearing in UI
