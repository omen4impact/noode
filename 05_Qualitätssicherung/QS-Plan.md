# QS-Plan – Noode

**Version:** 1.0  
**Datum:** 2026-02-06

---

## Qualitätsziele

| Ziel | Metrik | Schwellwert |
|------|--------|-------------|
| Code-Qualität | Linting-Fehler | 0 |
| Test-Abdeckung | Line Coverage | ≥ 80% |
| Security | Kritische Vulnerabilities | 0 |
| Performance | Response Time | < 3s |

---

## Review-Prozess (V-Model XT)

```
Code-Änderung
     │
     ▼
┌─────────────────┐
│ Dependency      │──► Blockiert bei Breaking Changes
│ Review Agent    │
└─────────────────┘
     │
     ▼
┌─────────────────┐
│ Architecture    │──► Blockiert bei Pattern-Verletzung
│ Review Agent    │
└─────────────────┘
     │
     ▼
┌─────────────────┐
│ Security        │──► VETO-RECHT (unlimitiertes Budget)
│ Review Agent    │
└─────────────────┘
     │
     ▼
┌─────────────────┐
│ Testing         │──► Blockiert bei < 80% Coverage
│ Review Agent    │
└─────────────────┘
     │
     ▼
  ✅ Merge
```

---

## Testebenen

| Ebene | Verantwortung | Automatisierung |
|-------|---------------|-----------------|
| Unit-Tests | Entwickler-Agent | CI/CD |
| Integrationstests | Test-Agent | CI/CD |
| E2E-Tests | Test-Agent | Nightly |
| Security-Scans | Security-Agent | Continuous |
| Performance-Tests | Infra-Agent | Weekly |

---

## Dokumentationsstandards

- Code: JSDoc/TSDoc für alle public APIs
- Architektur: ADR (Architecture Decision Records)
- Prozess: Diese V-Model XT Dokumentation
