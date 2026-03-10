# Campaigns (ASCAM)

ASCAM (AI Security Continuous Assurance Model) provides automated campaign management through four activities: Scan -> Assess -> Investigate -> Monitor. A Decision Engine evaluates 9 signals each cycle to determine the next activity.

## View Current Campaign

```bash
hb campaigns
```

## Export as JSON

```bash
hb campaigns --json
```

## Stop Running Campaign

```bash
# Stop with confirmation prompt
hb campaigns break

# Skip confirmation
hb campaigns break --force
```

## ASCAM Activities

| Activity | Description |
|---|---|
| **Scan** | Baseline security scan with full OWASP coverage across all threat classes |
| **Assess** | Targeted retesting of findings, coverage gaps, and weak areas |
| **Investigate** | Deep adversarial testing with score-guided refinement, backtracking, and cross-conversation learning |
| **Monitor** | Continuous validation with drift detection, trigger evaluation, and regression tracking |

!!! info "Note"
    ASCAM's Decision Engine evaluates 9 signals each cycle (critical findings, regressions, posture drops, stale coverage, drift, and more) to determine the next activity automatically.
