"""matcher モジュールのテスト"""

import re

from src.matcher import MatchResult, expand_template, match_line


class TestMatchLine:
    """match_line 関数のテスト"""

    def test_match_simple_pattern(self):
        """シンプルなパターンにマッチする"""
        patterns = [re.compile(r"ERROR")]
        result = match_line("2024-01-01 ERROR something failed", patterns)

        assert result is not None
        assert result.line == "2024-01-01 ERROR something failed"
        assert result.pattern == r"ERROR"

    def test_match_with_named_groups(self):
        """名前付きグループをキャプチャする"""
        patterns = [re.compile(r"(?P<level>ERROR|WARN) (?P<message>.+)")]
        result = match_line("ERROR connection failed", patterns)

        assert result is not None
        assert result.groups == {"level": "ERROR", "message": "connection failed"}

    def test_no_match_returns_none(self):
        """マッチしない場合はNoneを返す"""
        patterns = [re.compile(r"ERROR")]
        result = match_line("INFO all good", patterns)

        assert result is None

    def test_empty_line_returns_none(self):
        """空行はNoneを返す"""
        patterns = [re.compile(r"ERROR")]
        result = match_line("", patterns)

        assert result is None

    def test_whitespace_only_returns_none(self):
        """空白のみの行はNoneを返す"""
        patterns = [re.compile(r"ERROR")]
        result = match_line("   \n", patterns)

        assert result is None

    def test_first_matching_pattern_wins(self):
        """最初にマッチしたパターンが使用される"""
        patterns = [
            re.compile(r"(?P<type>ERROR)"),
            re.compile(r"(?P<type>WARN|ERROR)"),
        ]
        result = match_line("ERROR test", patterns)

        assert result is not None
        assert result.pattern == r"(?P<type>ERROR)"

    def test_strips_whitespace(self):
        """前後の空白を除去する"""
        patterns = [re.compile(r"ERROR")]
        result = match_line("  ERROR test  \n", patterns)

        assert result is not None
        assert result.line == "ERROR test"


class TestExpandTemplate:
    """expand_template 関数のテスト"""

    def test_expand_line(self):
        """lineプレースホルダーを展開する"""
        result = MatchResult(line="test line", pattern="test", groups={})
        message = expand_template("{line}", result, "source.log")

        assert message == "test line"

    def test_expand_pattern(self):
        """patternプレースホルダーを展開する"""
        result = MatchResult(line="test", pattern="ERROR.*", groups={})
        message = expand_template("Pattern: {pattern}", result, "source.log")

        assert message == "Pattern: ERROR.*"

    def test_expand_source(self):
        """sourceプレースホルダーを展開する"""
        result = MatchResult(line="test", pattern="test", groups={})
        message = expand_template("From: {source}", result, "app.log")

        assert message == "From: app.log"

    def test_expand_named_groups(self):
        """名前付きグループを展開する"""
        result = MatchResult(
            line="ERROR db failed",
            pattern="test",
            groups={"level": "ERROR", "msg": "db failed"},
        )
        message = expand_template("[{level}] {msg}", result, "source.log")

        assert message == "[ERROR] db failed"

    def test_expand_missing_group_as_empty(self):
        """存在しないグループは空文字になる"""
        result = MatchResult(line="test", pattern="test", groups={"level": None})
        message = expand_template("[{level}]", result, "source.log")

        assert message == "[]"

    def test_complex_template(self):
        """複雑なテンプレートを展開する"""
        result = MatchResult(
            line="2024-01-01 ERROR connection timeout",
            pattern=r"(?P<level>ERROR|WARN)",
            groups={"level": "ERROR"},
        )
        template = "🚨 **{level}** from `{source}`\n```\n{line}\n```"
        message = expand_template(template, result, "docker:myapp")

        expected = "🚨 **ERROR** from `docker:myapp`\n```\n2024-01-01 ERROR connection timeout\n```"
        assert message == expected
