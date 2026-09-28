"""构建银行业务本体骨架（命令行入口）。

种子定义位于 ~/.workbuddy/ontology-mcp/bank_seed.py（与 MCP server 共用同一份真源），
本脚本只负责指定输出路径与打印结果。

用法：
    /Users/zhongyuanpan/.workbuddy/binaries/python/envs/default/bin/python build_bank_ontology.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CORE_DIR = os.path.expanduser("~/.workbuddy/ontology-mcp")
sys.path.insert(0, CORE_DIR)

from bank_seed import build  # noqa: E402
from ontology_core import stats, validate  # noqa: E402

OUT = os.path.join(HERE, "bank-enterprise.owl")


def main() -> None:
    path = build(OUT)

    sys.path.insert(0, CORE_DIR)
    from ontology_core import load
    onto = load(path)

    print("已生成:", path)
    print("大小: %.1f KB" % (os.path.getsize(path) / 1024))
    print("统计:", stats(onto))
    result = validate(onto)
    print("校验:", "通过" if result["ok"] else result["issues"])


if __name__ == "__main__":
    main()
