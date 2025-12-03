# dictionary.py

from typing import List


def load_wordlist(path: str) -> List[str]:
    """
    Đọc file wordlist, bỏ dòng trống và comment.
    Đảm bảo mỗi path bắt đầu bằng "/".
    """
    paths: List[str] = []

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if not line.startswith("/"):
                line = "/" + line
            paths.append(line)

    return paths
