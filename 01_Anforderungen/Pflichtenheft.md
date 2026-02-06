# Pflichtenheft – Noode v2.0 - Tauri Edition

**Version:** 2.0  
**Datum:** 2026-02-06  
**Status:** Sprint 5 - Tauri UI Implementation

---

## 📋 Zusammenfassung

Dieses Pflichtenheft beschreibt die technische Spezifikation für Noode - eine autonome AI-Entwicklungsplattform mit moderner Tauri-basierter Desktop-UI und späterer Mobile-Unterstützung.

**Änderungshistorie:**
- v1.0: Ursprüngliches GTK3-basiertes Design
- v2.0: Umstellung auf Tauri Web-UI für Cross-Platform Unterstützung

---

## 1. Systemarchitektur

### 1.1 Übersicht

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Windows    │  │    macOS     │  │    Linux     │      │
│  │     .exe     │  │     .dmg     │  │   .AppImage  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
├─────────────────────────────────────────────────────────────┤
│                    TAURI DESKTOP APP                         │
│              (React + TypeScript Frontend)                   │
├─────────────────────────────────────────────────────────────┤
│                     TAURI CORE (Rust)                        │
│              • System APIs • File System                     │
│              • Notifications • Auto-Updater                  │
├─────────────────────────────────────────────────────────────┤
│                    API LAYER (HTTP)                          │
├─────────────────────────────────────────────────────────────┤
│                    BUSINESS LAYER                            │
│              (Python + FastAPI Backend)                      │
├─────────────────────────────────────────────────────────────┤
│                    DATA LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   SQLite     │  │   Qdrant     │  │    Redis     │      │
│  │  (Projects)  │  │  (Vectors)   │  │  (Sessions)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Technologie-Stack

#### Frontend (Tauri UI)
| Komponente | Technologie | Version | Zweck |
|------------|-------------|---------|-------|
| Framework | React | 18.x | UI Components |
| Language | TypeScript | 5.x | Type Safety |
| Styling | Tailwind CSS | 3.x | Utility-first CSS |
| Animation | Framer Motion | 11.x | Smooth animations |
| State | Zustand | 4.x | State management |
| Icons | Lucide React | latest | Icon library |
| Desktop | Tauri | 1.5.x | Native bridge |

#### Backend (API)
| Komponente | Technologie | Version | Zweck |
|------------|-------------|---------|-------|
| Runtime | Python | 3.12+ | Core logic |
| API | FastAPI | 0.104+ | REST API |
| Async | asyncio | stdlib | Concurrency |
| LLM | LiteLLM | 1.50+ | LLM abstraction |
| ORM | SQLAlchemy | 2.0+ | Database |
| Validation | Pydantic | 2.5+ | Data models |
| Logging | structlog | 24.0+ | Structured logs |

#### Datenbanken
| Datenbank | Verwendung | Deployment |
|-----------|------------|------------|
| SQLite | Projekte, Sessions, Config | Embedded |
| Qdrant | Vektor-Embeddings | Docker/Local |
| Redis | Caching, Pub/Sub | Docker/Optional |

### 1.3 Projektstruktur

