# Reports

Generate HTML security assessment reports for projects, assessments, or the entire organisation.

## Project Report

```bash
# Generate report for current project
hb report

# Save to file
hb report --output report.html
```

## Organisation Report

```bash
# Org-level report (all projects + inventory)
hb report --org
```

## Assessment Report

```bash
# Report for a specific assessment
hb report --assessment <assessment-id>
```

## JSON Output

```bash
hb report --json
```
