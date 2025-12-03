# http_client.py

import time
from typing import Optional, Dict

import requests


class HttpClient:
    """
    Client HTTP đơn giản, không dùng thread ở đây.
    """

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()

    def get(self, url: str) -> Optional[Dict]:
        """
        Gửi 1 request GET, trả về dict mô tả kết quả hoặc None nếu lỗi.
        """
        try:
            start = time.time()
            resp = self.session.get(url, timeout=self.timeout, allow_redirects=False)
            elapsed_ms = (time.time() - start) * 1000.0

            return {
                "url": url,
                "status_code": resp.status_code,
                "length": len(resp.content),
                "headers": dict(resp.headers),
                "elapsed_ms": elapsed_ms,
                "location": resp.headers.get("Location"),
            }
        except requests.RequestException:
            return None
