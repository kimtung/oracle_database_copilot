# HLD — High-Level Design
# Thiết Kế Cấp Cao

**Sản phẩm / Product:** DB Copilot  
**Phiên bản / Version:** 0.1  
**Ngày / Date:** 2026-09-08

---

# 🇻🇳 PHẦN TIẾNG VIỆT

---

## 1. Tổng Quan Hệ Thống

DB Copilot là **AI Database Observability and Investigation Platform** cho Oracle Database, được xây dựng theo kiến trúc **hai project riêng biệt**:

| Project | Vai trò |
|---|---|
| `oracle-mcp-server` | Oracle Evidence Gateway — kết nối Oracle, expose tools qua MCP protocol |
| `db-copilot` | AI Application — Investigation Engine, Health Engine, Report Engine, FastAPI |

### Nguyên tắc kiến trúc cốt lõi

> **AI quan sát. AI suy luận. AI đề xuất. Con người kiểm soát database.**

---

## 2. Sơ Đồ Kiến Trúc Tổng Thể

```
┌───────────────────────────────────────────────────────────┐
│                       DB COPILOT APP                      │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                    React UI                         │  │
│  │                                                     │  │
│  │ Dashboard | Incidents | SQL | Investigation | Chat  │  │
│  └──────────────────────┬──────────────────────────────┘  │
│                         │                                 │
│                         ▼                                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                  FastAPI (Python)                    │  │
│  └──────────────────────┬──────────────────────────────┘  │
│                         │                                 │
│                         ▼                                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Application Layer                       │  │
│  │                                                     │  │
│  │  Investigation Engine                               │  │
│  │  Incident Engine                                    │  │
│  │  Report Engine                                      │  │
│  └──────────────────────┬──────────────────────────────┘  │
│                         │                                 │
│              ┌──────────┴──────────┐                      │
│              ▼                     ▼                      │
│  ┌─────────────────────┐  ┌───────────────────────────┐  │
│  │ Correlation Engine   │  │ AI / LLM Service          │  │
│  └──────────┬──────────┘  └───────────────────────────┘  │
│             │                                             │
│             ▼                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Oracle Evidence Layer                   │  │
│  │                                                     │  │
│  │ Data Access → Normalization → Evidence Builder      │  │
│  └──────────────────────┬──────────────────────────────┘  │
│                         │                                 │
│                   MCP Protocol                            │
│                         │                                 │
└─────────────────────────┼────────────────────────────────┘
                          │
          ┌───────────────▼──────────────────┐
          │        ORACLE MCP SERVER          │
          │       (Separate Project)          │
          │                                  │
          │  server.py                        │
          │  tools/ (sql, ash, awr, session,  │
          │          plan, object, storage)   │
          │  oracle/ (connection, repos,      │
          │           queries)               │
          │  security/ | models/ | config/   │
          └───────────────┬──────────────────┘
                          │
                    Read-only User
                          │
                          ▼
                   ┌─────────────┐
                   │   Oracle    │
                   │  Database   │
                   └─────────────┘

          ┌─────────────────────────┐
          │       PostgreSQL        │
          │     Evidence Store      │
          │                         │
          │ snapshots | sql_metrics │
          │ incidents | evidence    │
          │ baselines | audit_logs  │
          └─────────────────────────┘
```

---

## 3. Hai Project Riêng Biệt

### 3.1 oracle-mcp-server

**Mục đích:** Oracle Evidence Gateway — cung cấp công cụ đọc Oracle qua MCP protocol.

**Đặc điểm:**
- Toàn bộ kết nối Oracle nằm ở đây
- Chỉ có SELECT privileges
- Có audit logging riêng
- Có thể deploy độc lập
- Stateless (không có database riêng)

**Tools:** 7 groups, ~35 tools (sql, ash, awr, session, plan, object, storage)

**Giao tiếp:** MCP protocol (Stdio hoặc SSE)

### 3.2 db-copilot

**Mục đích:** AI Application — Investigation, Health, Report.

**Đặc điểm:**
- Không có kết nối Oracle trực tiếp
- Gọi oracle-mcp-server qua MCP protocol
- Có PostgreSQL Evidence Store riêng
- Stateful (lưu evidence, baselines, incidents, audit logs)

**Components:**
- FastAPI REST API
- Investigation Engine
- Correlation/Detection Engine
- AI/LLM Service
- Evidence Store (PostgreSQL)

---

## 4. Data Flow Tổng Thể

### 4.1 Collection Flow (Background, mỗi 5 phút)

```
APScheduler (db-copilot)
    ↓
Evidence Collector
    ↓ [MCP call]
oracle-mcp-server tools
    ↓ [read-only query]
Oracle Database
    ↓ [structured JSON response]
Evidence Builder
    ↓
PostgreSQL Evidence Store
    ↓
Correlation Engine (detection rules)
    ↓
Incident Records
```

### 4.2 Investigation Flow (On-demand)

```
User Question (natural language)
    ↓
FastAPI POST /investigate
    ↓
Intent Parser
    ↓
Investigation Planner
    ↓
[Dynamic MCP calls via oracle-mcp-server]
    ↓
Evidence Collection
    ↓
Evidence Normalization
    ↓
Correlation Engine
    ↓
Hypothesis Engine
    ↓
AI / LLM Service
    ↓
Evidence-based Diagnosis
    ↓
REST API Response
```

### 4.3 Daily Report Flow (Scheduled, 6:00 AM)

```
APScheduler
    ↓
Health Service
    ↓ [reads from PostgreSQL]
Evidence Store (last 24h)
    ↓
AI / LLM Service
    ↓
Report Generator
    ↓
Dashboard | Email | Slack | Teams
```

---

