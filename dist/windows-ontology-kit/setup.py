# -*- coding: utf-8 -*-
"""Windows 一键部署：银行业务本体 + MCP server。

做的事情（全部只用 Python 标准库）：
  1. 把 ontology-mcp/ 三个文件部署到 %USERPROFILE%\\.workbuddy\\ontology-mcp
     （脚本内部用 expanduser("~/.workbuddy/ontology-mcp") 定位真源，此路径必须与 Mac 侧一致）
  2. 创建独立虚拟环境 %USERPROFILE%\\.workbuddy\\ontology-venv
  3. 安装唯一第三方依赖 owlready2==0.51（清华源）
  4. 合并写入 %USERPROFILE%\\.workbuddy\\mcp.json（保留已有的其他 server）
  5. 冒烟测试：与 server.py 做一次 MCP 握手

用法：
    install.bat          双击即可
    py -3 setup.py       或命令行执行
"""

import json
import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HOME = Path.home()
WORK = HOME / ".workbuddy"
CORE_SRC = ROOT / "ontology-mcp"
CORE_DST = WORK / "ontology-mcp"
VENV = WORK / "ontology-venv"
PY = VENV / "Scripts" / "python.exe"
MCP = WORK / "mcp.json"
CORE_FILES = ["server.py", "ontology_core.py", "bank_seed.py"]


def step(n, msg):
    print("\n[%d/5] %s" % (n, msg))


def main():
    if sys.platform != "win32":
        print("提示：本脚本面向 Windows；当前平台为 %s" % sys.platform)

    missing = [f for f in CORE_FILES if not (CORE_SRC / f).exists()]
    if missing:
        raise SystemExit("包内缺少文件: %s" % ", ".join(missing))

    step(1, "部署真源脚本 -> %s" % CORE_DST)
    CORE_DST.mkdir(parents=True, exist_ok=True)
    for f in CORE_FILES:
        shutil.copy2(CORE_SRC / f, CORE_DST / f)
        print("  已写入 %s" % f)

    step(2, "创建虚拟环境 %s" % VENV)
    if PY.exists():
        print("  已存在，跳过")
    else:
        venv.create(str(VENV), with_pip=True)
        print("  已创建")

    step(3, "安装 owlready2==0.51")
    subprocess.check_call([
        str(PY), "-m", "pip", "install", "-q",
        "owlready2==0.51",
        "-i", "https://pypi.tuna.tsinghua.edu.cn/simple",
    ])
    print("  安装完成")

    step(4, "写入 MCP 配置 %s" % MCP)
    cfg = {"mcpServers": {}}
    if MCP.exists():
        try:
            cfg = json.loads(MCP.read_text(encoding="utf-8"))
        except Exception:
            print("  已有配置无法解析，将备份为 mcp.json.bak")
            shutil.copy2(MCP, MCP.with_suffix(".json.bak"))
    cfg.setdefault("mcpServers", {})
    existed = "ontology" in cfg["mcpServers"]
    cfg["mcpServers"]["ontology"] = {
        "command": str(PY),
        "args": [str(CORE_DST / "server.py")],
        "env": {"PYTHONIOENCODING": "utf-8"},
    }
    MCP.parent.mkdir(parents=True, exist_ok=True)
    MCP.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    print("  %s ontology（%s）" % ("更新" if existed else "新增", PY))

    step(5, "MCP 握手冒烟测试")
    init = {
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                   "clientInfo": {"name": "setup-check", "version": "1.0"}},
    }
    proc = subprocess.Popen(
        [str(PY), str(CORE_DST / "server.py")],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, encoding="utf-8",
    )
    try:
        out, _ = proc.communicate(json.dumps(init) + "\n", timeout=30)
    except subprocess.TimeoutExpired:
        proc.kill()
        print("  握手超时，请检查 %s 是否可运行" % PY)
        return
    if '"result"' in out:
        print("  握手成功，server 可用")
    else:
        print("  握手返回异常：%s" % out[:200])

    print("\n" + "=" * 60)
    print("部署完成。接下来：")
    print("  1) 完全退出 WorkBuddy 再重开（配置在启动时读取）")
    print("  2) 连接器页面找到 ontology -> 点信任 -> 开一个新会话")
    print("  3) 装 Protégé 5.6.9 Windows 版，打开 ontology\\bank-enterprise.owl")
    print("  4) 若 java 不在 PATH，设置 PROTEGE_JRE 指向 Protégé 的 jre\\bin")
    print("=" * 60)


if __name__ == "__main__":
    main()
