# simple-logs-to-discord

A simple log watcher that sends matched lines to Discord via webhook.

**Just 3 environment variables** to get started.

## Quick Start

```bash
docker run -d \
  -e LOG_SOURCE="docker:terraria" \
  -e PATTERNS='["has joined", "has left"]' \
  -e DISCORD_WEBHOOK="https://discord.com/api/webhooks/xxx/yyy" \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  simple-logs-to-discord
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `LOG_SOURCE` | Yes | - | Log source: file path or `docker:<container>` |
| `PATTERNS` | Yes | - | JSON array of regex patterns |
| `DISCORD_WEBHOOK` | Yes | - | Discord webhook URL |
| `MESSAGE_TEMPLATE` | No | `{line}` | Message template |
| `BOT_USERNAME` | No | `simple-logs-to-discord` | Bot display name |

## LOG_SOURCE

### File mode

Watch a log file (like `tail -f`):

```bash
LOG_SOURCE="/var/log/app.log"
```

### Docker mode

Watch a Docker container's logs:

```bash
LOG_SOURCE="docker:my-container"
```

**Note**: Requires Docker socket mount:
```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock:ro
```

## PATTERNS

JSON array of regex patterns. Notification is sent when **any** pattern matches.

```bash
# Simple strings
PATTERNS='["error", "warning"]'

# Regex
PATTERNS='["ERROR \\[.*\\]", "Exception:"]'

# Named capture groups
PATTERNS='["(?P<player>.+) has joined\\.", "(?P<player>.+) has left\\."]'
```

**Note**: Backslashes must be escaped in JSON (`\\` instead of `\`).

## MESSAGE_TEMPLATE

Customize the notification message using placeholders:

| Placeholder | Description |
|-------------|-------------|
| `{line}` | Matched line (default) |
| `{pattern}` | Matched pattern |
| `{source}` | Log source |
| `{<name>}` | Named capture group |

Example:

```bash
MESSAGE_TEMPLATE="🎮 {player} joined the server"
```

## Examples

### Terraria Server

```yaml
version: "3.8"

services:
  terraria:
    image: ryshe/terraria:latest
    container_name: terraria
    ports:
      - "7777:7777"

  log-watcher:
    image: simple-logs-to-discord
    environment:
      - LOG_SOURCE=docker:terraria
      - PATTERNS=["(?P<player>.+) has joined\\.", "(?P<player>.+) has left\\."]
      - DISCORD_WEBHOOK=${DISCORD_WEBHOOK}
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    depends_on:
      - terraria
```

### Minecraft Server

```yaml
version: "3.8"

services:
  minecraft:
    image: itzg/minecraft-server
    container_name: minecraft

  log-watcher:
    image: simple-logs-to-discord
    environment:
      - LOG_SOURCE=docker:minecraft
      - PATTERNS=["joined the game", "left the game"]
      - DISCORD_WEBHOOK=${DISCORD_WEBHOOK}
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
```

### Application Error Monitoring

```yaml
version: "3.8"

services:
  log-watcher:
    image: simple-logs-to-discord
    environment:
      - LOG_SOURCE=/logs/app.log
      - PATTERNS=["ERROR", "CRITICAL", "Exception"]
      - DISCORD_WEBHOOK=${DISCORD_WEBHOOK}
      - MESSAGE_TEMPLATE=🚨 {line}
    volumes:
      - /var/log/myapp:/logs:ro
```

## Build

```bash
docker build -t simple-logs-to-discord .
```

## License

MIT
