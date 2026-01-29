"""config モジュールのテスト"""

import os
from unittest.mock import patch

import pytest


class TestLoadConfig:
    """load_config 関数のテスト"""

    def test_load_valid_file_config(self):
        """有効なファイル設定を読み込む"""
        env = {
            "LOG_SOURCE": "/var/log/app.log",
            "PATTERNS": '["ERROR", "WARN"]',
            "DISCORD_WEBHOOK": "https://discord.com/api/webhooks/123/abc",
        }

        with patch.dict(os.environ, env, clear=True):
            # Reimport to get fresh config
            import importlib

            import src.config

            importlib.reload(src.config)
            config = src.config.load_config()

        assert config.source_type == "file"
        assert config.source_target == "/var/log/app.log"
        assert len(config.patterns) == 2
        assert config.discord_webhook == "https://discord.com/api/webhooks/123/abc"
        assert config.message_template == "{line}"
        assert config.bot_username == "simple-logs-to-discord"

    def test_load_docker_config(self):
        """Docker設定を読み込む"""
        env = {
            "LOG_SOURCE": "docker:mycontainer",
            "PATTERNS": '["ERROR"]',
            "DISCORD_WEBHOOK": "https://discord.com/api/webhooks/123/abc",
        }

        with patch.dict(os.environ, env, clear=True):
            import importlib

            import src.config

            importlib.reload(src.config)
            config = src.config.load_config()

        assert config.source_type == "docker"
        assert config.source_target == "mycontainer"

    def test_custom_template_and_username(self):
        """カスタムテンプレートとユーザー名を読み込む"""
        env = {
            "LOG_SOURCE": "/var/log/app.log",
            "PATTERNS": '["ERROR"]',
            "DISCORD_WEBHOOK": "https://discord.com/api/webhooks/123/abc",
            "MESSAGE_TEMPLATE": "Alert: {line}",
            "BOT_USERNAME": "MyBot",
        }

        with patch.dict(os.environ, env, clear=True):
            import importlib

            import src.config

            importlib.reload(src.config)
            config = src.config.load_config()

        assert config.message_template == "Alert: {line}"
        assert config.bot_username == "MyBot"

    def test_missing_log_source_exits(self):
        """LOG_SOURCEがない場合は終了する"""
        env = {
            "PATTERNS": '["ERROR"]',
            "DISCORD_WEBHOOK": "https://discord.com/api/webhooks/123/abc",
        }

        with patch.dict(os.environ, env, clear=True):
            import importlib

            import src.config

            importlib.reload(src.config)

            with pytest.raises(SystemExit):
                src.config.load_config()

    def test_missing_patterns_exits(self):
        """PATTERNSがない場合は終了する"""
        env = {
            "LOG_SOURCE": "/var/log/app.log",
            "DISCORD_WEBHOOK": "https://discord.com/api/webhooks/123/abc",
        }

        with patch.dict(os.environ, env, clear=True):
            import importlib

            import src.config

            importlib.reload(src.config)

            with pytest.raises(SystemExit):
                src.config.load_config()

    def test_invalid_patterns_json_exits(self):
        """不正なJSONの場合は終了する"""
        env = {
            "LOG_SOURCE": "/var/log/app.log",
            "PATTERNS": "not json",
            "DISCORD_WEBHOOK": "https://discord.com/api/webhooks/123/abc",
        }

        with patch.dict(os.environ, env, clear=True):
            import importlib

            import src.config

            importlib.reload(src.config)

            with pytest.raises(SystemExit):
                src.config.load_config()

    def test_invalid_regex_exits(self):
        """不正な正規表現の場合は終了する"""
        env = {
            "LOG_SOURCE": "/var/log/app.log",
            "PATTERNS": '["[invalid"]',
            "DISCORD_WEBHOOK": "https://discord.com/api/webhooks/123/abc",
        }

        with patch.dict(os.environ, env, clear=True):
            import importlib

            import src.config

            importlib.reload(src.config)

            with pytest.raises(SystemExit):
                src.config.load_config()

    def test_invalid_webhook_url_exits(self):
        """不正なWebhook URLの場合は終了する"""
        env = {
            "LOG_SOURCE": "/var/log/app.log",
            "PATTERNS": '["ERROR"]',
            "DISCORD_WEBHOOK": "https://example.com/webhook",
        }

        with patch.dict(os.environ, env, clear=True):
            import importlib

            import src.config

            importlib.reload(src.config)

            with pytest.raises(SystemExit):
                src.config.load_config()
