"""ログ行のパターンマッチング"""

import re
from dataclasses import dataclass


@dataclass
class MatchResult:
    line: str
    pattern: str
    groups: dict[str, str]


def match_line(line: str, patterns: list[re.Pattern]) -> MatchResult | None:
    """最初にマッチしたパターンの結果を返す"""
    line = line.strip()
    if not line:
        return None

    for pattern in patterns:
        if match := pattern.search(line):
            return MatchResult(
                line=line,
                pattern=pattern.pattern,
                groups=match.groupdict(),
            )

    return None


def expand_template(template: str, result: MatchResult, source: str) -> str:
    """テンプレートを展開する"""
    message = template
    message = message.replace("{line}", result.line)
    message = message.replace("{pattern}", result.pattern)
    message = message.replace("{source}", source)

    for name, value in result.groups.items():
        message = message.replace(f"{{{name}}}", value or "")

    return message