```
03_Entwicklung/
├── src/noode/                    # Python Backend
│   ├── agents/                   # AI Agents
│   │   ├── __init__.py
│   │   ├── base.py              # Agent base class
│   │   ├── research_agent.py    # ✅ Sprint 0-4
│   │   ├── requirements_agent.py # 🔄 Sprint 7
│   │   ├── frontend_agent.py    # ✅ Sprint 0-4
│   │   ├── backend_agent.py     # ✅ Sprint 0-4
│   │   ├── database_agent.py    # 🔄 Sprint 7
│   │   ├── security_agent.py    # ✅ Sprint 0-4
│   │   └── testing_agent.py     # 🔄 Sprint 7
│   │
│   ├── core/                     # Core Logic
│   │   ├── __init__.py
│   │   ├── orchestrator.py      # Task coordination
│   │   ├── memory.py            # Agent memory
│   │   ├── knowledge_store.py   # 🔄 Sprint 8
│   │   ├── project_manager.py   # Project CRUD
│   │   └── session_manager.py   # Session handling
│   │
│   ├── api/                      # FastAPI
│   │   ├── __init__.py
│   │   ├── server.py            # App initialization
│   │   ├── routes.py            # REST endpoints
│   │   └── models.py            # Pydantic models
│   │
│   ├── protocols/               # Communication
│   │   ├── __init__.py
│   │   ├── messages.py          # Message types
│   │   └── consensus.py         # Voting logic
│   │
│   └── utils/                   # Utilities
│       ├── __init__.py
│       ├── logging.py           # Logging setup
│       └── validation.py        # Input validation
│
├── tauri-ui/                    # 🆕 Tauri Frontend
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   │   ├── ui/             # Base components
│   │   │   ├── layout/         # Layout components
│   │   │   └── agents/         # Agent-specific UI
│   │   │
│   │   ├── pages/              # Screens
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Projects.tsx
│   │   │   ├── NewProject.tsx
│   │   │   └── Settings.tsx
│   │   │
│   │   ├── hooks/              # Custom React hooks
│   │   │   ├── useApi.ts       # API communication
│   │   │   ├── useProjects.ts  # Project management
│   │   │   └── useAgents.ts    # Agent monitoring
│   │   │
│   │   ├── api/                # API client
│   │   │   ├── client.ts       # HTTP client
│   │   │   ├── projects.ts     # Project API
│   │   │   └── agents.ts       # Agent API
│   │   │
│   │   ├── types/              # TypeScript types
│   │   ├── store/              # Zustand stores
│   │   └── App.tsx             # Main component
│   │
│   ├── src-tauri/              # Rust backend
│   │   ├── src/
│   │   │   └── main.rs         # Entry point
│   │   ├── Cargo.toml
│   │   └── tauri.conf.json     # Tauri config
│   │
│   ├── public/                 # Static assets
│   ├── package.json
│   ├── tailwind.config.js
│   └── tsconfig.json
│
├── tests/                      # Test Suite
│   ├── test_core.py
│   ├── test_agents.py
│   └── ...
│
└── docs/                       # Documentation
    ├── architecture/
    ├── api/
    └── ui/
```

---

## 2. Funktionale Anforderungen

### 2.1 Frontend (Tauri UI)

#### FA-UI-01: Dashboard
- Übersicht aller Projekte
- Quick-Actions für häufige Aufgaben
- Agent-Status in Echtzeit
- Aktivitäts-Stream

#### FA-UI-02: Projekt-Management
- Projekt erstellen/bearbeiten/löschen
- Projekt-Details anzeigen
- Task-History
- Export/Import Funktionen

#### FA-UI-03: Agent Monitor
- Live-Status aller Agents
- Task-Queue Visualisierung
- Chat-Interface mit Agents
- Ergebnis-Review

#### FA-UI-04: Knowledge Base
- Dokumenten-Upload
- Vektor-Suche
- Konversations-History
- Knowledge Graph (optional)

#### FA-UI-05: Einstellungen
- API-Keys verwalten
- Theme (Dark/Light)
- Sprache
- Notifications

### 2.2 Backend (Python API)

#### FA-API-01: Projekt API
```
POST   /api/v1/projects          # Create project
GET    /api/v1/projects          # List projects
GET    /api/v1/projects/{id}     # Get project
PUT    /api/v1/projects/{id}     # Update project
DELETE /api/v1/projects/{id}     # Delete project
```

#### FA-API-02: Agent API
```
GET    /api/v1/agents            # List agents
GET    /api/v1/agents/{id}       # Get agent status
POST   /api/v1/agents/{id}/task  # Assign task
GET    /api/v1/agents/{id}/tasks # Get task history
```

#### FA-API-03: Task API
```
POST   /api/v1/tasks             # Create task
GET    /api/v1/tasks/{id}        # Get task status
POST   /api/v1/tasks/{id}/cancel # Cancel task
GET    /api/v1/tasks/{id}/result # Get result
```