## 5. Giao Tiếp Giữa Các Components

| Từ | Đến | Protocol | Ghi chú |
|---|---|---|---|
| React UI | FastAPI | HTTP/REST + WebSocket | REST cho queries, WS cho streaming investigation |
| FastAPI | Evidence Store | SQL (asyncpg) | Via SQLAlchemy async |
| FastAPI | oracle-mcp-server | MCP (Stdio/SSE) | Evidence collection & investigation |
| oracle-mcp-server | Oracle Database | `python-oracledb` thin mode | Read-only connection pool |
| FastAPI | LLM Provider | HTTP (OpenAI/Anthropic/Google APIs) | Structured JSON output |
| APScheduler | Evidence Collector | In-process | Background job |

---

## 6. Security Boundaries

```
┌─────────────────────────────────────────────┐
│              PUBLIC ZONE                    │
│  React UI ←→ FastAPI                        │
└──────────────────────┬──────────────────────┘
                       │ (internal only)
┌──────────────────────▼──────────────────────┐
│              INTERNAL ZONE                  │
│  FastAPI ←→ oracle-mcp-server               │
│  FastAPI ←→ PostgreSQL                      │
│  FastAPI ←→ LLM APIs                        │
└──────────────────────┬──────────────────────┘
                       │ (read-only, audited)
┌──────────────────────▼──────────────────────┐
│              DATABASE ZONE                  │
│  oracle-mcp-server ←→ Oracle DB             │
│  (read-only Oracle account, least privilege) │
└─────────────────────────────────────────────┘
```

**Oracle credentials** chỉ tồn tại trong `oracle-mcp-server`. Không bao giờ được gửi lên `db-copilot` app hoặc LLM.

---

## 7. Tech Stack Summary

| Layer | Technology |
|---|---|
| API | FastAPI (Python 3.12) |
| UI | React |
| Oracle Access | `python-oracledb` (thin mode) — chỉ trong oracle-mcp-server |
| MCP Protocol | MCP SDK (Python) |
| Evidence Store | PostgreSQL 16 |
| Scheduler | APScheduler |
| AI/LLM | Python abstraction: OpenAI / Claude / Gemini |
| Containerization | Docker / Docker Compose |
| Package Management | `pyproject.toml` (Poetry hoặc uv) |

---

---

# 🇬🇧 ENGLISH SECTION

---

## 8. System Overview

DB Copilot is an **AI Database Observability and Investigation Platform** for Oracle Database, built as **two separate projects**:

| Project | Role |
|---|---|
| `oracle-mcp-server` | Oracle Evidence Gateway — connects to Oracle, exposes tools via MCP protocol |
| `db-copilot` | AI Application — Investigation Engine, Health Engine, Report Engine, FastAPI |

### Core Architecture Principle

> **AI observes. AI reasons. AI recommends. Human controls the database.**

---

## 9. High-Level Architecture Diagram

_(See Section 2 — same diagram)_

Key architectural decision: **MCP Server is a completely separate, independently deployable project.** The main `db-copilot` app has no direct Oracle connection — it only communicates with `oracle-mcp-server` via MCP protocol.

---

## 10. Two Separate Projects

### 10.1 oracle-mcp-server

**Purpose:** Oracle Evidence Gateway — provides Oracle read tools via MCP protocol.

**Characteristics:**
- All Oracle connectivity lives here
- SELECT-only privileges
- Has its own audit logging
- Can be deployed independently
- Stateless (no database of its own)

**Tools:** 7 groups, ~35 tools (sql, ash, awr, session, plan, object, storage)

**Communication:** MCP protocol (Stdio or SSE)

### 10.2 db-copilot

**Purpose:** AI Application — Investigation, Health, Report.

**Characteristics:**
- No direct Oracle connection
- Calls oracle-mcp-server via MCP protocol
- Has its own PostgreSQL Evidence Store
- Stateful (stores evidence, baselines, incidents, audit logs)

**Components:**
- FastAPI REST API
- Investigation Engine
- Correlation/Detection Engine
- AI/LLM Service
- Evidence Store (PostgreSQL)

---

## 11. Data Flows

### 11.1 Collection Flow (Background, every 5 minutes)

APScheduler → Evidence Collector → [MCP call] → oracle-mcp-server → Oracle DB → Evidence Builder → PostgreSQL → Correlation Engine → Incidents

### 11.2 Investigation Flow (On-demand)

User Question → FastAPI → Intent Parser → Planner → [MCP calls] → Evidence → Correlation → Hypotheses → LLM → Diagnosis

### 11.3 Daily Report Flow (6:00 AM scheduled)

APScheduler → Health Service → PostgreSQL (last 24h) → LLM → Report → Dashboard/Email/Slack

---

## 12. Security Boundaries

- **Oracle credentials**: Only exist in `oracle-mcp-server`. Never sent to `db-copilot` app or LLM.
- **Public zone**: React UI ↔ FastAPI
- **Internal zone**: FastAPI ↔ oracle-mcp-server, FastAPI ↔ PostgreSQL, FastAPI ↔ LLM APIs
- **Database zone**: oracle-mcp-server ↔ Oracle DB (read-only, audited)

---

## 13. Tech Stack Summary

| Layer | Technology |
|---|---|
| API | FastAPI (Python 3.12) |
| UI | React |
| Oracle Access | `python-oracledb` (thin mode) — oracle-mcp-server only |
| MCP Protocol | MCP SDK (Python) |
| Evidence Store | PostgreSQL 16 |
| Scheduler | APScheduler |
| AI/LLM | OpenAI / Claude / Gemini (abstracted) |
| Containers | Docker / Docker Compose |
| Packaging | `pyproject.toml` (Poetry or uv) |
