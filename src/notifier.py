"""Discord Webhook 通知"""

import sys
import requests


def send_notification(
    webhook_url: str,
    message: str,
    username: str,
) -> bool:
    """Discord Webhook にメッセージを送信"""
    # Discord の制限: 2000文字
    if len(message) > 2000:
        message = message[:1997] + "..."

    payload = {
        "content": message,
        "username": username,
    }

    try:
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=10,
        )

        if response.status_code == 204:
            return True
        elif response.status_code == 429:
            # Rate limited
            retry_after = response.json().get("retry_after", 1)
            print(f"Rate limited, retry after {retry_after}s", file=sys.stderr)
            return False
        else:
            print(
                f"Webhook error: {response.status_code} {response.text}",
                file=sys.stderr,
            )
            return False

    except requests.RequestException as e:
        print(f"Request error: {e}", file=sys.stderr)
        return False
