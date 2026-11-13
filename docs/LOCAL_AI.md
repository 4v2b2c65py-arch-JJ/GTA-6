# Local AI Connection

## Detected Runtime
- **Runtime:** Ollama (`/usr/local/bin/ollama`, `ollama serve` active)
- **API base:** `http://localhost:11434`
- **OpenAI-compatible base:** `http://localhost:11434/v1`
- **Available model:** `llama3.2:latest` (llama, 3.2B, Q4_K_M, context 131072, capabilities: completion, tools)

## Quick Checks
```bash
# List local models
curl -sS http://localhost:11434/api/tags

# Native chat test
curl -sS http://localhost:11434/api/chat -d '{
  "model": "llama3.2:latest",
  "messages": [{"role": "user", "content": "Reply with: connected"}],
  "stream": false
}'

# OpenAI-compatible test
curl -sS http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:latest",
    "messages": [{"role": "user", "content": "Reply with: connected"}]
  }'
```

## Integration Notes
- Use `http://localhost:11434/v1` as the base URL for OpenAI-compatible clients; model name `llama3.2:latest`.
- For Kilo/provider-style clients, configure a local OpenAI-compatible provider pointing to `http://localhost:11434/v1` and select `llama3.2:latest` (no API key required for local Ollama unless configured).
- Keep the model runtime running (`ollama serve`) before issuing requests.
- Connection config: `systems/local_ai/connection.json`.
