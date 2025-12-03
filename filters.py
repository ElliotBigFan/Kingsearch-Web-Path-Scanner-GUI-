# filters.py

from dataclasses import dataclass
from typing import Optional, Set, Dict


@dataclass
class FilterConfig:
    """
    Cấu hình matcher & filter:
    - match_codes: chỉ chấp nhận những status code này
      (None nghĩa là match tất cả)
    - match_sizes: chỉ chấp nhận những response size này (hoặc None)
    - filter_codes: loại bỏ những status code này (hoặc None)
    - filter_sizes: loại bỏ những size này (hoặc None)
    """
    match_codes: Optional[Set[int]] = None
    match_sizes: Optional[Set[int]] = None
    filter_codes: Optional[Set[int]] = None
    filter_sizes: Optional[Set[int]] = None


def parse_range_list(spec: str) -> Set[int]:
    """
    Parse chuỗi dạng "200,301-303,400-404" thành set[int]
    """
    result: Set[int] = set()
    if not spec:
        return result

    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue

        if "-" in part:
            start_s, end_s = part.split("-", 1)
            try:
                start = int(start_s)
                end = int(end_s)
            except ValueError:
                continue
            if start > end:
                start, end = end, start
            for v in range(start, end + 1):
                result.add(v)
        else:
            try:
                result.add(int(part))
            except ValueError:
                continue

    return result


def build_filter_config(
    mc_str: Optional[str],
    ms_str: Optional[str],
    fc_str: Optional[str],
    fs_str: Optional[str],
    default_mc_str: Optional[str],
) -> FilterConfig:
    """
    Tạo FilterConfig từ chuỗi tham số.
    - mc_str: -mc từ CLI/GUI
    - ms_str: -ms
    - fc_str: -fc
    - fs_str: -fs
    - default_mc_str: chuỗi match code mặc định (từ config)
    """

    # MATCH CODES
    if mc_str is None or mc_str.strip() == "":
        mc_str = default_mc_str

    mc_str = mc_str.strip() if mc_str else None

    if mc_str and mc_str.lower() == "all":
        match_codes = None  # match tất cả
    else:
        match_codes = parse_range_list(mc_str) if mc_str else None

    # MATCH SIZES
    match_sizes = parse_range_list(ms_str) if ms_str else None

    # FILTER CODES
    filter_codes = parse_range_list(fc_str) if fc_str else None

    # FILTER SIZES
    filter_sizes = parse_range_list(fs_str) if fs_str else None

    return FilterConfig(
        match_codes=match_codes,
        match_sizes=match_sizes,
        filter_codes=filter_codes,
        filter_sizes=filter_sizes,
    )


def should_show(result: Dict, cfg: FilterConfig) -> bool:
    """
    Áp dụng matcher và filter lên 1 kết quả HTTP.
    """
    status = result["status_code"]
    length = result["length"]

    # MATCH
    if cfg.match_codes is not None and status not in cfg.match_codes:
        return False

    if cfg.match_sizes is not None and length not in cfg.match_sizes:
        return False

    # FILTER
    if cfg.filter_codes is not None and status in cfg.filter_codes:
        return False

    if cfg.filter_sizes is not None and length in cfg.filter_sizes:
        return False

    return True
