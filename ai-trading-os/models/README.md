# 本地模型目录（权重不入 Git）

预置脚本会把 Hugging Face 上的开源权重下载到本目录下的子文件夹（体积从约 1GB 到数 GB 不等）。

## 下载命令

在仓库根目录执行：

```bash
python3 -m venv ai-trading-os/.venv
source ai-trading-os/.venv/bin/activate   # Windows: ai-trading-os\.venv\Scripts\activate
pip install -r ai-trading-os/requirements-models.txt
python ai-trading-os/scripts/download_models.py
```

可选：

```bash
python ai-trading-os/scripts/download_models.py --with-vision
python ai-trading-os/scripts/download_models.py --with-phi
```

## 默认拉取的模型

| 子目录 | 说明 |
|--------|------|
| `Qwen2.5-0.5B-Instruct` | 极轻量中文指令模型，适合分类/短摘要 |
| `Qwen2.5-1.5B-Instruct` | **盯盘 + 白话解释** 推荐起步尺寸 |

环境变量 `HF_TOKEN` 仅在需要 gated 模型时设置；上述均为公开模型。

## 说明

- 本目录内容已被 `.gitignore` 忽略，请勿将权重提交进仓库。
- 语音（ChatTTS / CosyVoice）权重较大且安装方式不同，需要时再单独 `pip`/克隆仓库下载。
