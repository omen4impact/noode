# Systemübersicht – Noode

**Version:** 1.0  
**Datum:** 2026-02-06

---

## Architekturübersicht

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
│              (Natural Language / Visual)                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   ORCHESTRATOR AGENT                         │
│         (Koordiniert alle spezialisierten Agenten)          │
└──────┬──────┬──────┬──────┬──────┬──────┬──────┬───────────┘
       │      │      │      │      │      │      │
       ▼      ▼      ▼      ▼      ▼      ▼      ▼
    ┌─────┐┌─────┐┌─────┐┌─────┐┌─────┐┌─────┐┌─────┐
    │Req. ││Front││Back-││Data ││Infra││Test ││Sec. │
    │Agent││end  ││end  ││base ││Agent││Agent││Agent│
    └─────┘└─────┘└─────┘└─────┘└─────┘└─────┘└─────┘
```

---

## Komponenten

### Core Layer
| Komponente | Verantwortung |
|------------|---------------|
| Orchestrator | Workflow-Steuerung, Agent-Koordination |
| Memory Store | Langzeit-Wissen, Projekt-Kontext |
| Research Engine | Web-Suche, Dokumentations-Analyse |

### Development Agents
| Agent | Spezialisierung |
|-------|-----------------|
| Requirements | Anforderungsanalyse, User Stories |
| Frontend | UI/UX, React/Vue/etc. |
| Backend | APIs, Business Logic |
| Database | Schema-Design, Queries |
| Infrastructure | Cloud, Deployment |
| Testing | Automatisierte Tests |
| Security | Vulnerability-Scanning, Compliance |

---

## Technologie-Stack (vorläufig)

| Schicht | Technologie |
|---------|-------------|
| LLM | Multi-Provider (OpenAI, Anthropic, Google, OpenRouter) |
| Orchestration | Custom Python/TypeScript |
| Deployment | Docker, Kubernetes, Terraform |
| Monitoring | Prometheus, Grafana |

---

## Externe Schnittstellen - LLM Provider (NEU)

### Übersicht
Noode unterstützt direkte Integration mit führenden LLM Providern über deren offizielle APIs.

### Unterstützte Provider

| Provider | API Typ | Authentifizierung | Dokumentation |
|----------|---------|-------------------|---------------|
| **OpenAI** | REST API | API Key | https://platform.openai.com/docs |
| **Anthropic** | REST API | API Key | https://docs.anthropic.com/ |
| **Google (Gemini)** | REST API | API Key | https://ai.google.dev/docs |
| **OpenRouter** | REST API | API Key | https://openrouter.ai/docs |

### Schnittstellen-Spezifikation

#### 1. OpenAI API
```
Endpunkt: https://api.openai.com/v1/chat/completions
Methode: POST
Auth: Bearer Token (API Key)
Content-Type: application/json
```

**Request Format:**
```json
{
  "model": "gpt-4",
  "messages": [
    {"role": "system", "content": "Du bist ein Backend-Entwickler..."},
    {"role": "user", "content": "Erstelle eine Python API für..."}
  ],
  "temperature": 0.7,
  "max_tokens": 4000
}
```

**Response Format:**
```json
{
  "id": "chatcmpl-xxx",
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "Hier ist der Code..."
    }
  }]
}
```

#### 2. Anthropic API
```
Endpunkt: https://api.anthropic.com/v1/messages
Methode: POST
Auth: x-api-key Header
Content-Type: application/json
```

**Request Format:**
```json
{
  "model": "claude-3-opus-20240229",
  "max_tokens": 4000,
  "messages": [
    {"role": "user", "content": "Schreibe einen React Component..."}
  ]
}
```

#### 3. Google Gemini API
```
Endpunkt: https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
Methode: POST
Auth: API Key als Query Parameter
Content-Type: application/json
```

**Request Format:**
```json
{
  "contents": [{
    "parts": [{"text": "Erstelle eine Datenbank-Query..."}]
  }]
}
```

#### 4. OpenRouter API
```
Endpunkt: https://openrouter.ai/api/v1/chat/completions
Methode: POST
Auth: Bearer Token (API Key)
Content-Type: application/json
```

**Request Format:**
```json
{
  "model": "openai/gpt-4",
  "messages": [
    {"role": "user", "content": "Generiere Tests für..."}
  ]
}
```

### Fehlerbehandlung

| HTTP Status | Bedeutung | Reaktion |
|-------------|-----------|----------|
| 401 | Ungültiger API Key | Benutzer benachrichtigen |
| 429 | Rate Limit | Retry mit Exponential Backoff |
| 500 | Server Error | Fallback zu alternativem Provider |
| 503 | Service Unavailable | Queue & Retry |

### Konfiguration

Provider-Konfiguration erfolgt über:
- **UI**: Settings → LLM Provider
- **Config-Datei**: `~/.config/noode/providers.yaml`
- **Umgebungsvariablen**: `NOODE_OPENAI_API_KEY`, etc.

### Sicherheit

- API Keys werden verschlüsselt gespeichert (AES-256)
- Keine Logs von API Keys
- Keys niemals im Frontend/JavaScript
- Rotations-Reminder bei Key-Ablauf
