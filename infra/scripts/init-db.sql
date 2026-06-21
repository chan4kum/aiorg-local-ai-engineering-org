-- OpenClaw Database Initialization
-- This script runs once when the Postgres container is first created.
-- Tables are managed by SQLAlchemy / Alembic, so we only set up extensions here.

-- Enable pgvector for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
