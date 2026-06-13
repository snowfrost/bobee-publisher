# RunningHub API 配置

## 设置 API Key

```bash
export RUNNINGHUB_API_KEY="你的32位API Key"
```

或通过命令行传入：
```bash
python scripts/generate.py "prompt" --api-key "your-key"
```

## 可用模型

| 模型 | 说明 | 端点 | 耗时 |
|------|------|------|:---:|
| `z-image-turbo` | 最便宜（默认） | rhart-image/z-image/turbo | ~15-40s |
| `gpt-image2` | 质量最高 | rhart-image-g-2/text-to-image | ~60-150s |
| `qwen-text` | 文字渲染强 | alibaba/qwen-image-2.0-pro/text-to-image | ~10-30s |
| `rhart-i2i` | 图生图（需参考图） | rhart-image-n-g31-flash/image-to-image | ~15-60s |

## 使用示例

```bash
# 默认生成
python scripts/generate.py "BoBee bee worker..." -o output.png

# 高质量
python scripts/generate.py "prompt" --model gpt-image2 --res 2k

# 图生图（传入本地参考图）
python scripts/generate.py "prompt" --model gpt-image2 --ratio 16:9 --image-file reference.png

# 竖版
python scripts/generate.py "prompt" --ratio 9:16
```
