"""导出职责分离（四权分离）互斥矩阵，供 RBAC 授权服务加载做赋权拦截。

为什么需要这一步
----------------
本体里的 SWRL 规则只能「事后标记」违规，无法阻止赋权。
要做实时拦截，授权服务需要在赋权瞬间查一次角色互斥关系。
本脚本把本体中的互斥知识导出为 JSON 与 CSV，让授权服务直接加载，
不必依赖推理机，也不必理解 OWL。

产物
----
  separation_matrix.json  结构化矩阵，含 exclusions_by_role 便于 O(1) 查询
  separation_matrix.csv   两列互斥对，便于人工审阅与导入其它系统

自检
----
脚本会检查互斥对是否达到 C(n,2) 的完备数量，缺失会给出警告。
（曾出现过只声明 3 对、漏掉「业务操作权×审计权」的情况。）

用法
----
    python export_separation_matrix.py [本体路径] [输出目录]
"""

from __future__ import annotations

import csv
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.expanduser("~/.workbuddy/ontology-mcp"))

from ontology_core import load  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ONTOLOGY = os.path.join(HERE, "bank-enterprise.owl")

# 非角色型的职责分离规则：同一主体不得同时承担的两个岗位行为
SEPARATION_RULES = [
    {
        "name": "报送编制复核分离",
        "left_property": "compilesReport",
        "right_property": "reviewsReport",
        "description": "同一员工不得对同一报送批次既编制又复核。",
    },
]


def _label(x) -> str:
    lab = getattr(x, "label", None)
    return lab[0] if lab else ""


def _category(role) -> tuple[str, str]:
    """返回角色所属的四权分类（类名与中文标签）。"""
    for c in getattr(role, "is_a", []):
        name = getattr(c, "name", None)
        if name and name != "Role":
            return name, _label(c) or name
    return "", ""


def build_matrix(onto) -> dict:
    roles = sorted(onto.Role.instances(), key=lambda r: r.name)

    role_items = []
    for r in roles:
        cat, cat_label = _category(r)
        role_items.append({
            "id": r.name,
            "label": _label(r) or r.name,
            "category": cat,
            "category_label": cat_label,
        })

    pairs = set()
    for r in roles:
        for t in getattr(r, "separatedFrom", []):
            if t is r:
                continue
            pairs.add(frozenset([r.name, t.name]))

    sorted_pairs = sorted([sorted(p) for p in pairs])
    exclusions_by_role: dict[str, list[str]] = {r.name: [] for r in roles}
    for a, b in sorted_pairs:
        exclusions_by_role[a].append(b)
        exclusions_by_role[b].append(a)

    label_of = {r.name: (_label(r) or r.name) for r in roles}

    category_exclusions = []
    for d in onto.disjoints():
        names = [getattr(e, "name", str(e)) for e in d.entities]
        if "SystemAdministrationRole" in names:
            category_exclusions.append(names)

    expected = len(roles) * (len(roles) - 1) // 2

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_ontology": onto.base_iri.rstrip("#"),
        "description": "四权分离角色互斥矩阵。授权服务在赋权前应检查："
                       "待赋角色与已持有角色是否出现在同一互斥对中，命中则拒绝。",
        "roles": role_items,
        "exclusion_pairs": [
            {"a": a, "a_label": label_of.get(a, a),
             "b": b, "b_label": label_of.get(b, b)}
            for a, b in sorted_pairs
        ],
        "exclusions_by_role": exclusions_by_role,
        "category_exclusions": category_exclusions,
        "separation_rules": SEPARATION_RULES,
        "completeness": {
            "role_count": len(roles),
            "pair_count": len(sorted_pairs),
            "expected_pairs": expected,
            "complete": len(sorted_pairs) == expected,
        },
    }


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ONTOLOGY
    outdir = sys.argv[2] if len(sys.argv) > 2 else HERE
    os.makedirs(outdir, exist_ok=True)

    onto = load(path)
    matrix = build_matrix(onto)

    json_path = os.path.join(outdir, "separation_matrix.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(matrix, f, ensure_ascii=False, indent=2)

    csv_path = os.path.join(outdir, "separation_matrix.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["role_a", "role_a_label", "role_b", "role_b_label"])
        for p in matrix["exclusion_pairs"]:
            w.writerow([p["a"], p["a_label"], p["b"], p["b_label"]])

    comp = matrix["completeness"]
    print(f"本体     : {path}")
    print(f"角色数   : {comp['role_count']}")
    print(f"互斥对数 : {comp['pair_count']} / 期望 {comp['expected_pairs']}")
    print()
    for p in matrix["exclusion_pairs"]:
        print(f"  {p['a_label']:<8} × {p['b_label']}")
    print()
    print(f"已写出   : {json_path}")
    print(f"已写出   : {csv_path}")

    if not comp["complete"]:
        print()
        print(f"!! 警告：互斥对不完备（{comp['pair_count']}/{comp['expected_pairs']}），"
              "部分角色组合的违规将无法被检出。")
        return 1

    print()
    print("完整性自检：完备")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
