# Lastenheft – Noode

**Version:** 1.0  
**Datum:** 2026-02-06  
**Status:** Entwurf

---

## 1. Ausgangssituation

Software-Entwicklung ist für nicht-technische Nutzer unzugänglich. Bestehende Lösungen (Low-Code, AI-Assistenten, Entwickler-Hiring) haben fundamentale Limitierungen.

---

## 2. Ziele

### Hauptziele
| ID | Ziel | Priorität |
|----|------|-----------|
| Z1 | Vollständig autonome Software-Entwicklung durch AI-Agenten | Must |
| Z2 | Keine technischen Vorkenntnisse erforderlich | Must |
| Z3 | Produktionsreife Qualität und Sicherheit | Must |
| Z4 | Kosteneffizient gegenüber traditioneller Entwicklung | Should |

---

## 3. Funktionale Anforderungen

### 3.1 Anforderungsanalyse
| ID | Anforderung |
|----|-------------|
| FA-01 | Natürlichsprachliche Beschreibung von Anforderungen |
| FA-02 | Iterative Verfeinerung durch Dialog |
| FA-03 | Automatische Erkennung unstated requirements |

### 3.2 Entwicklung
| ID | Anforderung |
|----|-------------|
| FA-10 | Multi-Agent-Architektur (Frontend, Backend, DB, Infra) |
| FA-11 | Mandatory Research vor Implementation |
| FA-12 | Peer-Review durch spezialisierte Agenten |
| FA-13 | Automatisierte Tests |

### 3.3 Security
| ID | Anforderung |
|----|-------------|
| FA-20 | Dedizierter Security-Agent mit Veto-Recht |
| FA-21 | Security by Design (V-Model XT 2.4) |
| FA-22 | Dependency-Scanning |

### 3.4 Infrastruktur
| ID | Anforderung |
|----|-------------|
| FA-30 | Automatisches Deployment |
| FA-31 | Monitoring und Alerting |
| FA-32 | Disaster Recovery |
| FA-33 | Kosten-Optimierung |

---

## 4. Nicht-funktionale Anforderungen

| ID | Anforderung | Metrik |
|----|-------------|--------|
| NFA-01 | Barrierefreiheit | WCAG 2.1 AA |
| NFA-02 | Verfügbarkeit | 99.5% Uptime |
| NFA-03 | Performance | < 3s Antwortzeit |
| NFA-04 | Skalierbarkeit | 10.000 concurrent users |

---

## 5. Lieferform

**Zielplattform:** Linux Mint (AppImage)

| Aspekt | Spezifikation |
|--------|---------------|
| Format | AppImage (single executable) |
| Distribution | Download von Website |
| Updates | AppImageUpdate / manuell |
| Abhängigkeiten | Keine (self-contained) |

---

## 6. Abgrenzungen

- ~~Keine Unterstützung für bare-metal Deployments~~
- AppImage nur für Linux Mint (primär)
- Keine Web-Version in Phase 1
- Keine native Mobile-App
