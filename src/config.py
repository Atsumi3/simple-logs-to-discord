"""環境変数から設定を読み込む"""

import json
import os
import re
import sys
from dataclasses import dataclass


@dataclass
class Config:
    log_source: str
    source_type: str  # "file" or "docker"
    source_target: str  # file path or container name
    patterns: list[re.Pattern]
    discord_webhook: str
    message_template: str
    bot_username: str


def load_config() -> Config:
    """環境変数から設定を読み込む"""
    errors = []

    # LOG_SOURCE (required)
    log_source = os.environ.get("LOG_SOURCE", "").strip()
    if not log_source:
        errors.append("LOG_SOURCE is required")

    # Parse source type
    if log_source.startswith("docker:"):
        source_type = "docker"
        source_target = log_source[7:]
        if not source_target:
            errors.append("Container name is required for docker: source")
    else:
        source_type = "file"
        source_target = log_source

    # PATTERNS (required)
    patterns_raw = os.environ.get("PATTERNS", "").strip()
    if not patterns_raw:
        errors.append("PATTERNS is required")

    patterns = []
    if patterns_raw:
        try:
            patterns_list = json.loads(patterns_raw)
            if not isinstance(patterns_list, list) or len(patterns_list) == 0:
                errors.append("PATTERNS must be a non-empty JSON array")
            else:
                for p in patterns_list:
                    try:
                        patterns.append(re.compile(p))
                    except re.error as e:
                        errors.append(f"Invalid regex pattern '{p}': {e}")
        except json.JSONDecodeError as e:
            errors.append(f"PATTERNS is not valid JSON: {e}")

    # DISCORD_WEBHOOK (required)
    discord_webhook = os.environ.get("DISCORD_WEBHOOK", "").strip()
    if not discord_webhook:
        errors.append("DISCORD_WEBHOOK is required")
    elif not discord_webhook.startswith("https://discord.com/api/webhooks/"):
        errors.append("Invalid DISCORD_WEBHOOK format")

    # MESSAGE_TEMPLATE (optional)
    message_template = os.environ.get("MESSAGE_TEMPLATE", "{line}").strip()

    # BOT_USERNAME (optional)
    bot_username = os.environ.get("BOT_USERNAME", "simple-logs-to-discord").strip()

    if errors:
        for error in errors:
            print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    return Config(
        log_source=log_source,
        source_type=source_type,
        source_target=source_target,
        patterns=patterns,
        discord_webhook=discord_webhook,
        message_template=message_template,
        bot_username=bot_username,
    )