#### FA-API-04: Knowledge API
```
POST   /api/v1/knowledge/search  # Vector search
POST   /api/v1/knowledge/upload  # Upload document
GET    /api/v1/knowledge/{id}    # Get document
DELETE /api/v1/knowledge/{id}    # Delete document
```

---

## 3. UI/UX Spezifikation

### 3.1 Design System

#### Farbpalette
```css
/* Primary */
--primary: #6366F1;        /* Indigo */
--primary-light: #818CF8;
--primary-dark: #4F46E5;

/* Secondary */
--secondary: #14B8A6;      /* Teal */
--secondary-light: #5EEAD4;

/* Accent */
--accent: #F97316;         /* Orange */

/* Backgrounds */
--bg-main: #FAFBFC;        /* Light gray */
--bg-card: #FFFFFF;        /* White */
--bg-sidebar: #F1F5F9;     /* Blue-gray */

/* Text */
--text-primary: #1E293B;   /* Dark slate */
--text-secondary: #64748B; /* Medium gray */
--text-muted: #94A3B8;     /* Light gray */
```

#### Typography
- **Font:** Inter, system-ui, sans-serif
- **Headings:** 600-800 weight
- **Body:** 400 weight
- **Sizes:** xs (12px), sm (14px), base (16px), lg (18px), xl (20px), 2xl (24px), 3xl (30px)

#### Spacing
- **Base:** 4px
- **Scale:** 4, 8, 12, 16, 24, 32, 48, 64

### 3.2 Animationen

| Element | Animation | Dauer | Easing |
|---------|-----------|-------|--------|
| Page Transition | Fade + Slide | 300ms | ease-out |
| Card Hover | Scale + Shadow | 200ms | ease-in-out |
| Button Hover | Background | 150ms | ease |
| Modal Open | Scale + Fade | 250ms | ease-out |
| Loading | Pulse | 1.5s | ease-in-out |

### 3.3 Responsive Breakpoints

| Breakpoint | Width | Anpassungen |
|------------|-------|-------------|
| Mobile | < 640px | Single column, hamburger menu |
| Tablet | 640-1024px | Two columns, collapsible sidebar |
| Desktop | > 1024px | Full layout, persistent sidebar |

---

## 4. Nicht-funktionale Anforderungen

### 4.1 Performance

| Metrik | Anforderung |
|--------|-------------|
| First Paint | < 1.5s |
| Time to Interactive | < 3s |
| API Response | < 200ms (p95) |
| Bundle Size | < 10 MB Desktop |
| Memory Usage | < 200 MB |

### 4.2 Kompatibilität

| Plattform | Version | Status |
|-----------|---------|--------|
| Windows | 10+ | ✅ Unterstützt |
| macOS | 11+ | ✅ Unterstützt |
| Linux | Ubuntu 20.04+ | ✅ Unterstützt |
| iOS | 15+ | 🔄 Sprint 11-12 |
| Android | 12+ | 🔄 Sprint 11-12 |

### 4.3 Sicherheit

- API-Key Verschlüsselung (Keychain/Keyring)
- HTTPS für API-Kommunikation
- Input Validation (Backend + Frontend)
- XSS Protection
- CSRF Protection

### 4.4 Qualität

| Aspekt | Anforderung |
|--------|-------------|
| Test Coverage | ≥ 80% Backend, ≥ 70% Frontend |
| Type Coverage | 100% TypeScript |
| Linting | ESLint + Prettier |
| Accessibility | WCAG 2.1 AA |

---

## 5. Implementierungs-Phasen

### Phase 1: Foundation (Sprint 5)
- Tauri Projekt-Setup
- React + Tailwind Konfiguration
- API Client Implementierung
- Grundlegendes Layout

### Phase 2: UI Polish (Sprint 6)
- Dashboard komplett
- Projekt-Management UI
- Agent Monitor
- Animationen

### Phase 3: Agents (Sprint 7)
- Requirements Agent
- Database Agent
- Testing Agent

### Phase 4: Intelligence (Sprint 8)
- Qdrant Integration
- RAG Implementation
- Knowledge Store UI

