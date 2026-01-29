"""simple-logs-to-discord - エントリーポイント"""

import sys

from .config import load_config
from .matcher import expand_template, match_line
from .notifier import send_notification
from .watcher import watch


def main() -> None:
    print("simple-logs-to-discord starting...", file=sys.stderr)

    # 設定読み込み
    config = load_config()

    print(f"Source: {config.log_source}", file=sys.stderr)
    print(f"Patterns: {len(config.patterns)} pattern(s)", file=sys.stderr)
    print(f"Template: {config.message_template}", file=sys.stderr)

    # ログ監視開始
    try:
        for line in watch(config.source_type, config.source_target):
            result = match_line(line, config.patterns)

            if result:
                message = expand_template(
                    config.message_template,
                    result,
                    config.log_source,
                )

                print(f"Match: {result.line}", file=sys.stderr)

                success = send_notification(
                    config.discord_webhook,
                    message,
                    config.bot_username,
                )

                if success:
                    print(f"Notified: {message[:50]}...", file=sys.stderr)

    except KeyboardInterrupt:
        print("\nShutting down...", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
