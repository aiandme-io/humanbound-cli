# Bot Configuration File

The `--endpoint / -e` flag on `hb connect` accepts a JSON config file (or inline JSON string) that describes how to communicate with your bot. This integration is saved as the project's default, so subsequent `hb test` commands work automatically.

## Full Configuration Shape

```json
{
  "streaming": false,
  "thread_auth": {
    "endpoint": "",
    "headers": {},
    "payload": {}
  },
  "thread_init": {
    "endpoint": "",
    "headers": {},
    "payload": {}
  },
  "chat_completion": {
    "endpoint": "https://your-bot.com/chat",
    "headers": {
      "Authorization": "Bearer your-token",
      "Content-Type": "application/json"
    },
    "payload": {
      "content": "$PROMPT"
    }
  }
}
```

## Configuration Fields

- **`chat_completion`** (required) -- The endpoint your bot listens on for chat messages. This is the only required section.
- **`thread_init`** (required) -- Thread or session creation endpoint, called once per conversation before sending messages.
- **`thread_auth`** (optional) -- For bots that require authentication (e.g., OAuth token exchange) before testing can begin.
- **`$PROMPT`** -- The placeholder in the payload that gets replaced with each test prompt at runtime.
- **`streaming`** -- Set to `true` for WebSocket/SSE streaming endpoints.

!!! info "Note"
    At minimum, you must provide `chat_completion` and `thread_init`. `headers` and `payload` fields are required in each section but can be empty objects if not needed. Use them to pass API keys, content types, or other metadata as needed by your bot. If no `"$PROMPT"` placeholder is found in the payload, Humanbound will append the prompt to the end of the payload by default assuming OpenAI-style input. The bot output should be in the response body of the `chat_completion` endpoint for Humanbound to capture it for analysis. The expected response format is a JSON object with any of `content | ans | answer | response | resp` field containing the bot's reply.

## Basic Example

```json
{
  "thread_init": {
    "endpoint": "https://api.example.com/threads",
    "headers": { "Authorization": "Bearer token" },
    "payload": {}
  },
  "chat_completion": {
    "endpoint": "https://api.example.com/chat",
    "headers": { "Authorization": "Bearer token" },
    "payload": {
      "messages": [{ "role": "user", "content": "$PROMPT" }]
    }
  }
}
```

## Example: With OAuth Authentication

```json
{
  "streaming": false,
  "thread_auth": {
    "endpoint": "https://bot.com/oauth/token",
    "headers": {},
    "payload": {
      "client_id": "x",
      "client_secret": "y"
    }
  },
  "thread_init": {
    "endpoint": "https://bot.com/threads",
    "headers": {},
    "payload": {}
  },
  "chat_completion": {
    "endpoint": "https://bot.com/chat",
    "headers": {
      "Authorization": "Bearer token"
    },
    "payload": {
      "content": "$PROMPT"
    }
  }
}
```

!!! info "Tip"
    Save your config file as `bot-config.json` in your project root and use `hb connect -n "My Bot" -e ./bot-config.json` to connect with the integration pre-configured.
