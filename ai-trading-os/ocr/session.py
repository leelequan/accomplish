"""截屏会话：为每次「向右移动 + 截图」单调递增 K 线编号。"""

from __future__ import annotations


class CaptureSession:
    """同一品种、同一周期、连续右键步进截图时使用。"""

    def __init__(self, symbol: str, timeframe: str, start_index: int = 0) -> None:
        self.symbol = symbol
        self.timeframe = timeframe
        self._next_index = start_index

    def next_bar_index(self) -> int:
        i = self._next_index
        self._next_index += 1
        return i
