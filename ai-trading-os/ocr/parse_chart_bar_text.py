"""
从图表顶部状态栏 / 悬浮提示中的 OCR 纯文本解析 OHLC、成交量与大致时间。

说明：
- 不同终端文案差异很大，本模块采用「标签 + 数值」与常见排版规则的宽松解析。
- 时间戳若无法可靠解析则为 None，应由上游（交易所 API、录屏起始时间）补齐。
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from schema import CandleSnapshot

_FLOAT = r"(?:[\d]{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"


def _parse_float(token: str) -> Optional[float]:
    t = token.replace(",", "").strip()
    if not t:
        return None
    try:
        return float(t)
    except ValueError:
        return None


def _labeled_float(patterns: list[str], text: str) -> Optional[float]:
    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE | re.MULTILINE)
        if m:
            v = _parse_float(m.group(1))
            if v is not None:
                return v
    return None


def parse_timestamp_unix(text: str) -> Optional[int]:
    """尽力从 OCR 文本中提取时间并转为 Unix 秒（本地时区 naive → 视为本地）。"""
    candidates = [
        r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})\s+(\d{1,2}):(\d{2})(?::(\d{2}))?",
        r"(\d{4})(\d{2})(\d{2})\s+(\d{1,2}):(\d{2})(?::(\d{2}))?",
    ]
    for pat in candidates:
        m = re.search(pat, text)
        if not m:
            continue
        g = [int(x) if x is not None else 0 for x in m.groups()]
        if len(g) >= 5:
            y, mo, d, hh, mm = g[0], g[1], g[2], g[3], g[4]
            ss = g[5] if len(g) > 5 else 0
            try:
                dt = datetime(y, mo, d, hh, mm, ss)
                return int(dt.timestamp())
            except ValueError:
                continue
    return None


def parse_ohlc_from_ocr_text(text: str) -> dict[str, Any]:
    """
    返回字典字段（未识别则为 None）：
    open, high, low, close, volume, timestamp_unix, parse_note
    """
    normalized = re.sub(r"\s+", " ", text.replace("：", ":").strip())
    out: dict[str, Any] = {
        "open": None,
        "high": None,
        "low": None,
        "close": None,
        "volume": None,
        "timestamp_unix": parse_timestamp_unix(normalized),
        "parse_note": None,
    }

    o = _labeled_float(
        [
            rf"(?:^|[\s;|，,])(?:O|Open|开)\s*[:：]?\s*({_FLOAT})",
            rf"(?:开)\s*[:：]?\s*({_FLOAT})",
        ],
        normalized,
    )
    h = _labeled_float(
        [
            rf"(?:^|[\s;|，,])(?:H|High|高)\s*[:：]?\s*({_FLOAT})",
            rf"(?:高)\s*[:：]?\s*({_FLOAT})",
        ],
        normalized,
    )
    low_v = _labeled_float(
        [
            rf"(?:^|[\s;|，,])(?:L|Low|低)\s*[:：]?\s*({_FLOAT})",
            rf"(?:低)\s*[:：]?\s*({_FLOAT})",
        ],
        normalized,
    )
    c = _labeled_float(
        [
            rf"(?:^|[\s;|，,])(?:C|Close|收)\s*[:：]?\s*({_FLOAT})",
            rf"(?:收)\s*[:：]?\s*({_FLOAT})",
        ],
        normalized,
    )
    vol = _labeled_float(
        [
            rf"(?:Vol|Volume|量|成交量)\s*[:：]?\s*({_FLOAT})",
        ],
        normalized,
    )

    out["open"], out["high"], out["low"], out["close"], out["volume"] = o, h, low_v, c, vol

    if all(x is None for x in (o, h, low_v, c)):
        nums = re.findall(_FLOAT, normalized.replace(",", ""))
        floats = [_parse_float(n) for n in nums]
        floats = [x for x in floats if x is not None]
        if len(floats) >= 4:
            out["open"], out["high"], out["low"], out["close"] = floats[0], floats[1], floats[2], floats[3]
            out["parse_note"] = "fallback_first_four_numbers"

    return out


def merge_to_snapshot(
    *,
    symbol: str,
    timeframe: str,
    bar_index: int,
    raw_ocr_text: str,
    source_image_path: Optional[str] = None,
) -> CandleSnapshot:
    """将 OCR 文本解析结果与业务字段合并为 CandleSnapshot。"""
    p = parse_ohlc_from_ocr_text(raw_ocr_text)
    return CandleSnapshot(
        symbol=symbol,
        timeframe=timeframe,
        bar_index=bar_index,
        timestamp=p.get("timestamp_unix"),
        open=p.get("open"),
        high=p.get("high"),
        low=p.get("low"),
        close=p.get("close"),
        volume=p.get("volume"),
        source_image_path=source_image_path,
        raw_ocr_text=raw_ocr_text,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="从 OCR 文本解析 OHLC（stdin 或 --file）")
    parser.add_argument("--file", "-f", help="含 OCR 结果的 UTF-8 文本文件")
    args = parser.parse_args()
    if args.file:
        raw = Path(args.file).read_text(encoding="utf-8")
    else:
        import sys

        raw = sys.stdin.read()
    result = parse_ohlc_from_ocr_text(raw)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
