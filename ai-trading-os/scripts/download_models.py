#!/usr/bin/env python3
"""
下载 AI Trading OS 使用的开源权重到 ai-trading-os/models/（不入库）。

示例：
  python scripts/download_models.py
      # 仅 Qwen2.5 0.5B + 1.5B（最小集合）

  python scripts/download_models.py --recommended
      # 基座 + DeepSeek-R1 蒸馏 + ChatTTS + CosyVoice-300M（盯盘/播报推荐）

  python scripts/download_models.py --recommended --with-sensenova
      # 在上面的基础上增加 SenseNova-U1-8B（体积很大）

  python scripts/download_models.py --with-vision
      # 额外：Qwen2.5-VL-3B

  python scripts/download_models.py --with-phi
      # 额外：Phi-3-mini
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "1")

from huggingface_hub import snapshot_download


ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / "models"

# 文本基座（默认）
DEFAULT_MODELS: list[tuple[str, str]] = [
    ("Qwen/Qwen2.5-0.5B-Instruct", "text / 极速占用小"),
    ("Qwen/Qwen2.5-1.5B-Instruct", "text / 盯盘解释推荐"),
]

# 规格里强调的：推理 + 语音（体积相对可控）
RECOMMENDED_EXTRA: list[tuple[str, str]] = [
    ("deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B", "text / DeepSeek-R1 蒸馏推理链"),
    ("2Noise/ChatTTS", "tts / ChatTTS"),
    ("FunAudioLLM/CosyVoice-300M", "tts / CosyVoice 轻量基座"),
]

# 视觉重点（体积大，默认不拉）
SENSENOVA_U1: tuple[str, str] = (
    "sensenova/SenseNova-U1-8B-MoT",
    "vision / SenseNova-U1 多模态（大）",
)

OPTIONAL_VISION = ("Qwen/Qwen2.5-VL-3B-Instruct", "vision / K 线截图或 OCR 辅助（Qwen-VL）")
OPTIONAL_PHI = ("microsoft/Phi-3-mini-4k-instruct", "text / Phi-3 备选")


def download(repo_id: str, note: str, dest_name: str | None = None) -> Path:
    local = MODELS_DIR / (dest_name or repo_id.split("/")[-1])
    local.mkdir(parents=True, exist_ok=True)
    print(f"\n→ {repo_id}  ({note})")
    print(f"  目标目录: {local}")
    snapshot_download(repo_id=repo_id, local_dir=str(local))
    return local


def main() -> None:
    parser = argparse.ArgumentParser(
        description="下载 Hugging Face 开源模型到 ai-trading-os/models/",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="完整 R1 体量极大，本地一般用 R1-Distill；SenseNova-U1 需较大磁盘与显存。",
    )
    parser.add_argument(
        "--recommended",
        action="store_true",
        help="在基座之外额外下载：DeepSeek-R1 蒸馏、ChatTTS、CosyVoice-300M",
    )
    parser.add_argument(
        "--no-base",
        action="store_true",
        help="跳过 Qwen2.5 两个基座（仅当你已下载或只要扩展包时使用）",
    )
    parser.add_argument(
        "--with-sensenova",
        action="store_true",
        help="下载 SenseNova-U1-8B-MoT（多模态重点；体积与显存占用大）",
    )
    parser.add_argument(
        "--with-vision",
        action="store_true",
        help="额外下载 Qwen2.5-VL-3B（多模态备选）",
    )
    parser.add_argument(
        "--with-phi",
        action="store_true",
        help="额外下载 Microsoft Phi-3-mini-4k-instruct",
    )
    parser.add_argument(
        "--cosyvoice2",
        action="store_true",
        help="额外下载 CosyVoice2-0.5B（比 300M 更大、质量通常更好）",
    )
    args = parser.parse_args()

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"模型根目录: {MODELS_DIR}")

    if not args.no_base:
        for repo_id, note in DEFAULT_MODELS:
            download(repo_id, note)

    if args.recommended:
        for repo_id, note in RECOMMENDED_EXTRA:
            download(repo_id, note)

    if args.with_sensenova:
        download(SENSENOVA_U1[0], SENSENOVA_U1[1])

    if args.with_vision:
        download(OPTIONAL_VISION[0], OPTIONAL_VISION[1])

    if args.with_phi:
        download(OPTIONAL_PHI[0], OPTIONAL_PHI[1])

    if args.cosyvoice2:
        download(
            "FunAudioLLM/CosyVoice2-0.5B",
            "tts / CosyVoice2 0.5B（可选升级版）",
        )

    print("\n完成。路径见 ai-trading-os/models/ 下各子目录。")


if __name__ == "__main__":
    main()
