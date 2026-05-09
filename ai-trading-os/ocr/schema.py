"""单根 K 线截屏解析后的标准化结构（与标准化数据层对齐）。"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Optional


@dataclass
class CandleSnapshot:
    """一次截图对应的一根 K 线（来自图表顶部 OHLC 区域 OCR）。"""

    symbol: str
    timeframe: str
    bar_index: int
    timestamp: Optional[int]
    open: Optional[float]
    high: Optional[float]
    low: Optional[float]
    close: Optional[float]
    volume: Optional[float] = None
    source_image_path: Optional[str] = None
    raw_ocr_text: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