### Phase 5: Mobile (Sprint 11-12)
- Tauri Mobile Setup
- Touch-Optimierung
- Mobile Store Releases

---

## 6. Schnittstellen

### 6.1 Frontend → Backend

**Protokoll:** HTTP/REST + WebSocket (optional für Real-time)  
**Base URL:** `http://localhost:8000/api/v1`  
**Auth:** API-Key im Header  
**Content-Type:** `application/json`

### 6.2 Tauri → System

**File System:** Read/Write Projekt-Dateien  
**Notifications:** System Notifications  
**Auto-Update:** Tauri Updater  
**OS APIs:** Shell, Dialog, Clipboard

### 6.3 Backend → LLM Provider

**Architektur:** Direkte Provider-Integration (KEIN LiteLLM Wrapper)  
**Protokoll:** HTTP/REST mit Provider-spezifischen APIs  
**Timeout:** 30s Standard, 120s für komplexe Tasks  
**Retry:** 3 Versuche mit Exponential Backoff

#### 6.3.1 OpenAI
- **API:** https://api.openai.com/v1/chat/completions
- **Auth:** Bearer Token
- **Models:** gpt-4, gpt-4-turbo, gpt-3.5-turbo
- **SDK:** `openai` Python Package
- **Key-Storage:** `~/.config/noode/openai.key`

#### 6.3.2 Anthropic
- **API:** https://api.anthropic.com/v1/messages
- **Auth:** x-api-key Header
- **Models:** claude-3-opus, claude-3-sonnet, claude-3-haiku
- **SDK:** `anthropic` Python Package
- **Key-Storage:** `~/.config/noode/anthropic.key`

#### 6.3.3 Google (Gemini)
- **API:** https://generativelanguage.googleapis.com/v1beta
- **Auth:** API Key (Query Param)
- **Models:** gemini-pro, gemini-pro-vision
- **SDK:** `google-generativeai` Python Package
- **Key-Storage:** `~/.config/noode/google.key`

#### 6.3.4 OpenRouter
- **API:** https://openrouter.ai/api/v1/chat/completions
- **Auth:** Bearer Token
- **Models:** Alle verfügbaren Models (OpenAI, Anthropic, etc.)
- **SDK:** `requests` (Standard HTTP)
- **Key-Storage:** `~/.config/noode/openrouter.key`

#### 6.3.5 Fehlerbehandlung
| Fehler | HTTP | Reaktion |
|--------|------|----------|
| Invalid Key | 401 | User Notification |
| Rate Limit | 429 | Exponential Backoff |
| Server Error | 500/503 | Fallback Provider |
| Timeout | - | Retry mit 2x Timeout |

#### 6.3.6 Konfiguration
```yaml
# ~/.config/noode/providers.yaml
active_provider: openai
providers:
  openai:
    model: gpt-4
    temperature: 0.7
    max_tokens: 4000
  anthropic:
    model: claude-3-opus
    max_tokens: 4000
  google:
    model: gemini-pro
  openrouter:
    model: openai/gpt-4
```

---

## 7. Abnahmekriterien

### 7.1 MVP (Sprint 8)
- [ ] App startet auf Windows, macOS, Linux
- [ ] User kann Projekt erstellen und verwalten
- [ ] Alle 7 Agents funktionieren
- [ ] Live-Chat mit Agents
- [ ] Vektor-Suche funktioniert
- [ ] Bundle < 10 MB

### 7.2 Release 1.0 (Sprint 12)
- [ ] Mobile Apps für iOS und Android
- [ ] Auto-Update funktioniert
- [ ] Dokumentation vollständig
- [ ] 99% Uptime im Test
- [ ] < 100ms API Latenz (p95)

---

## 8. Änderungshistorie

| Version | Datum | Autor | Änderungen |
|---------|-------|-------|------------|
| 1.0 | 06.02.2026 | - | Initiale Version (GTK3) |
| 2.0 | 06.02.2026 | Kimi | Umstellung auf Tauri Web-UI, Cross-Platform Support, Mobile Roadmap |
