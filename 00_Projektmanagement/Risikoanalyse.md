# Risikoanalyse – Noode

**Version:** 1.0  
**Datum:** 2026-02-06

---

## Risikomatrix

| ID | Risiko | Wahrscheinlichkeit | Auswirkung | Priorität | Maßnahme |
|----|--------|-------------------|------------|-----------|----------|
| R1 | AI-Halluzinationen bei Code-Generierung | Hoch | Kritisch | 🔴 | Mandatory Peer Review, Tests |
| R2 | Security-Vulnerabilities durch AI | Mittel | Kritisch | 🔴 | Dedicated Security Agent |
| R3 | Kosten-Explosion Cloud-Infrastruktur | Mittel | Hoch | 🟠 | Budget-Limits, Auto-Scaling |
| R4 | Komplexität überschreitet AI-Fähigkeiten | Mittel | Hoch | 🟠 | Graceful Degradation |
| R5 | User-Akzeptanz nicht-technischer Nutzer | Mittel | Mittel | 🟡 | Usability-Tests, Iteration |
| R6 | Vendor Lock-In bei LLM-Providern | Niedrig | Mittel | 🟡 | Multi-Provider-Abstraktion |

---

## Risiko-Monitoring

Risiken werden bei jedem Entscheidungspunkt (EP) überprüft und aktualisiert.

### Eskalationsstufen

| Stufe | Aktion |
|-------|--------|
| 🟢 Grün | Beobachten |
| 🟡 Gelb | Aktive Mitigation |
| 🟠 Orange | Priorisierte Behandlung |
| 🔴 Rot | Sofortige Eskalation |
