# OpenClaw — Enterprise-Grade AI Engineering Platform

[![Docker Compose](https://img.shields.io/badge/Runtime-Docker%20Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-MCP%20Servers-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Kubernetes](https://img.shields.io/badge/Cloud-Ready%20K8s-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![Google Gemini](https://img.shields.io/badge/LLM-Google%20Gemini-4285F4?logo=google&logoColor=white)](https://aistudio.google.com/)

A **productizable, cloud-ready AI Engineering Platform**. 
You write down your problem statement in a beautiful Next.js Chat UI, and a specialized team of AI agents picks it up, solves it, containerizes it, deploys it to a GitHub repo, and creates a comprehensive README.

## Architecture & Vision

OpenClaw behaves like a software company composed of AI teammates, running with enterprise-grade traceability and scalability.

```mermaid
flowchart TD
    U[Next.js Chat UI] -->|WebSocket| O[OpenClaw API Gateway]
    
    O -->|Assigns Work| ORCH[Orchestrator Agent]
    
    subgraph Agent Team
        ORCH --> PM[Product Manager]
        ORCH --> SA[Solution Architect]
        PM --> BE[Backend Engineer]
        PM --> FE[Frontend Engineer]
        SA --> DE[DevOps Engineer]
    end
    
    Agent Team -->|Code Generation| WS[Workspace / Artifacts]
    
    WS -->|CI/CD Pipeline| GH[GitHub Repository]
    GH -->|Deployment| K8S[Kubernetes Cluster]
    
    %% Storage Layer
    O -.->|Task State| PG[(PostgreSQL + pgvector)]
    O -.->|Queues & Cache| RD[(Redis)]
```

## Core Features (Enterprise-Ready)

- **Cloud-Agnostic Infrastructure**: 12-Factor app design, deployable via Docker Compose or Kubernetes (Helm).
- **Full Traceability**: Agent actions, reasoning, and token usage are fully audited and logged in PostgreSQL.
- **Real-Time UI**: Next.js frontend with WebSocket integration for real-time visibility into agent workflows.
- **GitHub Automation**: Agents automatically create repositories, commit code, and write documentation.
- **Stateful AI Workflow**: Powered by robust check-pointing; workflows can be paused, resumed, or human-intervened.
- **Multi-tenant Auth**: Designed for org/user scoping and JWT authentication.

## Quick Start (Minimal Dev Stack)

To run the local development stack (Postgres + Redis):

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env to add your GOOGLE_API_KEY

# 2. Start the minimal infrastructure
docker compose -f docker-compose.dev.yml up -d

# 3. Start the Backend API
poetry run uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
```

## Infrastructure Services

| Service | Port | Purpose |
|---------|------|---------|
| OpenClaw API | 8001 | Main FastAPI & WebSocket Gateway |
| PostgreSQL | 5434 | Task state, artifacts, vector memory |
| Redis | 6380 | Task queues, event bus, caching |
