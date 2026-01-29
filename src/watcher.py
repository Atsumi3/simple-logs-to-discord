"""ログソースの監視"""

import subprocess
import sys
from collections.abc import Iterator


def watch_file(filepath: str) -> Iterator[str]:
    """ファイルを tail -f で監視"""
    print(f"Watching file: {filepath}", file=sys.stderr)

    process = subprocess.Popen(
        ["tail", "-F", "-n", "0", filepath],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
    )

    try:
        if process.stdout:
            for line in process.stdout:
                yield line
    finally:
        process.terminate()
        process.wait()


def watch_docker(container: str) -> Iterator[str]:
    """Docker コンテナのログを監視"""
    print(f"Watching docker container: {container}", file=sys.stderr)

    process = subprocess.Popen(
        ["docker", "logs", "-f", "--since", "0s", container],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    try:
        if process.stdout:
            for line in process.stdout:
                yield line
    finally:
        process.terminate()
        process.wait()


def watch(source_type: str, source_target: str) -> Iterator[str]:
    """ログソースを監視"""
    if source_type == "docker":
        yield from watch_docker(source_target)
    else:
        yield from watch_file(source_target)
