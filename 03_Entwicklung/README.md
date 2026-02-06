# Noode

**Autonomous AI Development Platform**  
*Windows | macOS | Linux | iOS | Android (coming soon)*

[![Version](https://img.shields.io/badge/version-0.5.0-blue.svg)](https://github.com/noode/noode)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CI/CD](https://github.com/noode/noode/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/noode/noode/actions)
[![Tests](https://img.shields.io/badge/tests-68%2F68%20passing-brightgreen.svg)]()
[![Tauri](https://img.shields.io/badge/built%20with-Tauri-FFC131?logo=tauri)](https://tauri.app)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev)

A comprehensive AI-driven framework where specialized agents collaborate to handle the entire software development lifecycle. Built with Tauri for cross-platform compatibility and a modern React frontend.

![Noode Screenshot](docs/images/screenshot.png)

## ✨ Features

- 🤖 **7 Specialized AI Agents** - Complete team for full-stack development
- 🎨 **Modern Tauri UI** - Professional desktop app with React + TypeScript
- 🔄 **Real-time Collaboration** - Agents work together with consensus protocols
- 🛡️ **Security-First** - Mandatory security reviews with veto power
- 📚 **Knowledge Management** - Vector-based RAG with Qdrant for intelligent search
- 🌍 **Cross-Platform** - Native apps for Windows, macOS, Linux (Mobile coming soon)

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Rust (for Tauri)
- Docker (optional, for Qdrant)

### Installation

```bash
# Clone repository
git clone https://github.com/noode/noode.git
cd noode/03_Entwicklung

# Backend setup
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"

# Frontend setup
cd tauri-ui
npm install
```

### Development

```bash
# Terminal 1: Start Qdrant (optional, for vector search)
docker run -p 6333:6333 qdrant/qdrant

# Terminal 2: Start API Server
cd 03_Entwicklung
source .venv/bin/activate
python -m uvicorn noode.api.server:app --reload

# Terminal 3: Start Tauri Dev
cd 03_Entwicklung/tauri-ui
npm run tauri:dev
```

### Building

```bash
# Build for all platforms
cd tauri-ui
npm run tauri build

# Outputs:
# - src-tauri/target/release/bundle/msi/*.msi (Windows)
# - src-tauri/target/release/bundle/dmg/*.dmg (macOS)
# - src-tauri/target/release/bundle/appimage/*.AppImage (Linux)
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     TAURI FRONTEND                          │
│                   (React + TypeScript)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Dashboard  │  │   Projects  │  │    Agent Monitor    │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                     TAURI BRIDGE                            │
│                      (Rust Core)                            │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/WebSocket
┌──────────────────────▼──────────────────────────────────────┐
│                     FASTAPI SERVER                          │
│                    (Python Backend)                         │
├──────────┬────────────────────────┬─────────────┬───────────┤
│          │                        │             │           │
│  ┌───────▼───────┐      ┌────────▼────────┐   ┌▼────────┐  │
│  │  ORCHESTRATOR │      │  AGENT POOL     │   │   API   │  │
│  │  (7 Agents)   │      │  (7 Agents)     │   │  Layer  │  │
│  └───────┬───────┘      └────────┬────────┘   └─────────┘  │
│          │                       │                         │
│  ┌───────▼───────┐      ┌────────▼────────┐               │
│  │ KNOWLEDGE DB  │      │  VECTOR STORE   │               │
│  │   (SQLite)    │      │   (Qdrant)      │               │
│  └───────────────┘      └─────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
03_Entwicklung/
├── src/noode/                    # Python Backend (FastAPI)
│   ├── agents/                   # 7 AI Agents
│   │   ├── backend_agent.py     # API & Business Logic ✅
│   │   ├── database_agent.py    # Schema & Queries ✅
│   │   ├── frontend_agent.py    # UI Development ✅
│   │   ├── research_agent.py    # Research & Docs ✅
│   │   ├── requirements_agent.py # Requirements Analysis ✅
│   │   ├── security_agent.py    # Security Reviews ✅
│   │   └── testing_agent.py     # Test Generation ✅
│   ├── core/                     # Core Logic
│   │   ├── base_agent.py        # Agent Base Class ✅
│   │   ├── memory.py            # Agent Memory ✅
│   │   ├── orchestrator.py      # Task Coordination ✅
│   │   ├── project_manager.py   # Project CRUD ✅
│   │   └── session_manager.py   # Session Handling ✅
│   ├── knowledge/               # Vector Knowledge System
│   │   ├── embeddings.py        # Embedding Service ✅
│   │   └── store.py            # Qdrant Knowledge Store ✅
│   ├── api/                      # FastAPI
│   │   ├── server.py           # App Server ✅
│   │   ├── routes.py           # REST Endpoints ✅
│   │   └── models.py           # Pydantic Models ✅
│   └── protocols/               # Communication
│       ├── messages.py         # Message Types ✅
│       └── consensus.py        # Voting Logic ✅
│
├── tauri-ui/                    # React Frontend (Tauri)
│   ├── src/
│   │   ├── api/                # API Client ✅
│   │   ├── types/              # TypeScript Types ✅
│   │   ├── App.tsx            # Main App ✅
│   │   └── styles.css         # Tailwind Styles ✅
│   └── src-tauri/             # Rust Core ✅
│
└── tests/                      # Test Suite (68 Tests) ✅
```

## 🤖 Agents

| Agent | Purpose | Status | Lines of Code |
|-------|---------|--------|---------------|
| **ResearchAgent** | Research best practices & documentation | ✅ Ready | ~400 |
| **RequirementsAgent** | Analyze requirements & user stories | ✅ Ready | ~350 |
| **FrontendAgent** | Build UI components & styling | ✅ Ready | ~450 |
| **BackendAgent** | Design APIs & business logic | ✅ Ready | ~500 |
| **DatabaseAgent** | Schema design & SQL queries | ✅ Ready | ~450 |
| **SecurityAgent** | Security reviews & audits | ✅ Ready | ~500 |
| **TestingAgent** | Generate & run tests | ✅ Ready | ~460 |

**Total: 7/7 Agents implemented (100%)**

## 🧠 Knowledge System (RAG)

### Embedding Service
- **Model**: sentence-transformers (all-MiniLM-L6-v2)
- **Dimensions**: 384
- **Features**:
  - Text to vector conversion
  - Batch processing
  - Cosine similarity
  - Multiple model support (fast, accurate, code, multilingual)

### Knowledge Store (Qdrant)
- **Database**: Qdrant Vector DB
- **Features**:
  - Document storage with embeddings
  - Semantic search (cosine similarity)
  - RAG (Retrieval Augmented Generation)
  - Memory fallback mode
  - Document types: text, code, markdown

### Usage
```python
from noode.knowledge import KnowledgeStore, Document

# Initialize
store = KnowledgeStore()

# Add document
doc = Document(
    content="REST API best practices...",
    doc_type="markdown",
    metadata={"topic": "api-design"}
)
store.add_document(doc)

# Search
results = store.search("How to design authentication", top_k=5)
```

## 🛠️ Development

### Backend
```bash
# Run tests
pytest

# Type checking
mypy src

# Linting
ruff check src

# Run server
python -m uvicorn noode.api.server:app --reload
```

### Frontend
```bash
cd tauri-ui

# Run dev server
npm run dev

# Run Tauri dev
npm run tauri:dev

# Build
npm run tauri build

# Linting
npm run lint
```

## 📅 Roadmap Status

### ✅ Completed
- [x] Core Framework (Sprint 0-4)
- [x] **Tauri UI** (Sprint 5-6) - Complete with API integration
- [x] **All 7 Agents** (Sprint 7) - 100% implemented
- [x] **Knowledge System** (Sprint 8) - 100% complete with UI
- [x] **CI/CD Pipeline** (Sprint 9) - GitHub Actions + Docker Compose

### 🔄 In Progress (Sprint 9)
- [ ] Beta Testing
- [ ] Performance Optimization
- [ ] Documentation

### ⏳ Planned (Sprint 10-12)
- [ ] Advanced RAG features
- [ ] Agent collaboration workflows
- [ ] Mobile preparation (Tauri Mobile)
- [ ] iOS & Android Apps
- [ ] Production deployment

## 📊 Statistics

- **Total Lines of Code**: ~9,500
- **Python Files**: 33
- **TypeScript Files**: 12
- **Tests**: 68 (all passing)
- **Test Coverage**: ~65%
- **Agents**: 7/7 (100%)
- **UI Screens**: 4 (Dashboard, Projects, New Project, Knowledge)
- **API Endpoints**: 12 (100%)

## 📄 Documentation

- [Project Plan](00_Projektmanagement/Projektplan.md) - Sprint planning & timeline
- [Pflichtenheft](01_Anforderungen/Pflichtenheft.md) - Technical specification
- [System Architecture](02_Systemarchitektur/Systemübersicht.md) - Architecture docs
- [Session Handover](docs/SESSION_HANDOVER.md) - Current status & next steps

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) first.

## 📄 License

MIT © 2026 Noode Team

---

<p align="center">
  Built with ❤️ using <a href="https://tauri.app">Tauri</a>, <a href="https://react.dev">React</a>, and <a href="https://python.org">Python</a>
</p>
