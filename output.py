# output.py

import os
import datetime
from typing import Dict, List

from config import REPORTS_DIR


def print_result(result: Dict):
    """
    In 1 dòng kết quả ra màn hình CLI.
    """
    status = result["status_code"]
    length = result["length"]
    elapsed = result["elapsed_ms"]
    url = result["url"]
    print(f"[{status}] {length:6d}B {elapsed:7.1f}ms  {url}")


def save_report(results: List[Dict], target_url: str) -> str:
    """
    Lưu kết quả vào file .txt trong thư mục reports/.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_url = target_url.replace("://", "_").replace("/", "_")
    filename = os.path.join(REPORTS_DIR, f"report_{safe_url}_{ts}.txt")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Scan report for {target_url}\n")
        f.write(f"Total results: {len(results)}\n\n")
        for r in results:
            line = (
                f"[{r['status_code']}] {r['length']}B "
                f"{r['elapsed_ms']:.1f}ms {r['url']}\n"
            )
            f.write(line)

    return filename
