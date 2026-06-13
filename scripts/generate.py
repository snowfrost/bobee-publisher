#!/usr/bin/env python3
"""
RunningHub 标准模型 API — BoBee 图像生成脚本

通过 RunningHub API 生成 BoBee 蜜蜂打工人 IP 插图。
API Key 从环境变量 RUNNINGHUB_API_KEY 读取，或通过 --api-key 传入。
"""

import json
import time
import sys
import os
import argparse
import urllib.request
import urllib.error
import base64
import mimetypes

# ============================================================
# 模型注册表 — 按价格/质量排序
# ============================================================
MODELS = {
    # 最便宜（默认）
    "z-image-turbo": {
        "endpoint": "/openapi/v2/rhart-image/z-image/turbo",
        "description": "Z-Image Turbo — 最便宜，性价比最高",
        "params": {
            "prompt": {"type": "str", "required": True},
            "aspectRatio": {"type": "str", "required": True, "default": "16:9"},
            "outputFormat": {"type": "str", "required": False, "default": "png"},
        },
        "ratios": ["1:1", "3:4", "4:3", "9:16", "16:9", "2:3", "3:2"],
    },
    # 质量最好（二选）
    "gpt-image2": {
        "endpoint": "/openapi/v2/rhart-image-g-2/text-to-image",
        "description": "GPT-IMAGE2 (全能图片V2) — 质量最高",
        "params": {
            "prompt": {"type": "str", "required": True},
            "aspectRatio": {"type": "str", "required": False, "default": "16:9"},
            "resolution": {"type": "str", "required": False, "default": "1k"},
        },
        "ratios": ["1:1", "3:2", "2:3", "5:4", "4:5", "16:9", "9:16", "21:9", "3:4", "4:3", "9:21", "1:2", "2:1", "1:3", "3:1"],
    },
    # 千问文生图
    "qwen-text": {
        "endpoint": "/openapi/v2/alibaba/qwen-image-2.0-pro/text-to-image",
        "description": "千问2.0Pro文生图 — 文字渲染强",
        "params": {
            "prompt": {"type": "str", "required": True},
            "negativePrompt": {"type": "str", "required": False},
            "size": {"type": "str", "required": False, "default": "1280*720"},
            "imageNum": {"type": "str", "required": False, "default": "1"},
            "promptExtend": {"type": "bool", "required": False, "default": True},
        },
        "size_map": {
            "16:9": "1280*720", "9:16": "720*1280", "1:1": "1024*1024",
            "4:3": "1280*960", "3:4": "960*1280", "3:2": "1152*768",
            "2:3": "768*1152", "21:9": "1344*576",
        },
    },
    # 图生图
    "rhart-i2i": {
        "endpoint": "/openapi/v2/rhart-image-n-g31-flash/image-to-image",
        "description": "rhart图生图 — 需传入参考图",
        "params": {
            "imageUrls": {"type": "list", "required": True},
            "prompt": {"type": "str", "required": True},
            "aspectRatio": {"type": "str", "required": False, "default": "16:9"},
            "resolution": {"type": "str", "required": True, "default": "1k"},
        },
    },
}

# ============================================================
# 配置区
# ============================================================
CONFIG = {
    "api_key": os.environ.get("RUNNINGHUB_API_KEY", ""),
    "base_url": "https://www.runninghub.cn",
    "model": "z-image-turbo",
    "ratio": "16:9",
    "poll_interval": 3,
    "max_wait": 300,
    "output_dir": None,
}


