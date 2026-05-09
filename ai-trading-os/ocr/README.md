# OCR 截屏 → K 线结构化数据

本目录约定：**您本地的截屏工具（例如 Windows 上的「辅助记忆」）负责热键与截图**；本仓库只约定 **截图之后** 如何把顶部 OHLC 文本变成标准化 JSON（可与 API 路径的 K 线格式对齐）。

无法访问您机器上的 `E:\桌面\辅助记忆`，以下为 **对接契约**，便于您把现有程序改成「方向键右移 + 截图」并写入字段。

---

## 1. 热键与操作节奏（建议）

| 目标 | 建议 |
|------|------|
| 向右浏览 K 线 | 将 **热键设为方向键 `→`（Right）**，与图表软件「向右一根 K 线」一致 |
| 每次按键 | 触发一次截图（或：先 `→` 再自动截图，按您原工具逻辑改） |
| 内存 | 截图完成后尽快释放位图；只保留文件路径 + OCR 文本 |

**K 线编号 `bar_index`**：在一次连续会话里从 `0` 或 `1` 开始，每按一次 `→` 并生成一根 K 线记录就 **+1**。编号表示「本次录制顺序」，不等于交易所全局 K 线 ID；若需要绝对时间对齐，以 `timestamp`（Unix 秒）为主。

---

## 2. 必须落地的字段

与标准化层一致（示例见 `example_capture_output.json`）：

| 字段 | 含义 |
|------|------|
| `symbol` | 品种，如 `BTCUSDT` |
| `timeframe` | 周期，如 `15m`、`1h` |
| `bar_index` | 本次会话内 K 线序号（截图顺序） |
| `timestamp` | Unix 秒；OCR 读不到时可为 `null`，由后续用 API 对齐 |
| `open` / `high` / `low` / `close` | 开盘价、最高、最低、收盘 |
| `volume` | 可选 |
| `source_image_path` | 截图文件路径，便于复核 |
| `raw_ocr_text` | OCR 原始字符串，便于调规则 |

---

## 3. 本仓库提供的解析脚本（纯文本 → 数字）

在 **`ai-trading-os/ocr/`** 目录下执行（依赖仅 Python 标准库）：

```bash
cd ai-trading-os/ocr
echo "O 103200.5 H 103850 L 103100 C 103700.25 Vol 12345" | python parse_chart_bar_text.py
```

或：

```bash
python parse_chart_bar_text.py -f sample_ocr.txt
```

解析逻辑见 `parse_chart_bar_text.py`：支持 `O/H/L/C`、`开高低收`、英文标签；无法识别标签时会尝试 **按顺序取前四个数字** 作为 OHLC（会标记 `parse_note`，需谨慎）。

Python 中合并会话编号与路径：

```python
from session import CaptureSession
from parse_chart_bar_text import merge_to_snapshot

sess = CaptureSession("BTCUSDT", "15m", start_index=1)
idx = sess.next_bar_index()
raw = "..."  # OCR 输出
snap = merge_to_snapshot(
    symbol="BTCUSDT",
    timeframe="15m",
    bar_index=idx,
    raw_ocr_text=raw,
    source_image_path=r"E:\captures\x.png",
)
print(snap.to_dict())
```

---

## 4. 与您「辅助记忆」的衔接方式（任选）

1. **截屏后 OCR**：对 **图表顶部状态栏 / 十字光标旁 OHLC 区域** 做矩形 ROI，再 PaddleOCR / EasyOCR，把字符串交给 `parse_chart_bar_text.py` 同类逻辑。  
2. **只做截图**：把图片路径与手动粘贴的 OCR 文本放进队列，由本仓库脚本离线解析。  
3. **更强**: 已下载的多模态权重（如 SenseNova / Qwen-VL）可在后续版本做「整图读数」，仍建议保留 `raw_ocr_text` 备查。

---

## 5. 文件说明

| 文件 | 作用 |
|------|------|
| `schema.py` | `CandleSnapshot` 数据结构 |
| `session.py` | `CaptureSession` 生成递增 `bar_index` |
| `parse_chart_bar_text.py` | OCR 文本 → OHLC / 时间（尽力而为） |
| `example_capture_output.json` | 输出示例 |

若您在「辅助记忆」里已实现具体语言（易语言 / AHK / Python），只要把 **每次截图产出的 OCR 字符串** 按上述字段写出 JSON 或调用 `merge_to_snapshot`，即可与下游指标引擎对接。
