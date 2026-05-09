# 本地模型目录（权重不入 Git）

预置脚本会把 Hugging Face 上的开源权重下载到本目录下的子文件夹（体积从约 1GB 到数十 GB 不等）。

## 下载命令

在仓库根目录执行：

```bash
python3 -m venv ai-trading-os/.venv
source ai-trading-os/.venv/bin/activate   # Windows: ai-trading-os\.venv\Scripts\activate
pip install -r ai-trading-os/requirements-models.txt
```

**最小集合（仅 Qwen 文本基座）：**

```bash
python ai-trading-os/scripts/download_models.py
```

**推荐集合（规格里的重点：DeepSeek-R1 蒸馏 + ChatTTS + CosyVoice）：**

```bash
python ai-trading-os/scripts/download_models.py --recommended
```

**再加上 SenseNova-U1（多模态重点，磁盘与显存占用大）：**

```bash
python ai-trading-os/scripts/download_models.py --recommended --with-sensenova
```

若 Qwen 基座已下载过，可跳过重复拉取：

```bash
python ai-trading-os/scripts/download_models.py --no-base --recommended --with-sensenova
```

其它可选：

```bash
python ai-trading-os/scripts/download_models.py --with-vision   # Qwen2.5-VL-3B
python ai-trading-os/scripts/download_models.py --with-phi       # Phi-3-mini
python ai-trading-os/scripts/download_models.py --cosyvoice2    # CosyVoice2-0.5B 额外一份
```

## 仓库 ID 与用途对照

| Hugging Face 仓库 | 本地子目录名（默认） | 用途 |
|-------------------|----------------------|------|
| `Qwen/Qwen2.5-0.5B-Instruct` | `Qwen2.5-0.5B-Instruct` | 极轻量指令 / 分类 |
| `Qwen/Qwen2.5-1.5B-Instruct` | `Qwen2.5-1.5B-Instruct` | 盯盘白话解释（基座） |
| `deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B` | `DeepSeek-R1-Distill-Qwen-1.5B` | **DeepSeek-R1 蒸馏**，链式推理（完整 R1 体量过大，一般用蒸馏版） |
| `sensenova/SenseNova-U1-8B-MoT` | `SenseNova-U1-8B-MoT` | **SenseNova-U1**，图表/多模态理解（大） |
| `2Noise/ChatTTS` | `ChatTTS` | **ChatTTS** 语音合成 |
| `FunAudioLLM/CosyVoice-300M` | `CosyVoice-300M` | **CosyVoice** 轻量 TTS 基座 |
| `FunAudioLLM/CosyVoice2-0.5B` | `CosyVoice2-0.5B` | CosyVoice2（可选 `--cosyvoice2`） |
| `Qwen/Qwen2.5-VL-3B-Instruct` | `Qwen2.5-VL-3B-Instruct` | Qwen 系多模态备选（`--with-vision`） |

推理代码（加载方式）以各官方仓库说明为准：`ChatTTS`、`CosyVoice` 也可再配合各自 GitHub 仓库做服务端封装。

## 鉴权

公开模型一般无需登录；若提示限速，可在环境里设置 `HF_TOKEN`。部分账号专属或 gated 模型需在 Hugging Face 网页同意条款后再拉取。

## 说明

- 本目录内容已被 `.gitignore` 忽略，请勿将权重提交进仓库。
- **完整版 DeepSeek-R1**（非 Distill）体积与算力需求远高于蒸馏版，不建议作为本地默认下载目标；需要时用官方文档与 Hub 说明单独处理。
