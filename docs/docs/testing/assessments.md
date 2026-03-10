# Assessments

Assessments are snapshots of a project's security state at a point in time. Each ASCAM activity (assess, investigate, monitor) produces an assessment that captures posture, findings, and coverage at that moment.

## List Assessments

```bash
hb assessments list
```

## View Assessment Details

```bash
hb assessments show <assessment-id>
```

## Generate Assessment Report

```bash
hb report --assessment <assessment-id>
```

!!! info "Note"
    Assessments are created automatically by ASCAM activities. Use `hb assessments list` to see history and `hb report --assessment` to generate a detailed report for any past assessment.
