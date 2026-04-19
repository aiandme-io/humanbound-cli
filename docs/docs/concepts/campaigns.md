# Continuous Monitoring

AI agents are non-deterministic systems. A secure agent today can regress tomorrow — after a model update, a prompt change, a new tool integration, or simply because the LLM behaves differently over time. One-time testing gives you a snapshot. Continuous monitoring gives you confidence.

## Why Continuous Monitoring Matters

| Risk | What happens | How monitoring helps |
|---|---|---|
| **Model updates** | Provider ships a new model version, agent behavior changes | Automatic retest detects regressions |
| **Prompt drift** | System prompt edited, boundary enforcement weakens | Posture score drops, alert fires |
| **New attack classes** | Novel attack techniques emerge | Evolving test strategies adapt |
| **Configuration changes** | New tools added, permissions expanded | Coverage gaps detected and tested |
| **Compliance** | Auditors need evidence of ongoing security | Historical posture data + reports |

## How It Works

Continuous monitoring automates the test → assess → improve cycle:

```
         ┌─────────────┐
         │  Schedule    │  Daily / Weekly / On-demand
         └──────┬──────┘
                │
         ┌──────▼──────┐
         │  Test        │  Run adversarial + behavioral tests
         └──────┬──────┘
                │
         ┌──────▼──────┐
         │  Assess      │  Compare to baseline, detect changes
         └──────┬──────┘
                │
         ┌──────▼──────┐
         │  Alert       │  Webhook on regression or new finding
         └──────┬──────┘
                │
                ▼
         Repeat on schedule
```

Each cycle produces:

- **Posture delta** — score compared to previous run
- **Finding lifecycle** — new findings, regressions (was fixed, now broken), stale findings (not seen in 14+ days)
- **Coverage tracking** — which threat classes were tested, where gaps remain
- **Strategy evolution** — attack patterns that worked are remembered and reused

## Campaigns

A campaign is a continuous monitoring session for a project. It runs on a configurable schedule, automatically selects what to test based on previous results, and alerts on changes.

```bash
# Enable daily monitoring
hb monitor enable --schedule daily

# Weekly monitoring
hb monitor enable --schedule weekly

# Configure alerts
hb monitor webhook --url https://slack.example.com/webhook

# Check status
hb monitor status

# Disable
hb monitor disable
```

!!! note "Platform feature"
    Continuous monitoring requires a Humanbound account. It runs on Humanbound's infrastructure — your agent is tested automatically without keeping the CLI running.

## Connection to Testing and Firewall

Continuous monitoring sits between one-time testing and runtime firewall protection:

```
[One-Time Test]  →  [Continuous Monitoring]  →  [Firewall]
hb test              hb monitor                  hb-firewall

Point-in-time        Ongoing assurance           Runtime protection
snapshot             Detects drift               Blocks attacks
Developer runs       Platform runs               Your app runs
Local or platform    Platform only               Your infrastructure
```

- **Tests** produce findings and guardrails
- **Monitoring** tracks findings over time, detects regressions, evolves attack strategies
- **Firewall** uses guardrails and trained classifiers to block attacks at runtime

The monitoring layer enriches both ends:

- **Better tests** — attack strategies that worked in previous cycles are reused in future tests
- **Better firewall** — more test data over time means richer training data for Tier 2 classifiers

## Posture History

With continuous monitoring, posture becomes a time series:

```bash
hb posture --history

  Date          Score  Grade  Change
  2026-04-14    45     D      —
  2026-04-16    61     C      +16
  2026-04-18    71     C      +10
  2026-04-25    82     B      +11
  2026-05-02    85     B      +3
```

## Finding Lifecycle

Findings are tracked across test cycles:

| Status | Meaning |
|---|---|
| **Open** | Vulnerability found, not yet fixed |
| **Fixed** | Not seen in recent tests |
| **Regressed** | Was fixed, now appears again |
| **Stale** | Not seen in 14+ days (may still exist but not triggered) |

```bash
hb findings

  ID    Title                           Status     Severity  Since
  F-01  Prompt injection via role-play  fixed      critical  Apr 14
  F-02  PII disclosure on transfer      regressed  high      Apr 14
  F-03  Excessive tool access           open       critical  Apr 18
```
