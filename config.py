# config.py

# HTTP
DEFAULT_TIMEOUT = 10  # giây

# Match HTTP status codes, hoặc "all" để match tất cả
# Mặc định: 200-299,301,302,307,401,403,405,500
DEFAULT_MATCH_CODES = "200-299,301,302,307,401,403,405,500"

# Match/Filter theo size: mặc định không dùng (None)
DEFAULT_MATCH_SIZES = None
DEFAULT_FILTER_CODES = None
DEFAULT_FILTER_SIZES = None

# Đường dẫn mặc định
DEFAULT_WORDLIST = "wordlists/common.txt"
REPORTS_DIR = "reports"
