"""notifier モジュールのテスト"""

from unittest.mock import MagicMock, patch

from src.notifier import send_notification


class TestSendNotification:
    """send_notification 関数のテスト"""

    def test_successful_send(self):
        """正常に送信できる"""
        mock_response = MagicMock()
        mock_response.status_code = 204

        with patch("src.notifier.requests.post", return_value=mock_response) as mock_post:
            result = send_notification(
                "https://discord.com/api/webhooks/123/abc",
                "Test message",
                "TestBot",
            )

        assert result is True
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["json"]["content"] == "Test message"
        assert call_kwargs["json"]["username"] == "TestBot"

    def test_truncates_long_message(self):
        """2000文字を超えるメッセージは切り詰める"""
        mock_response = MagicMock()
        mock_response.status_code = 204
        long_message = "x" * 2500

        with patch("src.notifier.requests.post", return_value=mock_response) as mock_post:
            send_notification(
                "https://discord.com/api/webhooks/123/abc",
                long_message,
                "TestBot",
            )

        call_kwargs = mock_post.call_args[1]
        content = call_kwargs["json"]["content"]
        assert len(content) == 2000
        assert content.endswith("...")

    def test_rate_limited_returns_false(self):
        """レート制限時はFalseを返す"""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"retry_after": 5}

        with patch("src.notifier.requests.post", return_value=mock_response):
            result = send_notification(
                "https://discord.com/api/webhooks/123/abc",
                "Test message",
                "TestBot",
            )

        assert result is False

    def test_error_status_returns_false(self):
        """エラーステータスはFalseを返す"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"

        with patch("src.notifier.requests.post", return_value=mock_response):
            result = send_notification(
                "https://discord.com/api/webhooks/123/abc",
                "Test message",
                "TestBot",
            )

        assert result is False

    def test_request_exception_returns_false(self):
        """リクエスト例外時はFalseを返す"""
        import requests

        with patch(
            "src.notifier.requests.post",
            side_effect=requests.RequestException("Connection error"),
        ):
            result = send_notification(
                "https://discord.com/api/webhooks/123/abc",
                "Test message",
                "TestBot",
            )

        assert result is False

    def test_timeout_is_set(self):
        """タイムアウトが設定されている"""
        mock_response = MagicMock()
        mock_response.status_code = 204

        with patch("src.notifier.requests.post", return_value=mock_response) as mock_post:
            send_notification(
                "https://discord.com/api/webhooks/123/abc",
                "Test message",
                "TestBot",
            )

        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["timeout"] == 10
