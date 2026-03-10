# MCP Server

Humanbound exposes an **MCP (Model Context Protocol) server** that lets AI coding assistants (Claude Code, Cursor, Windsurf, GitHub Copilot) query your security testing data directly. Ask natural-language questions about posture, findings, coverage, and experiments without leaving your IDE.

## Setup

The MCP server is built into the Humanbound CLI. Configure it in your IDE's MCP settings:

```json
{
  "mcpServers": {
    "humanbound": {
      "command": "hb",
      "args": ["mcp"]
    }
  }
}
```

## Available Tools

| Tool | Description |
|---|---|
| `get_posture` | Current security posture score, grade, and trend data for the active project |
| `get_findings` | List findings with optional status/severity filters |
| `get_coverage` | Test coverage summary and untested categories |
| `get_experiments` | Recent experiments with status, results, and configuration |
| `get_logs` | Conversation logs and verdicts from a specific experiment |
| `get_campaigns` | Current ASCAM campaign status and phase information |

## Example Queries

Once configured, you can ask your AI assistant questions like:

- *"What's my current security posture score?"*
- *"Show me all critical findings that are still open"*
- *"What attack categories haven't been tested yet?"*
- *"Did the last experiment find any prompt injection vulnerabilities?"*
- *"What ASCAM phase is my project currently in?"*

!!! info "Requirements"
    Humanbound CLI must be installed and authenticated (`hb login`). The MCP server uses your existing CLI credentials and active project context.
