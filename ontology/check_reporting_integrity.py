"""报送记录完整性校验。

用途
----
OWL 采用开放世界假设（OWA）：本体的限制公理
`EASTAccountItem ⊑ ∃reportsEntity.Account` 表达的是语义承诺，
但某条记录「未陈述」reportsEntity 只代表未知，不代表违反，
HermiT 不会因此判定本体不一致。

要真正查出报送数据里的缺失与错配，必须在封闭世界下逐条检查实例。
本脚本承担这一层，适合作为报送抽取后的数据质量门禁。

用法
----
    python check_reporting_integrity.py [本体路径]
缺省本体路径为同目录下的 bank-enterprise.owl。
退出码 0 表示无问题，1 表示检出问题。
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.expanduser("~/.workbuddy/ontology-mcp"))

from bank_seed import RESTRICTIONS  # noqa: E402
from ontology_core import load  # noqa: E402

DEFAULT_ONTOLOGY = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "bank-enterprise.owl")

# 从种子真源读取各主题域应指向的实体类型，避免与本体定义漂移
EXPECTED_ENTITY = {
    cls: target
    for cls, prop, kind, target, _card in RESTRICTIONS
    if prop == "reportsEntity" and kind == "some"
}

REQUIRED_DATA_PROPS = ("reportedPeriod", "snapshotTime")


def _as_list(value) -> list:
    """函数性属性返回单个值，非函数性返回列表，缺失返回 None 或 []，统一成列表。"""
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value]


def check(onto) -> list[str]:
    """返回问题清单，空列表表示全部通过。"""
    issues: list[str] = []

    for domain_cls, expected_entity in sorted(EXPECTED_ENTITY.items()):
        cls = getattr(onto, domain_cls, None)
        if cls is None:
            issues.append(f"本体中缺少主题域类 {domain_cls}")
            continue
        expected = getattr(onto, expected_entity, None)
        if expected is None:
            issues.append(f"本体中缺少业务实体类 {expected_entity}")
            continue

        for ind in cls.instances():
            name = getattr(ind, "name", str(ind))

            targets = _as_list(getattr(ind, "reportsEntity", None))
            if not targets:
                issues.append(f"[{domain_cls}] {name}：未指向源实体（reportsEntity 缺失）")
                continue
            if len(targets) > 1:
                issues.append(f"[{domain_cls}] {name}：指向了 {len(targets)} 个源实体，应为 1 个")
            for t in targets:
                if not isinstance(t, expected):
                    issues.append(
                        f"[{domain_cls}] {name}：源实体 {getattr(t, 'name', t)} "
                        f"类型不符，应为 {expected_entity}"
                    )

            for prop in REQUIRED_DATA_PROPS:
                if getattr(ind, prop, None) in (None, [], ""):
                    issues.append(f"[{domain_cls}] {name}：缺少必填字段 {prop}")

    # 同一源实体在同一报送期间不得重复报送
    seen: dict[tuple, str] = {}
    for domain_cls in EXPECTED_ENTITY:
        cls = getattr(onto, domain_cls, None)
        if cls is None:
            continue
        for ind in cls.instances():
            period = getattr(ind, "reportedPeriod", None)
            for t in _as_list(getattr(ind, "reportsEntity", None)):
                key = (domain_cls, getattr(t, "name", str(t)), period)
                if key in seen:
                    issues.append(
                        f"[{domain_cls}] {getattr(ind, 'name', ind)}：与 {seen[key]} "
                        f"在同一报送期间 {period} 重复指向源实体 {key[1]}"
                    )
                else:
                    seen[key] = getattr(ind, "name", str(ind))

    return issues


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ONTOLOGY
    onto = load(path)

    total = sum(
        len(getattr(onto, c).instances())
        for c in EXPECTED_ENTITY
        if getattr(onto, c, None) is not None
    )
    print(f"校验本体 : {path}")
    print(f"报送记录 : {total} 条")
    print(f"覆盖主题域 : {len(EXPECTED_ENTITY)} 个")
    print()

    issues = check(onto)
    if not issues:
        print("结果：全部通过")
        return 0

    print(f"结果：检出 {len(issues)} 个问题")
    for i, msg in enumerate(issues, 1):
        print(f"  {i}. {msg}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
