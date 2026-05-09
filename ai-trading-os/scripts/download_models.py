#!/usr/bin/env python3
"""
下载 AI Trading OS 默认使用的开源权重到 ai-trading-os/models/（不入库）。
用法：
  python scripts/download_models.py              # 文本：Qwen2.5 0.5B + 1.5B
  python scripts/download_models.py --with-vision   # 额外：Qwen2.5-VL 3B（体积大）
  python scripts/download_models.py --with-phi      # 额外：Phi-3-mini（体积大）
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

# 大文件走 Hub 加速传输（需 hf_transfer）
os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "1")

from huggingface_hub import snapshot_download


ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / "models"

DEFAULT_MODELS: list[tuple[str, str]] = [
    ("Qwen/Qwen2.5-0.5B-Instruct", "text / 极速占用小"),
    ("Qwen/Qwen2.5-1.5B-Instruct", "text / 盯盘解释推荐"),
]

OPTIONAL_VISION = ("Qwen/Qwen2.5-VL-3B-Instruct", "vision / K 线截图或 OCR 辅助")
OPTIONAL_PHI = ("microsoft/Phi-3-mini-4k-instruct", "text / 备选轻量堆栈")


def download(repo_id: str, note: str, dest_name: str | None = None) -> Path:
    local = MODELS_DIR / (dest_name or repo_id.split("/")[-1])
    local.mkdir(parents=True, exist_ok=True)
    print(f"\n→ {repo_id}  ({note})")
    print(f"  目标目录: {local}")
    snapshot_download(repo_id=repo_id, local_dir=str(local))
    return local


def main() -> None:
    parser = argparse.ArgumentParser(description="下载 Hugging Face 开源模型到本地")
    parser.add_argument(
        "--with-vision",
        action="store_true",
        help="额外下载 Qwen2.5-VL-3B（多模态，体积较大）",
    )
    parser.add_argument(
        "--with-phi",
        action="store_true",
        help="额外下载 Microsoft Phi-3-mini-4k-instruct（体积较大）",
    )
    args = parser.parse_args()

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"模型根目录: {MODELS_DIR}")

    for repo_id, note in DEFAULT_MODELS:
        download(repo_id, note)

    if args.with_vision:
        download(OPTIONAL_VISION[0], OPTIONAL_VISION[1])

    if args.with_phi:
        download(OPTIONAL_PHI[0], OPTIONAL_PHI[1])

    print("\n完成。路径见 ai-trading-os/models/ 下各子目录。")


if __name__ == "__main__":
    main()
