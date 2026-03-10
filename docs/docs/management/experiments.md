# Experiments

Experiments are individual test executions that generate attack prompts, run conversations with your AI agent, and produce security verdicts.

## List Experiments

```bash
hb experiments list
```

## Show Experiment Details

```bash
hb experiments show <id>
```

## Check Experiment Status

```bash
# Single status check
hb experiments status <id>

# Live updates (refreshes every 10 seconds)
hb experiments status <id> --watch

# Dashboard: all experiments, polls every 60s until all complete
hb experiments status --all
```

## Wait for Completion

Block until an experiment completes (useful for CI/CD pipelines):

```bash
# Wait indefinitely
hb experiments wait <id>

# Wait with timeout (minutes)
hb experiments wait <id> --timeout 60
```

## View Experiment Logs

```bash
# View all logs
hb experiments logs <id>

# Filter by result
hb experiments logs <id> --result fail
hb experiments logs <id> --result pass

# Export branded HTML report
hb logs <id> --format html -o report.html

# Export as JSON
hb logs <id> --format json --all -o results.json

# Project-wide logs with scope flags
hb logs --last 5                           # Last 5 experiments
hb logs --last 3 --verdict fail            # Failed logs from last 3
hb logs --category owasp_agentic           # Filter by test category
hb logs --days 7 --format json -o week.json
hb logs --from 2026-01-01 --until 2026-02-01 --format html -o jan.html
```

## Terminate Running Experiment

```bash
hb experiments terminate <id>
```

## Delete Experiment

```bash
# Delete with confirmation
hb experiments delete <id>

# Skip confirmation
hb experiments delete <id> --force
```
