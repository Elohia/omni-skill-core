import os

def scan_directory(source_dir):
    """扫描目录并推测运行时环境及入口文件"""
    try:
        files = os.listdir(source_dir)
    except FileNotFoundError:
        return {"runtime": "unknown", "entrypoint": ""}

    # 优先检测节点环境 (Node)
    if "package.json" in files:
        entry = "index.js"
        if "index.js" not in files and "app.js" in files:
            entry = "app.js"
        return {"runtime": "node", "entrypoint": entry}

    # 检测蟒蛇语言环境 (Python)
    if "requirements.txt" in files or any(f.endswith(".py") for f in files):
        entry = "main.py"
        if "main.py" not in files and "app.py" in files:
            entry = "app.py"
        elif "main.py" not in files:
            pys = [f for f in files if f.endswith(".py")]
            entry = pys[0] if pys else "main.py"
        return {"runtime": "python", "entrypoint": entry}

    # 检测二进制环境 (Binary)
    binaries = [f for f in files if f.endswith(".exe") or f.endswith(".bin") or f.endswith(".sh")]
    if binaries:
        return {"runtime": "binary", "entrypoint": binaries[0]}

    # 检测提示词环境 (Prompt)
    prompts = [f for f in files if f.endswith(".md") or f.endswith(".txt") or f.endswith(".prompt")]
    if prompts:
        return {"runtime": "prompt", "entrypoint": prompts[0]}

    return {"runtime": "unknown", "entrypoint": ""}