def api_request(url, data=None, method="POST"):
    """发送 API 请求（Bearer 认证）"""
    headers = {
        "Authorization": f"Bearer {CONFIG['api_key']}",
        "Content-Type": "application/json",
    }
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        raise RuntimeError(f"HTTP {e.code}: {error_body[:300]}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"URL Error: {e.reason}")


def submit_task(prompt, **kwargs):
    """提交生成任务"""
    model_config = MODELS[CONFIG["model"]]
    url = f"{CONFIG['base_url']}{model_config['endpoint']}"

    payload = {}
    for pname, pinfo in model_config["params"].items():
        if pname == "prompt":
            payload[pname] = prompt
        elif pname == "imageUrls":
            payload[pname] = kwargs.get("image_urls") or []
        elif pname == "negativePrompt":
            val = kwargs.get("negative_prompt")
            if val:
                payload[pname] = val
        elif pname == "size":
            payload[pname] = kwargs.get("size") or pinfo.get("default", "1280*720")
        elif pname == "imageNum":
            payload[pname] = str(kwargs.get("image_num", 1))
        elif pname == "promptExtend":
            payload[pname] = kwargs.get("prompt_extend", True)
        elif pname == "aspectRatio":
            payload[pname] = kwargs.get("aspect_ratio") or CONFIG["ratio"]
        elif pname == "resolution":
            payload[pname] = kwargs.get("resolution") or pinfo.get("default", "1k")
        elif pname == "outputFormat":
            payload[pname] = kwargs.get("output_format") or pinfo.get("default", "png")
        elif pinfo.get("required") and pinfo.get("default") is not None:
            payload[pname] = pinfo["default"]

    print(f"[INFO] Model: {CONFIG['model']}")
    print(f"[INFO] Endpoint: {model_config['endpoint']}")
    print(f"[INFO] Payload keys: {list(payload.keys())}")
    print(f"[DEBUG] Prompt: {prompt[:150]}...")

    result = api_request(url, payload)

    task_id = result.get("taskId")
    if not task_id:
        raise RuntimeError(f"Submission failed: {json.dumps(result)[:300]}")

    status = result.get("status", "UNKNOWN")
    print(f"[INFO] Task submitted: taskId={task_id}, status={status}")
    return task_id


def poll_task(task_id):
    """轮询任务状态"""
    url = f"{CONFIG['base_url']}/openapi/v2/query"
    start_time = time.time()

    while True:
        elapsed = time.time() - start_time
        if elapsed > CONFIG["max_wait"]:
            raise TimeoutError(f"Task {task_id} timed out after {CONFIG['max_wait']}s")

        result = api_request(url, {"taskId": task_id})
        status = result.get("status", "UNKNOWN")

        if status == "SUCCESS":
            print(f"\n[INFO] Task completed in {elapsed:.0f}s")
            return result
        elif status == "FAILED":
            raise RuntimeError(f"Task failed: [{result.get('errorCode','')}] {result.get('errorMessage','')}")
        elif status in ("QUEUED", "RUNNING"):
            sys.stdout.write(f"\r[INFO] Status: {status} ({elapsed:.0f}s)")
            sys.stdout.flush()
            time.sleep(CONFIG["poll_interval"])
        else:
            raise RuntimeError(f"Unknown status '{status}'")


def download_image(url, output_path):
    """下载图像"""
    print(f"[INFO] Downloading...")
    urllib.request.urlretrieve(url, output_path)
    print(f"[INFO] Saved to: {output_path}")


def upload_local_image(filepath):
    """上传本地图片到 RunningHub，返回可访问的 URL"""
    url = f"{CONFIG['base_url']}/openapi/v2/media/upload/binary"
    boundary = "----WebKitFormBoundary" + os.urandom(16).hex()

    filename = os.path.basename(filepath)
    mime_type = mimetypes.guess_type(filepath)[0] or "image/png"

    with open(filepath, "rb") as f:
        file_data = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {mime_type}\r\n\r\n"
    ).encode("utf-8") + file_data + f"\r\n--{boundary}--\r\n".encode("utf-8")

    headers = {
        "Authorization": f"Bearer {CONFIG['api_key']}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    print(f"[INFO] Uploading {filename} ({len(file_data)} bytes)...")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else ""
        raise RuntimeError(f"Upload failed HTTP {e.code}: {error_body[:300]}")

    if result.get("code") != 0:
        raise RuntimeError(f"Upload failed: {result}")

    download_url = result["data"].get("download_url")
    if not download_url:
        # 构建完整 URL
        filename = result["data"].get("fileName", "")
        download_url = f"https://www.runninghub.cn/view?filename={filename}&type=input"

    print(f"[INFO] Uploaded: {download_url}")
    return download_url


def generate(prompt, output_path=None, **kwargs):
    """主函数"""
    task_id = submit_task(prompt, **kwargs)
    result = poll_task(task_id)

    results = result.get("results")
    if not results:
        raise RuntimeError(f"No results: {json.dumps(result)[:300]}")

    first = results[0]
    image_url = first.get("url")
    if not image_url:
        raise RuntimeError(f"No URL: {json.dumps(first)[:200]}")

    if output_path is None:
        output_dir = CONFIG["output_dir"] or os.getcwd()
        os.makedirs(output_dir, exist_ok=True)
        ext = first.get("outputType", "png")
        filename = f"rh_{task_id}.{ext}"
        output_path = os.path.join(output_dir, filename)

    download_image(image_url, output_path)
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="RunningHub 图像生成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
模型:
  z-image-turbo  最便宜（默认）
  gpt-image2     质量最高（二选）
  qwen-text      千问文生图（文字渲染强）
  rhart-i2i      图生图（需 --image）

示例:
  python generate.py "a cute bee in an office"              # 默认 z-image-turbo, 16:9
  python generate.py "a bee" --ratio 9:16                    # 竖版
  python generate.py "a bee" --model gpt-image2 --res 2k     # 高质量
  python generate.py "..." --model rhart-i2i --image URL     # 图生图
  python generate.py --show                                  # 显示配置
        """
    )
    parser.add_argument("prompt", nargs="?", help="提示词")
    parser.add_argument("--output", "-o", help="输出路径")
    parser.add_argument("--model", choices=list(MODELS.keys()), default=CONFIG["model"], help="模型")
    parser.add_argument("--ratio", default=CONFIG["ratio"], help="比例 (16:9, 9:16, 1:1...)")
    parser.add_argument("--res", default="1k", choices=["1k", "2k", "4k"], help="分辨率")
    parser.add_argument("--format", default="png", choices=["png", "jpeg", "webp(lossless)", "webp(lossy)"], help="输出格式")
    parser.add_argument("--size", help="千问模型的尺寸 (如 1280*720)")
    parser.add_argument("--num", type=int, default=1, help="千问模型的生成张数")
    parser.add_argument("--negative", help="千问模型的负向提示词")
    parser.add_argument("--no-extend", action="store_true", help="关闭千问prompt智能改写")
    parser.add_argument("--image", action="append", help="图生图输入图片URL")
    parser.add_argument("--image-file", help="本地图片路径（自动上传到 RunningHub 作为参考图）")
    parser.add_argument("--api-key", help="覆盖API Key")
    parser.add_argument("--show", action="store_true", help="显示配置")

    args = parser.parse_args()

    if args.show:
        mc = MODELS[CONFIG["model"]]
        print(f"Model: {CONFIG['model']} ({mc['description']})")
        print(f"Endpoint: {mc['endpoint']}")
        print(f"Ratio: {CONFIG['ratio']}")
        return

    if not args.prompt:
        parser.print_help()
        sys.exit(1)

    if args.api_key:
        CONFIG["api_key"] = args.api_key

    CONFIG["model"] = args.model
    if args.ratio != CONFIG["ratio"]:
        CONFIG["ratio"] = args.ratio

    try:
        # 处理本地图片上传
        image_urls = list(args.image) if args.image else []
        if args.image_file:
            uploaded_url = upload_local_image(args.image_file)
            image_urls.append(uploaded_url)

        # 如果有参考图且模型是文生图，自动切换到图生图
        if image_urls and CONFIG["model"] not in ("rhart-i2i",):
            print(f"[INFO] Reference image provided, switching to rhart-i2i for image-to-image generation")
            CONFIG["model"] = "rhart-i2i"

        output = generate(
            prompt=args.prompt,
            output_path=args.output,
            aspect_ratio=args.ratio,
            resolution=args.res,
            output_format=args.format,
            size=args.size,
            image_num=args.num,
            negative_prompt=args.negative,
            prompt_extend=not args.no_extend,
            image_urls=image_urls,
        )
        print(f"\n[DONE] {output}")
        print(f"__RESULT__:{json.dumps({'path': output, 'status': 'success'})}")
    except Exception as e:
        print(f"\n[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
